"""Utility functions for Hugging Face models."""
from __future__ import annotations

from collections import OrderedDict
from contextlib import AbstractContextManager, suppress
from dataclasses import dataclass, field
import logging
import os
import time
from typing import Any, Dict, List, Literal, Optional, Tuple

from timm import utils
from timm.data import Mixup
from timm.models import model_parameters
from timm.utils import ApexScaler
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.utils

from bitfount.transformations.base_transformation import Transformation
from bitfount.transformations.parser import TransformationsParser
from bitfount.types import _JSONDict

_logger = logging.getLogger(__name__)


@dataclass
class TIMMTrainingConfig:
    """Configuration for training a TIMM model."""

    pretrained: bool = False
    initial_checkpoint: str = ""
    num_classes: Optional[int] = None
    gp: Optional[str] = None
    img_size: Optional[int] = None
    in_chans: Optional[int] = None
    input_size: Optional[Tuple[int, int, int]] = None
    crop_pct: Optional[float] = None
    mean: Optional[List[float]] = None
    std: Optional[List[float]] = None
    interpolation: str = ""
    batch_size: int = 128
    validation_batch_size: Optional[int] = None
    channels_last: bool = False
    fuser: str = ""
    grad_accum_steps: int = 1
    grad_checkpointing: bool = False
    fast_norm: bool = False
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    head_init_scale: Optional[float] = None
    head_init_bias: Optional[float] = None
    torchscript: bool = False
    torchcompile: Optional[str] = None
    opt: str = "sgd"
    opt_eps: Optional[float] = None
    opt_betas: Optional[List[float]] = None
    momentum: float = 0.9
    weight_decay: float = 2e-5
    clip_grad: Optional[float] = None
    clip_mode: str = "norm"
    layer_decay: Optional[float] = None
    opt_kwargs: Dict[str, Any] = field(default_factory=dict)
    sched: str = "cosine"
    sched_on_updates: bool = False
    lr: Optional[float] = None
    lr_base: float = 0.1
    lr_base_size: int = 256
    lr_base_scale: str = ""
    lr_noise: Optional[List[float]] = None
    lr_noise_pct: float = 0.67
    lr_noise_std: float = 1.0
    lr_cycle_mul: float = 1.0
    lr_cycle_decay: float = 0.5
    lr_cycle_limit: int = 1
    lr_k_decay: float = 1.0
    warmup_lr: float = 1e-5
    min_lr: float = 0
    epochs: int = 300
    epoch_repeats: float = 0.0
    start_epoch: Optional[int] = None
    decay_milestones: List[int] = field(default_factory=lambda: [90, 180, 270])
    decay_epochs: float = 90
    warmup_epochs: int = 5
    warmup_prefix: bool = False
    cooldown_epochs: int = 0
    patience_epochs: int = 10
    decay_rate: float = 0.1
    aug_splits: int = 0
    jsd_loss: bool = False
    bce_loss: bool = False
    bce_target_thresh: Optional[float] = None
    resplit: bool = False
    mixup: float = 0.0
    cutmix: float = 0.0
    cutmix_minmax: Optional[List[float]] = None
    mixup_prob: float = 1.0
    mixup_switch_prob: float = 0.5
    mixup_mode: str = "batch"
    mixup_off_epoch: int = 0
    smoothing: float = 0.1
    drop: float = 0.0
    drop_connect: Optional[float] = None
    drop_path: Optional[float] = None
    drop_block: Optional[float] = None
    bn_momentum: Optional[float] = None
    bn_eps: Optional[float] = None
    sync_bn: bool = False
    dist_bn: str = "reduce"
    split_bn: bool = False
    model_ema: bool = False
    model_ema_force_cpu: bool = False
    model_ema_decay: float = 0.9998
    seed: int = 42
    log_interval: int = 50
    recovery_interval: int = 0
    checkpoint_hist: int = 10
    workers: int = 4
    save_images: bool = False
    amp: bool = False
    amp_dtype: str = "float16"
    amp_impl: str = "native"
    no_ddp_bb: bool = False
    synchronize_step: bool = False
    no_prefetcher: bool = False
    eval_metric: str = "top1"
    tta: int = 0
    local_rank: int = 0

    def __post_init__(self) -> None:
        self.prefetcher = not self.no_prefetcher
        self.grad_accum_steps = max(1, self.grad_accum_steps)

        # Will be set later by `utils.init_distributed_device`
        self.device: str
        self.distributed: bool
        self.world_size: int
        self.rank: int
        self.local_rank: int

        # Will be set later by TIMMFineTuning Algorithm. Required for downstream
        # saving of checkpoints.
        self.model: str  # the architecture name


