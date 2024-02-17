from typing import Optional
import random

from .graph import Node, Graph, Tree, mkSubsetGraph


# Generating Random Spanning Trees More Quickly than the Cover Time
# David Bruce Wilson
# https://www.cs.cmu.edu/~15859n/RelatedWork/RandomTrees-Wilson.pdf
def RandomTreeRoot(units: list[Node], r: Node) -> Tree:
    InTree: dict[Node, Tree] = {}
    Next: dict[Node, Node] = {}
    neighbors: dict[Node, list[Node]] = {}
    u: Optional[Node]
    InTree[r] = Tree(r, set())
    for i in units:
        assert i is not None
        u = i
        while u not in InTree:
            if u not in neighbors:
                neighbors[u] = list(u.neighbors)
            Next[u] = random.choice(neighbors[u])
            u = Next[u]
            assert u is not None
        u = i
        while u not in InTree:
            InTree[u] = Tree(u, set())
            u = Next[u]
            assert u is not None

    # turn all that into a tree
    for u in units:
        if u == r:
            assert u not in Next
            continue
        assert u in Next
        t: Tree = InTree[u]
        parent: Tree = InTree[Next[u]]
        parent.children.add(t)
    return InTree[r]


def RandomTree(graph: Graph) -> Tree:
    all = list(graph.nodes)
    graph.check()
    root: Node = random.choice(all)
    t: Tree = RandomTreeRoot(all, root)
    return t


### END ###
