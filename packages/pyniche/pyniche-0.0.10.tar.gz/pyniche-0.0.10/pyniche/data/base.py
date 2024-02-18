import random
import lightning as L

from torch.utils.data import random_split, DataLoader
from datasets import concatenate_datasets, load_dataset


class BaseDataModule(L.LightningDataModule):
    """
    parameters
    ---
    dataname and configname: str
        local config file or repository name on the huggingface hub
    batch: int (default: 32, optional)
        batch size
    n_train: int or float (default: None, optional)
        if specified, use only n_train samples in the train/val process
        otherwise, use the default split
    """

    def __init__(
        self,
        dataname: str,
        configname: str = None,
        batch: int = 32,
        n_train: any = None,  # no redistribution if None
        k: int = 5,  # k-fold cross validation
        **kwargs,
    ):
        super().__init__()
        # input parameters
        self.dataname = dataname
        self.configname = configname
        self.batch = batch
        self.n_train = n_train
        self.k = k
        # datasets
        self.dataset = {
            "train": None,
            "val": None,
            "test": None,
        }
        self.kwargs = kwargs

    def prepare_data(self):
        # download
        pass

    def setup(self, stage: str):
        # Assign train/val datasets for use in dataloaders
        if stage == "fit":
            # load and re-distribute train/val
            data_train = self.get_dataset("train")
            try:
                data_val = self.get_dataset("val")
                data_train, data_val = self.re_distribute(
                    data_train,
                    data_val,
                    self.n_train,
                    self.k,
                )
            except:
                # if the dataset does not have a validation split
                data_train, data_val = self.re_distribute(
                    data_train,
                    None,
                    self.n_train,
                    self.k,
                )
            # assign and set transforms
            self.dataset["train"] = data_train
            self.dataset["val"] = data_val
        elif stage == "test":
            data_test = self.get_dataset("test")
            self.dataset["test"] = data_test

    def get_dataset(self, split):
        return load_dataset(
            self.dataname,
            self.configname,
            split=split,
            **self.kwargs,
        )

    def set_dataset(self, split):
        """
        split: str
            train, val, or test
        """
        self.dataset[split] = self.get_dataset(split)

    # loaders
    def get_dataloader(self, split):
        if split == "train":
            return self.train_dataloader()
        elif split == "val":
            return self.val_dataloader()
        elif split == "test":
            return self.test_dataloader()

    def train_dataloader(self):
        if self.dataset["train"] is None:
            self.set_dataset("train")
        return DataLoader(
            self.dataset["train"].with_transform(self._transform_train),
            batch_size=self.batch,
            shuffle=True,
            pin_memory=True,
            collate_fn=self._collate_fn_train,
        )

    def val_dataloader(self):
        if self.dataset["val"] is None:
            self.set_dataset("val")
        return DataLoader(
            self.dataset["val"].with_transform(self._transform_val),
            batch_size=self.batch,
            shuffle=False,
            pin_memory=True,
            collate_fn=self._collate_fn_val,
        )

    def test_dataloader(self):
        if self.dataset["test"] is None:
            self.set_dataset("test")
        return DataLoader(
            self.dataset["test"].with_transform(self._transform_test),
            batch_size=self.batch,
            shuffle=False,
            pin_memory=True,
            collate_fn=self._collate_fn_test,
        )

    # additional methods
    def re_distribute(self, data_train, data_val=None, n=None, k=5):
        """
        data_train, data_val: datasets.Dataset
        n: int or float, sample size in train and val
            if None, do nothing
            if -1, use all samples
            if int, number of samples in train and val
            if float, ratio of samples in train and val
        k: int
            how many folds to split the train/val set

        """
        if n is not None:
            # concatenate to get the full dataset
            if data_val:
                data_full = concatenate_datasets([data_train, data_val])
            else:
                data_full = data_train

            # determine n
            total_n = len(data_full)
            if n == -1:
                n = total_n
            elif isinstance(n, float):
                n = int(n * total_n)
            n_val = int(n / k)

            # split
            # select n samples from total_n
            idx = random.sample(range(total_n), n)
            data_train = data_full.select(idx[n_val:])
            data_val = data_full.select(idx[:n_val])

        # return
        return data_train, data_val

    # need to be implemented
    def _collate_fn(self, batch):
        raise NotImplementedError

    def _collate_fn_train(self, batch):
        batch = self._collate_fn(batch)
        return batch

    def _collate_fn_val(self, batch):
        batch = self._collate_fn(batch)
        return batch

    def _collate_fn_test(self, batch):
        batch = self._collate_fn(batch)
        return batch

    def _transform_train(examples):
        return examples

    def _transform_val(examples):
        return examples

    def _transform_test(examples):
        return examples
