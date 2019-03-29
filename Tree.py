
class Tree:
    def __init__(self):
        self.parent = None
        self.children = []

    def get_parent(self):
        return self.parent

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def add_children(self, nodes):
        for node in nodes:
            node.parent = self
        self.children.extend(nodes)

    def get_children(self):
        return self.children

    def num_children(self):
        return len(self.get_children())

