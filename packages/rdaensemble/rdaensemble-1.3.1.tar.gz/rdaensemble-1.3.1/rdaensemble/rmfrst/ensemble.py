"""
GENERATE AN ENSEMBLE OF RANDOM MAPS from RANDOM SPANNING TREES (RMfRST)
"""

from typing import List, Dict, Tuple

from rdabase import (
    mkAdjacencies,
    populations,
    total_population,
    Graph,
    Assignment,
    calc_population_deviation,
)

from .random_map import random_map


def gen_rmfrst_ensemble(
    size: int,  # Number of random maps to generate
    seed: int,  # Starting random seed
    data: Dict[str, Dict[str, int | str]],
    graph: Dict[str, List[str]],
    N: int,  # Number of districts
    logfile,
    *,
    roughly_equal: float = 0.02,
) -> List[Dict[str, str | float | Dict[str, int | str]]]:
    """Generate an ensemble of random maps from random spanning trees."""

    start: int = seed
    plans: List[Dict[str, str | float | Dict[str, int | str]]] = list()

    pairs: List[Tuple[str, str]] = mkAdjacencies(Graph(graph))

    pop_by_geoid: Dict[str, int] = populations(data)
    total_pop: int = total_population(pop_by_geoid)

    conforming_count: int = 0

    while True:
        print(f"... {conforming_count} ...")
        print(
            f"Conforming count: {conforming_count}, random seed: {seed}", file=logfile
        )

        plan_name: str = f"{conforming_count:03d}_{seed}"

        try:
            assignments: List[Assignment] = random_map(
                pairs,
                pop_by_geoid,
                N,
                seed,
            )  # Generate a random contiguous & 'roughly' equal population partitioning of the state.

            popdev: float = calc_population_deviation(
                assignments, pop_by_geoid, total_pop, N
            )

            if popdev > roughly_equal:
                continue

            conforming_count += 1
            plan: Dict[str, int | str] = {a.geoid: a.district for a in assignments}
            plans.append({"name": plan_name, "plan": plan})  # No weights.

            if conforming_count == size:
                break

        except Exception as e:
            print(f"Failure: {e}", file=logfile)
            pass

        finally:
            seed += 1

    print(
        f"{conforming_count} conforming plans took {seed - start + 1} random seeds.",
        file=logfile,
    )

    return plans


### END ###
