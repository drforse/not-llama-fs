import pathlib
from typing import Any

from asciitree import LeftAligned, BoxStyle
from asciitree.drawing import BOX_LIGHT


class TreeObject:
    def __init__(self, name: str, children: list['TreeObject'], file: Any = None, src_path: str = None):
        if file is not None and children:
            raise ValueError("Cannot both be file and have children")
        if file is None and src_path is not None:
            raise ValueError("Directory cannot have src_path")
        if file is not None and src_path is None:
            raise ValueError("Cannot be a file without src_path")
        self.file = file
        self.src_path = src_path
        self.name = name
        self.children = children

    def is_dir(self):
        return self.file is None

    def add_child(self, child: 'TreeObject | str'):
        self.children.append(child)

    @classmethod
    def from_json(cls, data: dict):
        tree = None
        for file in data["files"]:
            parts = pathlib.Path(file["dst_path"]).parts
            if tree is None:
                tree = TreeObject(parts[0], [])
            current = tree
            for part in parts:
                # print(current.name, current.children)
                if part not in [child.name for child in current.children] + [current.name]:
                    if part == parts[-1]:
                        current.add_child(TreeObject(part, [], file, src_path=file["src_path"]))
                    else:
                        current.add_child(TreeObject(part, []))
                current_child = [child for child in current.children if child.name == part]
                if current_child:
                    current = current_child[0]
        return tree

    def __str__(self, level=0):
        def build_tree(node):
            tree_dict = {node.name: {}}
            for child in node.children:
                if child.is_dir():
                    child_name = child.name
                else:
                    child_name = f"{child.name} ({child.src_path})"
                tree_dict[node.name][child_name] = build_tree(child)[child.name]
            return tree_dict

        tree = build_tree(self)
        tr = LeftAligned(draw=BoxStyle(gfx=BOX_LIGHT, horiz_len=1))
        return tr(tree)

    def __repr__(self):
        return self.__str__()
