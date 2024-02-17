"""
torch.distributed utils
"""

from __future__ import annotations
from typing import Optional, Any, Dict
import os
import socket
import logging

import torch
from torch.nn.parallel import DistributedDataParallel

from returnn.config import Config

_logger = logging.getLogger("returnn.torch.distributed")


class DistributedContext:
    """
    This class setups some helper functions for torch distributed training
    """

    def __init__(self, options: Dict[str, Any]):
        import torch.distributed as dist

        self._opts = options

        # when no backend is specified, both gloo and nccl backends will be created
        # the gloo backend will be used for collectives with CPU tensors and
        # the nccl backend will be used for collectives with CUDA tensors
        dist.init_process_group(backend=self._opts.get("backend", None))

        self._local_rank = int(os.environ["LOCAL_RANK"])
        self._local_size = int(os.environ["LOCAL_WORLD_SIZE"])
        self._rank = dist.get_rank()
        self._size = dist.get_world_size()

        _logger.info(
            "Torch distributed initialized. Hostname %s, pid %i, rank %i / size %i, local rank %s / local size %s."
            % (socket.gethostname(), os.getpid(), self._rank, self._size, self._local_rank, self._local_size)
        )

        self._reduce_type = self._opts.get("reduce_type", "grad")
        self._param_sync_step: Optional[int] = self._opts.get("param_sync_step", None)
        if self._reduce_type == "param":
            assert isinstance(self._param_sync_step, int) and self._param_sync_step > 0, (
                f"reduce_type param: param_sync_step must be a positive int,"
                f" got {self._param_sync_step!r} ({type(self._param_sync_step).__name__})"
            )
            _logger.info(f"reduce_type param: param_sync_step {self._param_sync_step}")
        elif self._reduce_type == "grad":
            _logger.info("reduce_type grad")
        else:
            raise ValueError(f"invalid reduce_type {self._reduce_type!r}")

    def local_rank(self) -> int:
        """local rank"""
        return self._local_rank

    def local_size(self) -> int:
        """local size"""
        return self._local_size

    def rank(self) -> int:
        """global rank"""
        return self._rank

    def size(self) -> int:
        """global size"""
        return self._size

    def get_param_sync_step(self) -> Optional[int]:
        """param sync step"""
        return self._param_sync_step

    def maybe_make_distributed_module(self, module: torch.nn.Module) -> Optional[DistributedDataParallel]:
        """
        Maybe make a wrapped distributed module.

        :param module: original module
        :return: potentially wrapped module
        """
        if self._reduce_type == "param":
            return None
        cls = self._opts.get("class", DistributedDataParallel)
        if cls is not DistributedDataParallel:
            _logger.warning(f"Using custom class {cls} instead of DistributedDataParallel, might be unsupported.")
        kwargs = self._opts.get("options", {})
        return cls(
            module=module,
            device_ids=[self.local_rank()],
            **kwargs,
        )

    def step_after_param_update(self, *, module: torch.nn.Module, epoch_step_idx: int):
        """one train step"""
        if self._reduce_type == "param" and ((epoch_step_idx % self._param_sync_step) == (self._param_sync_step - 1)):
            _sync_params_avg(module=module, sync_on_cpu=self._opts.get("sync_on_cpu", False))


_is_set_up = False
_ctx = None  # type: Optional[DistributedContext]


def get_ctx(config=None) -> Optional[DistributedContext]:
    """
    :param Config|None config:
    :returns: the global context if Torch distributed is enabled, or None otherwise.
      If we did not setup the context yet, it will automatically create it.
    """
    global _is_set_up, _ctx
    if _is_set_up:
        return _ctx
    if not config:
        from returnn.config import get_global_config

        config = get_global_config(raise_exception=False)
        if not config:
            return None

    _is_set_up = True
    opts = config.typed_value("torch_distributed")
    if opts is None:
        return None

    assert isinstance(opts, dict)
    _ctx = DistributedContext(opts)
    return _ctx


@torch.no_grad()
def _sync_params_avg(*, module: torch.nn.Module, sync_on_cpu: bool = False):
    import torch.distributed as dist

    if sync_on_cpu:
        for param in module.parameters():
            # Separately move each param to CPU (instead of the whole module), to safe CPU memory.
            param_cpu = param.to(torch.device("cpu"))
            # On CPU, we are likely using Gloo, and Gloo does not support AVG
            dist.all_reduce(param_cpu.data, op=dist.ReduceOp.SUM)
            param_cpu.data /= dist.get_world_size()
            param.data = param_cpu.to(param.device)
        return

    if dist.get_backend() == "gloo":
        # Gloo does not support AVG
        reduce_op = dist.ReduceOp.SUM
    else:
        if hasattr(dist.ReduceOp, "AVG"):
            reduce_op = dist.ReduceOp.AVG
        else:
            # Older PyTorch versions do not have ReduceOp.AVG.
            reduce_op = dist.ReduceOp.SUM

    for param in module.parameters():
        dist.all_reduce(param.data, op=reduce_op)
        if reduce_op == dist.ReduceOp.SUM:
            param.data /= dist.get_world_size()
