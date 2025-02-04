import os.path
import pickle
from typing import Any, Callable, Optional, Tuple

import numpy as np
from PIL import Image

from torchvision.datasets.utils import check_integrity, download_and_extract_archive
from torchvision.datasets.vision import VisionDataset


class CIFAR10(VisionDataset):
    """`CIFAR10 <https://www.cs.toronto.edu/~kriz/cifar.html>`_ Dataset.

    Args:
        dataset_path (string): Root directory of dataset where directory
            ``cifar-10-batches-py`` exists or will be saved to if download is set to True.
        train (bool, optional): If True, creates dataset from training set, otherwise
            creates from test set.
        transform (callable, optional): A function/transform that takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.

    """

    # base_folder = "cifar-10-batches-py"
    # url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
    # filename = "cifar-10-python.tar.gz"
    # tgz_md5 = "c58f30108f718f92721af3b95e74349a"
    # train_list = [
    #     ["data_batch_1", "c99cafc152244af753f735de768cd75f"],
    #     ["data_batch_2", "d4bba439e000b95fd0a9bffe97cbabec"],
    #     ["data_batch_3", "54ebc095f3ab1f0389bbae665268c751"],
    #     ["data_batch_4", "634d18415352ddfa80567beed471001a"],
    #     ["data_batch_5", "482c414d41f54cd18b22e5b47cb7c3cb"],
    # ]

    meta = {
        "filename": "batches.meta",
        "key": "label_names",
        "md5": "5ff9c542aee3614f3951f8cda6e48888",
    }

    def __init__(
            self,
            rate: list,
            dataset_path: str,
            train: bool = True,
            transform: Optional[Callable] = None,
            target_transform: Optional[Callable] = None,
    ) -> None:

        super().__init__(dataset_path, transform=transform, target_transform=target_transform)

        self.rate = rate

        self.train = train  # training set or test set

        # if download:
        #     self.download()

        # if not self._check_integrity():
        #     raise RuntimeError("Dataset not found or corrupted. You can use download=True to download it")

        train_list = os.listdir(self.root)
        self.train_list = []
        for file_name in train_list:
            if "data" in file_name:
                self.train_list.append(file_name)

        self.test_list = ["test_batch"]

        if self.train:
            files_list = self.train_list
        else:
            files_list = self.test_list

        self.data: Any = []
        self.targets = []

        # now load the picked numpy arrays
        for i, file_name in enumerate(files_list):
            file_path = os.path.join(self.root, file_name)
            with open(file_path, "rb") as f:
                entry = pickle.load(f, encoding="latin1")

                # # check the dataset
                # entry0 = entry['data'][0]
                # for k in range(1, 5000):
                #     if (entry0 == entry['data'][k]).all():
                #         print("same")
                #     else:
                #         print("diff")

                entry = self.reduce_data(entry, i)
                self.data.append(entry["data"])
                if "labels" in entry:
                    self.targets.extend(entry["labels"])
                else:
                    self.targets.extend(entry["fine_labels"])

        self.data = np.vstack(self.data).reshape(-1, 3, 32, 32)
        self.data = self.data.transpose((0, 2, 3, 1))  # convert to HWC

        self._load_meta()

    def reduce_data(self, entry, class_num) -> dict:
        new_entry = {"data": [],
                     "labels": [],
                     "filenames": []}
        rand_number = np.random.randint(low=0, high=500, size=int(5000 * self.rate[class_num]))
        rand_number.tolist()
        for i in rand_number:
            new_entry['data'].append(entry['data'][i])
            new_entry['labels'].append(entry['labels'][i])
            new_entry['filenames'].append(entry['filenames'][i])
        return new_entry

    def _load_meta(self) -> None:
        path = os.path.join(self.root, self.meta["filename"])
        # if not check_integrity(path, self.meta["md5"]):
        #     raise RuntimeError("Dataset metadata file not found or corrupted. You can use download=True to download it")
        with open(path, "rb") as infile:
            data = pickle.load(infile, encoding="latin1")
            self.classes = data[self.meta["key"]]
        self.class_to_idx = {_class: i for i, _class in enumerate(self.classes)}

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        """
        Args:
            index (int): Index

        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        img, target = self.data[index], self.targets[index]

        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = Image.fromarray(img)

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self) -> int:
        return len(self.data)

    # def _check_integrity(self) -> bool:
    #     root = self.root
    #     for fentry in self.train_list + self.test_list:
    #         filename, md5 = fentry[0], fentry[1]
    #         fpath = os.path.join(root, self.base_folder, filename)
    #         if not check_integrity(fpath, md5):
    #             return False
    #     return True

    # def download(self) -> None:
    #     if self._check_integrity():
    #         print("Files already downloaded and verified")
    #         return
    #     download_and_extract_archive(self.url, self.root, filename=self.filename, md5=self.tgz_md5)

    def extra_repr(self) -> str:
        split = "Train" if self.train is True else "Test"
        return f"Split: {split}"


class CIFAR100(CIFAR10):
    """`CIFAR100 <https://www.cs.toronto.edu/~kriz/cifar.html>`_ Dataset.

    This is a subclass of the `CIFAR10` Dataset.
    """

    base_folder = "cifar-100-python"
    url = "https://www.cs.toronto.edu/~kriz/cifar-100-python.tar.gz"
    filename = "cifar-100-python.tar.gz"
    tgz_md5 = "eb9058c3a382ffc7106e4002c42a8d85"
    train_list = [
        ["train", "16019d7e3df5f24257cddd939b257f8d"],
    ]

    test_list = [
        ["test", "f0ef6b0ae62326f3e7ffdfab6717acfc"],
    ]
    meta = {
        "filename": "meta",
        "key": "fine_label_names",
        "md5": "7973b15100ade9c7d40fb424638fde48",
    }


if __name__ == '__main__':
    import torchvision.transforms as transforms
    from torch.utils.data import DataLoader

    normMean = [0.49139968, 0.48215827, 0.44653124]
    normStd = [0.24703233, 0.24348505, 0.26158768]
    normTransform = transforms.Normalize(normMean, normStd)

    trainTransform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        normTransform
    ])

    rate = [0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    dataset = CIFAR10(rate=rate, dataset_path='cifar_after_divide', train=True,
                      transform=trainTransform)
    dataloader = DataLoader(dataset, shuffle=True, batch_size=16)
    it = iter(dataloader)
    data = next(it)

    print("")
