class Node:
    def __init__(self, source: lark.Tree = None,
                 parent: Node = None,
                 depth: int = 0,
                 root: Node = None,
                 children: Union[list[Node], List[Node]] = None,
                 type_: str = None,
                 vtype: str = None,
                 names: dict[str, Node] = None,
                 update: bool = True, **kwargs):

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
        if update:
            self.update_attrs()