def validate(
    model: nn.Module,
    loader: DataLoader,
    loss_fn: nn.Module,
    args: TIMMTrainingConfig,
    device: torch.device,
    amp_autocast: AbstractContextManager = suppress,
    log_suffix: str = "",
) -> Dict[str, Any]:
    """Performs validation of the model and returns metrics.

    Borrowed with permission from https://github.com/huggingface/pytorch-image-models.
    Copyright 2020 Ross Wightman (https://github.com/rwightman)
    """
    batch_time_m = utils.AverageMeter()
    losses_m = utils.AverageMeter()
    top1_m = utils.AverageMeter()
    top5_m = utils.AverageMeter()

    model.eval()

    end = time.time()
    last_idx = len(loader) - 1
    with torch.no_grad():
        for batch_idx, (input_, target) in enumerate(loader):
            # this is a temporary fix that will be changed after using the new dataloaders
            if isinstance(input_, (tuple, list)):
                input_ = torch.stack(input_)
                input_ = torch.swapaxes(input_, 0, 1)
            input_ = input_.to(device)
            target = target.to(device)
            last_batch = batch_idx == last_idx
            if not args.prefetcher:
                input_, target = input_.to(device), target.to(device)
            if args.channels_last:
                input_ = input_.contiguous(memory_format=torch.channels_last)

            with amp_autocast():
                output = model(input_)
                if isinstance(output, (tuple, list)):
                    output = output[0]

                # augmentation reduction
                reduce_factor = args.tta
                if reduce_factor > 1:
                    output = output.unfold(0, reduce_factor, reduce_factor).mean(dim=2)
                    target = target[0 : target.size(0) : reduce_factor]

                loss = loss_fn(output, target)
            acc1, acc5 = utils.accuracy(output, target, topk=(1, 5))

            if args.distributed:
                reduced_loss = utils.reduce_tensor(loss.data, args.world_size)
                acc1 = utils.reduce_tensor(acc1, args.world_size)
                acc5 = utils.reduce_tensor(acc5, args.world_size)
            else:
                reduced_loss = loss.data

            if device.type == "cuda":
                torch.cuda.synchronize()

            losses_m.update(reduced_loss.item(), input_.size(0))
            top1_m.update(acc1.item(), output.size(0))
            top5_m.update(acc5.item(), output.size(0))

            batch_time_m.update(time.time() - end)
            end = time.time()
            if utils.is_primary(args) and (
                last_batch or batch_idx % args.log_interval == 0
            ):
                log_name = "Test" + log_suffix
                _logger.info(
                    f"{log_name}: [{batch_idx:>4d}/{last_idx}]  "
                    f"Time: {batch_time_m.val:.3f} ({batch_time_m.avg:.3f})  "
                    f"Loss: {losses_m.val:>7.3f} ({losses_m.avg:>6.3f})  "
                    f"Acc@1: {top1_m.val:>7.3f} ({top1_m.avg:>7.3f})  "
                    f"Acc@5: {top5_m.val:>7.3f} ({top5_m.avg:>7.3f})"
                )

    metrics = OrderedDict(
        [("loss", losses_m.avg), ("top1", top1_m.avg), ("top5", top5_m.avg)]
    )

    return metrics


