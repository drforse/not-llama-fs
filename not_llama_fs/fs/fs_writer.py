import abc
import pathlib

from not_llama_fs.fs.tree import TreeObject


class FsWriter(abc.ABC):
    def write_tree(self, tree: TreeObject) -> None:
        raise NotImplementedError()

    def write_file(self, parent: TreeObject, file: TreeObject) -> None:
        raise NotImplementedError()


class LocalDiskFsWriter(FsWriter):
    def __init__(self, dest_path: pathlib.Path, move: bool = False):
        self.dest_path = dest_path
        self.move = move

    def write_tree(self, tree: TreeObject) -> None:
        for child in tree.children:
            if child.is_dir():
                self.write_tree(child)
            else:
                self.write_file(tree, child)

    def write_file(self, parent: TreeObject, file: TreeObject) -> None:
        # print(f"{file.src_path=}")
        # print(f"{file.file=}")
        # print(f"{self.dest_path=}")
        file_dst_path = self.dest_path / file.file["dst_path"]
        # print(f"{file_dst_path=}")
        file_dst_path.parent.mkdir(parents=True, exist_ok=True)
        src_file_path = pathlib.Path(file.src_path)
        if self.move:
            src_file_path.rename(file_dst_path)
        else:
            file_dst_path.write_bytes(src_file_path.read_bytes())
