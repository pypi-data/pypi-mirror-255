from typing import NamedTuple


class Node:
    id: str
    weight: int
    neighbors: set["Node"]

    def __init__(self, id: str, weight: int, neighbors: set["Node"]) -> None:
        self.id = id
        self.weight = weight
        self.neighbors = neighbors

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Node)
        return id(self) == id(other)

    def __repr__(self) -> str:
        return f"Node({self.id}, {self.weight}, {set(s.id for s in self.neighbors)})"


class Graph(NamedTuple):
    nodes: frozenset[Node]

    def check(self) -> None:
        for n in self.nodes:
            for neighbor in n.neighbors:
                assert neighbor in self.nodes


# Taking the union requires knowing the original graph so that it
# can be used to look up neighbors between the two graphs being combined.
def Union(universe: Graph, g1: Graph, g2: Graph) -> Graph:
    original2node: dict[str, Node] = {n.id: n for n in universe.nodes}
    nodes: set[Node] = set(g1.nodes) | set(g2.nodes)
    id2node: dict[str, Node] = {}
    for n in nodes:
        id2node[n.id] = Node(n.id, n.weight, set())
    for n in nodes:
        for neighbor in original2node[n.id].neighbors:
            if neighbor.id in id2node:
                id2node[n.id].neighbors.add(id2node[neighbor.id])
    g = Graph(frozenset(id2node.values()))
    return g


def mkSubsetGraph(nodes: set[Node]) -> Graph:
    id2node: dict[str, Node] = {}
    for n in nodes:
        id2node[n.id] = Node(n.id, n.weight, set())
    for n in nodes:
        for neighbor in n.neighbors:
            if neighbor.id in id2node:
                id2node[n.id].neighbors.add(id2node[neighbor.id])
    g = Graph(frozenset(id2node.values()))
    return g


class Tree:
    node: Node
    children: set["Tree"]
    subtree_weight: float

    def __init__(self, node: Node, children: set["Tree"]) -> None:
        self.node = node
        self.children = children

    def nodecount(self) -> int:
        # avoiding recursion due to Python's recursion limit
        wl: list[Tree] = [self]
        total = 0
        while wl:
            current = wl.pop()
            wl.extend(current.children)
            total += 1
        return total

    def compute_weight(self) -> None:
        # avoiding recursion due to Python's recursion limit
        # done for side effects
        wl: list[tuple[Tree, int]] = [(self, 0)]
        while wl:
            t: Tree
            index: int
            t, index = wl.pop()
            children = list(t.children)
            if index < len(children):
                wl.append((t, index + 1))
                wl.append((children[index], 0))
            else:
                t.subtree_weight = t.node.weight + sum(
                    c.subtree_weight for c in t.children
                )

    def all_subtrees(self) -> list["Tree"]:
        wl: list[Tree] = [self]
        index: int = 0
        while index < len(wl):
            current: Tree = wl[index]
            wl.extend(current.children)
            index += 1
        return wl

    def all_subtrees_above(self, above: "Tree") -> list["Tree"]:
        wl: list[Tree] = [self]
        index: int = 0
        while index < len(wl):
            current: Tree = wl[index]
            wl.extend(c for c in current.children if c != above)
            index += 1
        return wl

    def __hash__(self) -> int:
        return hash(self.node.id)

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Tree)
        return id(self) == id(other)

    def __repr__(self) -> str:
        return f"Tree({self.node.id}, {set(s.node.id for s in self.children)})"


def Tree2Graph(t: Tree) -> Graph:
    nodes: set[Node] = set(st.node for st in t.all_subtrees())
    return mkSubsetGraph(nodes)


### END ###
