"""
RANDOM MAP
Generate a random map with N contiguous, 'roughly equal' population districts.

This code is adapted from Todd Proebsting's early work in the `ensembles` project.
He wrote most of the code which I only lightly edited to make it work in this context.
"""

import random
from typing import List, Dict, Tuple, Set, Optional

from rdabase import Assignment

from ..ust import Node, Graph, Tree, RandomTree, mkSubsetGraph


def random_map(
    adjacencies: List[Tuple[str, str]],
    populations: Dict[str, int],
    N: int,
    seed: int,
    # initial_csv: str,
    *,
    roughly_equal: float = 0.01,
    attempts_per_seed: int = 1000,
    # verbose: bool = False,
) -> List[Assignment]:
    """Generate a random map with N contiguous, 'roughly equal' population districts."""

    random.seed(seed)

    total_population: int = sum(populations.values())
    target_population: int = int(total_population / N)
    # root: Node

    remainder: Graph = mkGraph(adjacencies, populations)

    # tbc: Set[str] = set(populations.keys())

    assignments: Dict[str, int] = {}
    district: int = 1
    # tree_pops: Dict[str, int]

    while True:
        counter: int = 0
        while True:
            counter += 1
            if counter > attempts_per_seed:
                raise Exception(f"Too many attempts for seed ({seed})")
                # The random seed is updated after each call,
                # so the process should eventually succeed.

            # Calculate the population yet to be assigned.
            remaining_population = sum(populations[node.id] for node in remainder.nodes)
            if remaining_population < target_population * 1.5:  # hack
                break

            # Get a spanning tree.
            spanning: Tree = RandomTree(remainder)
            spanning.compute_weight()
            cuts: list[Tree] = spanning.all_subtrees()

            # Sort the cuts by their deviation from the target population, and
            # then filter out the ones that wouldn't yield 'roughly equal' population.
            ranked: List[Tree] = sorted(
                cuts,
                key=lambda x: abs(x.subtree_weight - target_population)
                / target_population,
            )
            ranked = [
                n
                for n in ranked
                if abs(n.subtree_weight - target_population) / target_population
                < roughly_equal
            ]
            if not ranked:
                continue

            # Choose one of the candidate cuts at random.
            random_i = random.randint(0, 20)
            if random_i >= len(ranked):
                continue
            cut: Tree = ranked[random_i]

            # If the deviation of the district would be too large, try again.
            deviation = abs(cut.subtree_weight - target_population) / target_population
            if deviation > roughly_equal:
                continue

            # If the deviation of the remaining population would be too large, try again.
            deviation = (
                abs(
                    (remaining_population - cut.subtree_weight) / (N - district)
                    - target_population
                )
                / target_population
            )
            if deviation > roughly_equal:
                continue

            # The cut is good ...

            # Assign the GEOIDs in the chosen cut to the current district.
            assign_district(cut, district, assignments)

            # Increment the district, partition the graph, and repeat.
            district += 1
            _, remainder = partition(spanning, cut)

        # Must handle the last district, which may have a bad size.
        assert (
            abs(remaining_population - target_population)
        ) / target_population < roughly_equal
        cut: Tree = RandomTree(remainder)
        assign_district(cut, district, assignments)
        break

    # note that this may not generate N districts due to spanning tree issues.
    n_assigned: int = len(set(assignments.values()))
    if n_assigned != N:
        raise Exception(
            f"Failed to generate {N} districts. Only generated {len(assignments.values())}."
        )

    # Convert the assignments (dict) into a plan.
    plan: List[Assignment] = [
        Assignment(geoid=geoid, district=district)  # districts 1-N
        for geoid, district in assignments.items()
    ]

    return plan


def mkGraph(adjacencies: List[Tuple[str, str]], populations: Dict[str, int]):
    nodes: Dict[str, Node] = {
        geoid: Node(geoid, populations[geoid], set()) for geoid in populations.keys()
    }
    for a, b in adjacencies:
        nodes[a].neighbors.add(nodes[b])
        nodes[b].neighbors.add(nodes[a])
    graph: Graph = Graph(frozenset(nodes.values()))
    return graph


def partition(root: Tree, cut: Tree) -> tuple[Graph, Graph]:
    remainder_nodes: set[Node] = set(c.node for c in root.all_subtrees_above(cut))
    cleaved_nodes: set[Node] = set(c.node for c in cut.all_subtrees())
    remainder: Graph = mkSubsetGraph(remainder_nodes)
    cleaved: Graph = mkSubsetGraph(cleaved_nodes)
    assert len(remainder.nodes) + len(cleaved.nodes) == root.nodecount()
    return cleaved, remainder


def assign_district(cut: Tree, district: int, assignments: Dict[str, int]):
    assert cut.node.id not in assignments
    assignments[cut.node.id] = district
    for child in cut.children:
        assign_district(child, district, assignments)


### END ###
