from __future__ import annotations
import lark
from typing import Callable, Union

from compiler.pylist import List


class Node:
    def __init__(self,
                 children: Union[list[Node], List[Node]] = None,
                 type_: str = None,
                 source: lark.Tree = None,
                 parent: Node = None,
                 depth: int = 0,
                 root: Node = None,
                 vtype: str = None,
                 names: dict[str, Node] = None,
                 update: bool = True,
                 # aliases:  = None,
                 **kwargs):

        self.parent: Node = parent
        self.root: Node = root if root else self
        self.depth: int = depth

        if children is None:
            children = List()
        elif isinstance(children, list):
            children = List(children)
        self.children = children
        for node in self.children:
            if node.parent is None:
                node.parent = self
                node.depth = self.depth + 1

        self.type: str = type_
        self.source: lark.Tree = source

        self.vtype: str = vtype

        if names is None and parent is not None:
            # names = dict()
            # assert parent is not None, self
            names = parent.names
        self.names = names

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.data_attrs = set()
        self.child_aliases = List()
        # should we separate the AST representation from the IR?
        match self.type:
            case 'return':
                assert self.children.len() == 1, self
                self.alias_children('arg')
            case 'fn_signature':
                self.alias_children('name type_params arguments return_type',
                                    'name arguments return_type')
            case 'function_declaration':
                self.alias_children('signature body')
                self.alias_children('name type_params arguments return_type',
                                    'name arguments return_type',
                                    target=self.signature)
            case 'call':
                self.alias_children('f args')
            case 'list' | 'tuple':
                self.items = self.children
            case 'bin_op':
                self.alias_children('left op right')
            case 'assignment':
                self.alias_children('left right')
            case 'let_stmt':
                self.alias_children('left right')
            case 'typed_name':
                self.alias_children('name ptype')

    def alias_children(self, *args, target=None):
        if target is None:
            target = self
        args = List(args).map(lambda x: x.split() if isinstance(x, str) else x)
        matches = args.filter(lambda x: len(x) == target.children.len())
        assert matches.len() > 0, f"At least one alias group must have as many elements as this node has children; got {args}, while node has children {target.children}; target is\n{target}"
        assert matches.len() == 1
        if target == self:
            setattr(self, 'child_aliases', matches[0])
        for name, node in zip(matches[0], target.children):
            setattr(self, name, node)
            self.data_attrs.add(name)

    def __getattr__(self, attr):
        # assert (attr in self.child_aliases), f"Attempted to access attribute `{attr}`; valid auxiliary attributes for this type of node ({self.type}) are: {self.child_aliases}"
        # if attr in self.child_aliases:
        aliases = None
        if hasattr(self, 'child_aliases'):
            aliases = object.__getattribute__(self, 'child_aliases')
        if (aliases is not None) and (attr in aliases):
            return self.children[self.child_aliases.index(attr)]
        return object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        # assert (attr in self.child_aliases), f"Attempted to access attribute `{attr}`; valid auxiliary attributes for this type of node ({self.type}) are: {self.child_aliases}"
        if attr in self.child_aliases:
            self.children[self.child_aliases.index(attr)] = value
        else:
            object.__setattr__(self, attr, value)

    def __str__(self) -> str:
        return f'Node <{self.type} ~ {self.vtype}> ({self.depth})' + '\n' +\
            '\n'.join('  '*self.depth + str(n) for n in self.children)

    __repr__ = __str__
