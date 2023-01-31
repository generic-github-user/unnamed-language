from __future__ import annotations
import lark
from typing import Callable, Union

from compiler.pylist import List
from compiler.option import Option


class Node:
    def __init__(self,
                 children: Union[list[Node], List[Node]],
                 type_: str,
                 parent: Option[Node] = Option.none(),
                 vtype: Option[str] = Option.none(),
                 **kwargs):

        self.parent: Option[Node] = parent

        if children is None:
            children = List()
        elif isinstance(children, list):
            children = List(children)
        self.children = children

        self.type: str = type_
        self.vtype: Option[str] = vtype

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.aliases = None
        # should we separate the AST representation from the IR?
        match self.type:
            case 'return': self.aliases = 'arg'
            case 'call': self.aliases = 'f args'
            case 'bin_op': self.aliases = 'left op right'
            case 'assignment': self.aliases = 'left right'
            case 'let_stmt': self.aliases = 'left right'
            case 'typed_name': self.aliases = 'name ptype'
        if self.aliases is not None: self.aliases = self.aliases.split()

    def __getitem__(self, key: str):
        return self.children[self.aliases.index(key)]

    def __setitem__(self, key: str, value: Node):
        self.children[self.aliases.index(key)] = value

    def __str__(self) -> str:
        return f'Node <{self.type} ~ {self.vtype}> ({self.depth})' + '\n' +\
            '\n'.join('  '*self.depth + str(n) for n in self.children)

    __repr__ = __str__
