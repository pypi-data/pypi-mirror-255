import os
import shutil
from typing import List

from dicomset import config

from .nrrd_dataset import NRRDDataset

def list() -> List[str]:
    path = os.path.join(config.directories.datasets, 'nrrd')
    if os.path.exists(path):
        return sorted(os.listdir(path))
    else:
        return []

def create(name: str) -> None:
    ds_path = os.path.join(config.directories.datasets, 'nrrd', name)
    os.makedirs(ds_path)
    return NRRDDataset(name)

def destroy(name: str) -> None:
    ds_path = os.path.join(config.directories.datasets, 'nrrd', name)
    if os.path.exists(ds_path):
        shutil.rmtree(ds_path)

def recreate(name: str) -> None:
    destroy(name)
    return create(name)
