"""Dataset and related classes"""

import math
from typing import List, Tuple, Iterator, Union

import numpy as np
import torch
from torch.utils.data import Dataset, Sampler

from .constants import NUM_FEATURES_TEST




class ExampleDataset(Dataset):
    """
    This is a template of a custom dataset for PyTorch experiments. Only __len__ and __getitem__ methods are needed
    and their implementation is entirely up to the developer.
    """
    def __init__(self, params: dict):
        """Initialize the dataset."""
        self._params = params # miscellaneous params can go here

        # make a toy linear dataset
        num_samps = 50
        input_ = np.arange(num_samps * NUM_FEATURES_TEST).reshape(num_samps, NUM_FEATURES_TEST)
        self._coeffs = dict(a=np.random.rand(NUM_FEATURES_TEST), b=np.random.rand())
        output_ = input_ @ self._coeffs['a'] + self._coeffs['b']

        self._data = {
            'input': input_,
            'output': output_
        }

        # save dataset size (to avoid compute during call to __len__)
        self._num_samps = num_samps

    def __len__(self):
        return self._num_samps

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get one item in this dataset. The output could be two tensors or dictionaries of lists/arrays or anything
        else that can be interpreted by PyTorch's batching operations.

        A batch sampler will call this method via dataset[i] for B indices i.
        Individual items of size NxD that are returned are packed into a BxNxD tensor.
        This can be used to batch sequences of length N and feature dimensionality D.
        """
        input_ = torch.Tensor(self._data['input'][idx, :])
        output_ = torch.Tensor(self._data['output'][idx:idx + 1])

        return input_, output_





class VariableLengthSequenceBatchSampler(Sampler[List[int]]):
    """
    Batch sampler for variable-length sequence modeling.
    Generated batches are comprised of same-length sequences with uniform sampling over the entire dataset.
    Each item in a dataset is associated with a group in which all items have the same length.
    """
    def __init__(self,
                 group_ids: List[Union[str, int]],
                 batch_size: int,
                 mode: str):
        """Init.

        group_ids: list of group ids (unique integers), one per sequence
        batch_size: size of batches
        mode: 'train', 'test'

        The argument 'mode' controls whether some groups are truncated to have exactly batch_size items in each batch
        or if one possibly smaller batch is allowed so that all items are included.
        """
        super().__init__()

        assert mode in ['train', 'test']

        self._batch_size = batch_size
        self._mode = mode

        # collect batch info for each group
        self._batch_info = {}
        g_ids_np = np.array(group_ids)
        for group_id in set(group_ids):
            idxs_ = np.where(g_ids_np == group_id)[0]
            self._batch_info[group_id] = {'idxs_in_dataset': idxs_}

        self._num_batches_tot = len(self._make_batches())

    def __len__(self) -> int:
        return self._num_batches_tot

    def __iter__(self) -> Iterator[List[int]]:
        batches = self._make_batches()
        order = np.random.permutation(len(batches)) if self._mode == 'train' else range(len(batches))
        for i in order:
            yield batches[i]

    def _make_batches(self) -> List[List[int]]:
        """Make a new set of batches. Always the same number of batches."""
        batches: List[List[int]] = []
        for group_id, d in self._batch_info.items():
            num_idxs = len(d['idxs_in_dataset'])
            if self._mode == 'train': # permute and truncate list of indices to get integer number of full batches
                # determine number of full batches and item indices
                num_batches_full = num_idxs // self._batch_size
                if num_batches_full == 0: # if a group has too few items, skip it
                    continue
                num_idxs_tot = self._batch_size * num_batches_full

                # split indices into batches
                idxs_perm = np.random.permutation(d['idxs_in_dataset'])[:num_idxs_tot]
                batches_group: List[List[int]] = idxs_perm.reshape(num_batches_full, self._batch_size).tolist()
                batches += batches_group
            elif self._mode == 'test': # don't permute (shuffle) and include all samples
                num_batches = int(math.ceil(num_idxs / self._batch_size))
                for i in range(num_batches):
                    batches_group: List[int] = (
                        d['idxs_in_dataset'][i * self._batch_size:(i + 1) * self._batch_size].tolist())
                    assert len(batches_group) > 0
                    batches.append(batches_group)
            else:
                raise NotImplementedError

        return batches

