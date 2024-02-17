import io
import os

from typing import List, Iterator


class OpenMany:
    def __init__(self, file_paths: List[str], *args, **kwargs) -> None:
        self.file_paths: List[str] = file_paths
        self.files: List[io.IOBase] = [None] * len(file_paths)
        self.__args = args
        self.__kwargs = kwargs

    def __enter__(self) -> List[io.IOBase]:
        for index, file_path in enumerate(self.file_paths):
            self.files[index] = open(file_path, *self.__args, **self.__kwargs)
        return self.files

    def __exit__(self, type, value, traceback) -> None:
        for file in self.files:
            file.close()


def safe_makedirs(dirname: str):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def get_subfolders(parent_dir) -> Iterator[str]:
    """Returns the folders in a directory."""
    return [
        f"{parent_dir}/{name}"
        for name in os.listdir(parent_dir)
        if os.path.isdir(f"{parent_dir}/{name}")
    ]


def iterate_through_nested_folders(base_folder: str, max_depth: int) -> Iterator[str]:
    """Iterates through all folders with a certain depth from the specified base folder."""
    yield base_folder
    sub_folders = get_subfolders(base_folder)
    if max_depth > 0:
        for subfolder in sub_folders:
            for folder in iterate_through_nested_folders(subfolder, max_depth - 1):
                yield folder
    else:
        for folder in get_subfolders(base_folder):
            yield folder


def iterate_through_files_in_nested_folders(
    base_folder: str, max_depth: int
) -> Iterator[str]:
    """Iterates through all of the files that are in the folders with a
    certain depth from the specified base folder."""
    for folder in iterate_through_nested_folders(base_folder, max_depth):
        for file in os.listdir(folder):
            yield f"{folder}/{file}"
