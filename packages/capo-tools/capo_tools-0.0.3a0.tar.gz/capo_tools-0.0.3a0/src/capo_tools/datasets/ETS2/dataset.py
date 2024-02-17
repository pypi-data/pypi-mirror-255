import os

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

from datasets.ETS2.ets2_tools import get_data
from datasets.ETS2.ets2_tools.depth_file import read_depth_file


class ETS2Dataset(Dataset):
    def __init__(self, indexes, data_path, is_train=False, transform=None):
        super(ETS2Dataset, self).__init__()
        self.data_path = data_path
        self.is_train = is_train
        self.indexes = indexes
        self.data = get_data(self.data_path)
        self.transform = transform
        self.maxDepth = 80.0

    def __getitem__(self, item):
        index = self.indexes[item]
        row = self.data.iloc[index]
        file_path = os.path.join(self.data_path, row['session'], row['capture'])
        image = Image.open(f"{file_path}.jpg")

        depth_file = read_depth_file(f"{file_path}.depth.raw")
        header = depth_file.header
        depth = -depth_file.get_data()
        depth[depth == 0] = 3000.0
        depth_shape = (header['height'], header['width'], 1)

        depth = np.clip(np.reshape(depth, depth_shape), 1, self.maxDepth)
        sample = {'image': image, 'depth': depth, 'frame': file_path}

        if self.transform:
            sample = self.transform(sample)

        return sample['image'], sample['depth'], \
            {"path": file_path, "session": row['session'], "capture": row['capture']}

    def __len__(self):
        return len(self.indexes)


class ETS2DatasetVideo(Dataset):
    def __init__(self, indexes, data_path, is_train=False, transform=None, max_depth: float = 80.0):
        super(ETS2DatasetVideo, self).__init__()
        self.data_path = data_path
        self.is_train = is_train
        self.data_indexes = indexes
        self.data = get_data(data_path)
        self.transform = transform
        self.maxDepth = max_depth

    def __getitem__(self, item):
        sequence_start_index = self.data_indexes[item]

        # TODO: parametrize number of frames in sequence
        sequence_end_index = sequence_start_index + 10

        data_rows = self.data.iloc[sequence_start_index:sequence_end_index, :]
        files = [os.path.join(self.data_path, x) for x in (data_rows['session'] + "/" + data_rows['capture']).tolist()]

        x = []
        y = []
        metadata = []

        for index, file in enumerate(files):
            file_path = f"{file}.jpg"
            image = Image.open(file_path)

            depth_file = read_depth_file(f"{file}.depth.raw")
            header = depth_file['header']
            depth = -depth_file['data']
            depth_shape = (header['height'], header['width'], 1)
            depth = np.clip(np.reshape(depth, depth_shape), 1, self.maxDepth)

            sample = {'image': image, 'depth': depth, 'frame': file}
            sample = self.transform(sample)
            x.append(sample['image'])
            y.append(sample['depth'])

            data_row = data_rows.iloc[index]
            metadata.append({"path": file_path, "session": data_row['session'], "capture": data_row['capture']})

        x = torch.stack((x))
        y = torch.stack((y))

        return x, y, metadata

    def __len__(self):
        return len(self.data_indexes)