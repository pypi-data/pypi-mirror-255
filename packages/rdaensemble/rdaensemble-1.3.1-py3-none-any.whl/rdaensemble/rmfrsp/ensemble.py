"""
GENERATE AN ENSEMBLE OF RANDOM MAPS from RANDOM STARTING POINTS (RMfRSP)
"""

from typing import Any, List, Dict, Tuple

from rdabase import (
    mkPoints,
    mkAdjacencies,
    populations,
    total_population,
    Graph,
    Point,
    Assignment,
    load_plan,
    IndexedWeightedAssignment,
    index_geoids,
    index_assignments,
)
from rdadccvt import (
    file_list,
    clean,
    dccvt_randomsites,
    dccvt_initial,
    dccvt_points,
    dccvt_adjacencies,
    dccvt_balzer1,
    dccvt_contiguous,
    dccvt_balzer2,
    dccvt_consolidated,
    dccvt_complete,
    dccvt_output,
    index_points_file,
    index_pairs_file,
    randomsites,
    initial,
    mk_contiguous,
    balzer_go,
    consolidate,
    complete,
    postprocess,
    calc_energy_file,
    calc_population_deviation_file,
    write_redistricting_points,
    write_assignments,
)


def gen_rmfrsp_ensemble(
    size: int,  # Number of random maps to generate
    seed: int,  # Starting random seed
    data: Dict[str, Dict[str, int | str]],
    shapes: Dict[str, Any],
    graph: Dict[str, List[str]],
    N: int,  # Number of districts
    logfile,
    *,
    roughly_equal: float = 0.02,
    verbose: bool = False,
) -> List[Dict[str, str | float | Dict[str, int | str]]]:
    """Generate an ensemble of random maps from random starting points."""

    start: int = seed
    plans: List[Dict[str, str | float | Dict[str, int | str]]] = list()

    points: List[Point] = mkPoints(data, shapes)
    pairs: List[Tuple[str, str]] = mkAdjacencies(Graph(graph))

    temp_points: str = "temp/NC_2020_points.csv"
    write_redistricting_points(points, temp_points)

    index_points_file(points, dccvt_points, verbose=verbose)
    index_pairs_file(points, pairs, dccvt_adjacencies, verbose=verbose)

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
            randomsites(dccvt_points, dccvt_randomsites, N, seed)
            initial(dccvt_randomsites, dccvt_points, dccvt_initial)
            balzer_go(
                dccvt_points,
                None,  # NOTE - No adjacencies for the initial run.
                dccvt_initial,
                dccvt_balzer1,
                balance=False,
            )  # Run Balzer's algorithm (DCCVT) to get balanced but not contiguous assignments.
            mk_contiguous(dccvt_balzer1, dccvt_adjacencies, dccvt_contiguous)
            balzer_go(
                dccvt_points,
                dccvt_adjacencies,
                dccvt_contiguous,
                dccvt_balzer2,
                balance=True,
            )  # Run Balzer's algorithm again to get balanced & contiguous assignments.
            consolidate(
                dccvt_balzer2,
                dccvt_adjacencies,
                plan_name,
                dccvt_consolidated,
                verbose=verbose,
            )
            complete(
                dccvt_consolidated,
                dccvt_adjacencies,
                dccvt_points,
                dccvt_complete,
                verbose=verbose,
            )
            postprocess(dccvt_complete, temp_points, dccvt_output, verbose=verbose)

            popdev: float = calc_population_deviation_file(
                dccvt_output, pop_by_geoid, total_pop, N
            )

            if popdev > roughly_equal:
                continue

            conforming_count += 1
            assignments: List[Assignment] = load_plan(dccvt_output)
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
