"""
CUT EDGES & BOUNDARY NODES
"""

from typing import Any, List, Dict, Tuple

from rdabase import OUT_OF_STATE


def cuts_and_boundaries(
    plan: Dict[str, int | str], graph: Dict[str, List[str]]
) -> Tuple[float, float]:
    """Given a plan and a graph, return a dictionary of cut edges and boundary nodes."""

    precision: int = 4
    cuts, edges, boundaries, nodes = 0, 0, 0, 0

    for node, neighbors in graph.items():
        if node == OUT_OF_STATE:
            continue
        nodes += 1
        boundary: bool = False

        for neighbor in neighbors:
            if neighbor == OUT_OF_STATE:
                continue
            edges += 1

            if plan[node] != plan[neighbor]:
                cuts += 1
                boundary = True

        if boundary:
            boundaries += 1

    cut_pct: float = round(cuts / edges, precision)
    boundary_pct: float = round(boundaries / nodes, precision)

    return cut_pct, boundary_pct


### END ###