def train_one_epoch(
    epoch: int,
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    args: TIMMTrainingConfig,
    device: torch.device,
    lr_scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
    saver: Optional[utils.CheckpointSaver] = None,
    output_dir: Optional[str] = None,
    amp_autocast: AbstractContextManager = suppress,
    loss_scaler: Optional[ApexScaler] = None,
    model_ema: Optional[utils.ModelEmaV2] = None,
    mixup_fn: Optional[Mixup] = None,
) -> Dict[str, Any]:
    """Performs one epoch of training and returns loss.

    Borrowed with permission from https://github.com/huggingface/pytorch-image-models.
    Copyright 2020 Ross Wightman (https://github.com/rwightman)
    """
    if args.mixup_off_epoch and epoch >= args.mixup_off_epoch:
        if args.prefetcher and loader.mixup_enabled:
            loader.mixup_enabled = False
        elif mixup_fn is not None:
            mixup_fn.mixup_enabled = False

    second_order = hasattr(optimizer, "is_second_order") and optimizer.is_second_order
    has_no_sync = hasattr(model, "no_sync")
    update_time_m = utils.AverageMeter()
    data_time_m = utils.AverageMeter()
    losses_m = utils.AverageMeter()

    model.train()

    accum_steps = args.grad_accum_steps
    last_accum_steps = len(loader) % accum_steps
    updates_per_epoch = (len(loader) + accum_steps - 1) // accum_steps
    num_updates = epoch * updates_per_epoch
    last_batch_idx = len(loader) - 1
    last_batch_idx_to_accum = len(loader) - last_accum_steps

    data_start_time = update_start_time = time.time()
    optimizer.zero_grad()
    update_sample_count = 0
    for batch_idx, (input_, target) in enumerate(loader):
        if isinstance(input_, (tuple, list)):
            # this is a temporary fix that will be changed after using the new dataloaders
            input_ = torch.stack(input_)
            input_ = torch.swapaxes(input_, 0, 1)
        last_batch = batch_idx == last_batch_idx
        need_update = last_batch or (batch_idx + 1) % accum_steps == 0
        update_idx = batch_idx // accum_steps
        if batch_idx >= last_batch_idx_to_accum:
            accum_steps = last_accum_steps

        input_, target = input_.to(device), target.to(device)
        if not args.prefetcher:
            input_, target = input_.to(device), target.to(device)
            if mixup_fn is not None:
                input_, target = mixup_fn(input_, target)
        if args.channels_last:
            input_ = input_.contiguous(memory_format=torch.channels_last)

        # multiply by accum steps to get equivalent for full update
        data_time_m.update(accum_steps * (time.time() - data_start_time))

        def _forward():
            with amp_autocast():
                output = model(input_)
                loss = loss_fn(output, target)
            if accum_steps > 1:
                loss /= accum_steps
            return loss

        def _backward(_loss):
            if loss_scaler is not None:
                loss_scaler(
                    _loss,
                    optimizer,
                    clip_grad=args.clip_grad,
                    clip_mode=args.clip_mode,
                    parameters=model_parameters(
                        model, exclude_head="agc" in args.clip_mode
                    ),
                    create_graph=second_order,
                    need_update=need_update,
                )
            else:
                _loss.backward(create_graph=second_order)
                if need_update:
                    if args.clip_grad is not None:
                        utils.dispatch_clip_grad(
                            model_parameters(
                                model, exclude_head="agc" in args.clip_mode
                            ),
                            value=args.clip_grad,
                            mode=args.clip_mode,
                        )
                    optimizer.step()

        if has_no_sync and not need_update:
            with model.no_sync():
                loss = _forward()
                _backward(loss)
        else:
            loss = _forward()
            _backward(loss)

        if not args.distributed:
            losses_m.update(loss.item() * accum_steps, input_.size(0))
        update_sample_count += input_.size(0)

        if not need_update:
            data_start_time = time.time()
            continue

        num_updates += 1
        optimizer.zero_grad()
        if model_ema is not None:
            model_ema.update(model)

        if args.synchronize_step and device.type == "cuda":
            torch.cuda.synchronize()
        time_now = time.time()
        update_time_m.update(time.time() - update_start_time)
        update_start_time = time_now

        if update_idx % args.log_interval == 0:
            lrl = [param_group["lr"] for param_group in optimizer.param_groups]
            lr = sum(lrl) / len(lrl)

            if args.distributed:
                reduced_loss = utils.reduce_tensor(loss.data, args.world_size)
                losses_m.update(reduced_loss.item() * accum_steps, input_.size(0))
                update_sample_count *= args.world_size

            if utils.is_primary(args):
                _logger.info(
                    f"Train: {epoch} [{update_idx:>4d}/{updates_per_epoch} "
                    f"({100. * update_idx / (updates_per_epoch - 1):>3.0f}%)]  "
                    f"Loss: {losses_m.val:#.3g} ({losses_m.avg:#.3g})  "
                    f"Time: {update_time_m.val:.3f}s, {update_sample_count / update_time_m.val:>7.2f}/s  "
                    f"({update_time_m.avg:.3f}s, {update_sample_count / update_time_m.avg:>7.2f}/s)  "
                    f"LR: {lr:.3e}  "
                    f"Data: {data_time_m.val:.3f} ({data_time_m.avg:.3f})"
                )

                if args.save_images and output_dir:
                    torchvision.utils.save_image(
                        input_,
                        os.path.join(output_dir, "train-batch-%d.jpg" % batch_idx),
                        padding=0,
                        normalize=True,
                    )

        if (
            saver is not None
            and args.recovery_interval
            and ((update_idx + 1) % args.recovery_interval == 0)
        ):
            saver.save_recovery(epoch, batch_idx=update_idx)

        if lr_scheduler is not None:
            lr_scheduler.step_update(num_updates=num_updates, metric=losses_m.avg)

        update_sample_count = 0
        data_start_time = time.time()
        # end for

    if hasattr(optimizer, "sync_lookahead"):
        optimizer.sync_lookahead()
    return OrderedDict([("loss", losses_m.avg)])


def parse_batch_transforms(
    batch_transformations: Optional[List[Dict[str, _JSONDict]]] = None
) -> Tuple[List[Transformation]]:
    """Parse batch transformations from timm algorithms.
    Args:
        batch_transformations: The batch transformations to be parsed.
    """
    if batch_transformations is not None:
        parser = TransformationsParser()
        transformations, _ = parser.deserialize_transformations(batch_transformations)
        return transformations
