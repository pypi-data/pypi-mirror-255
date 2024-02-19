
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from torch.utils.data import DataLoader




def init_train_misc(dataloader_train: DataLoader,
                    model: nn.Module,
                    train_opts: dict,
                    dataloader_test: Optional[DataLoader] = None):
    """
    Initialize miscellaneous training info/settings.

    Loss function, optimizer, and scheduler are specified with names (str) and params (dict), e.g.
        train_opts = dict(
            loss_fn='MSELoss',
            optimizer='SGD',
            optimizer_params=dict(lr=0.1),
            scheduler='MultiStepLR',
            scheduler_params=dict(milestones=[0.5, 0.8], gamma=0.2)
        )
    """
    # extract options
    loss_fn_str = train_opts.get('loss_fn', 'MSELoss')
    loss_fn_params = train_opts.get('loss_fn_params', {})
    optimizer_str = train_opts.get('optimizer', 'SGD')
    optimizer_params = train_opts.get('optimizer_params', {})
    scheduler_str = train_opts.get('scheduler', 'None')
    scheduler_params = train_opts.get('scheduler_params', {})

    # batch sizes
    num_batches_train = len(dataloader_train)
    num_batches_test = max(len(dataloader_test), 1) if dataloader_test is not None else 1

    # set up loss function
    loss_fn = getattr(nn, loss_fn_str)(**loss_fn_params)

    # set up optimizer
    optimizer = getattr(optim, optimizer_str)(model.parameters(), **optimizer_params)

    # set up scheduler
    if scheduler_str == 'None':
        scheduler = None
    else:
        scheduler = getattr(lr_scheduler, scheduler_str)(optimizer, **scheduler_params)

    return loss_fn, optimizer, scheduler, num_batches_train, num_batches_test






def perform_train_epoch(model: nn.Module,
                        loss_fn,
                        optimizer: optim.Optimizer,
                        dataloader_train: DataLoader,
                        max_grad_norm: Optional[float] = None) \
        -> float:
    """Perform one training epoch"""
    is_training = model.training
    model.train()

    epoch_losses = []
    for i, (X, Y) in enumerate(dataloader_train):
        model.zero_grad(set_to_none=True)
        _, loss = forward_pass_through_seq(model, X, Y=Y, loss_fn=loss_fn, return_Y_pred=False)#, device=device)
        loss.backward()
        if max_grad_norm is not None:
            nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
        optimizer.step()

        epoch_losses.append(loss.detach().item())

    train_loss = torch.tensor(epoch_losses).sum().item()

    model.training = is_training

    return train_loss


@torch.no_grad()
def perform_test_epoch(model: nn.Module,
                       loss_fn,
                       dataloader_test: DataLoader) \
        -> float:
    """Evaluate on a test dataset"""
    is_training = model.training
    model.eval()

    epoch_losses = []
    for i, (X, Y) in enumerate(dataloader_test):
        _, loss = forward_pass_through_seq(model, X, Y=Y, loss_fn=loss_fn, return_Y_pred=False)

        epoch_losses.append(loss.detach().item())

    test_loss = torch.tensor(epoch_losses).sum().item()

    model.training = is_training

    return test_loss


def forward_pass_through_seq(model: nn.Module,
                             X: torch.Tensor,
                             Y: Optional[torch.Tensor] = None,
                             loss_fn = None,
                             return_Y_pred: bool = True) \
        -> Tuple[Optional[torch.Tensor], torch.Tensor]:
    """Full forward pass through sequence."""
    # perform forward pass, save outputs and loss
    loss = torch.zeros(1, dtype=torch.float)

    # process
    out: torch.Tensor = model(X)
    if Y is not None and loss_fn is not None:
        loss = loss_fn(out, Y)
    Y_pred = out if return_Y_pred else None

    return Y_pred, loss