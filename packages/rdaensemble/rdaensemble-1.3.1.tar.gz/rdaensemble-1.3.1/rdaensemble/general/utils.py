"""
MISCELLANEOUS UTILITIES
"""

from typing import Any, Dict, List

from rdabase import Assignment


def make_plan(assignments: Dict[str, int | str]) -> List[Assignment]:
    """Convert a dict of geoid: district assignments to a list of Assignments."""

    plan: List[Assignment] = [
        Assignment(geoid, district) for geoid, district in assignments.items()
    ]
    return plan


def plan_from_ensemble(
    plan_name: str, ensemble: Dict[str, Any]
) -> Dict[str, str | float | Dict[str, int | str]]:
    """Return the named plan from an ensemble."""

    plans: List[Dict[str, str | float | Dict[str, int | str]]] = ensemble["plans"]
    for p in plans:
        if p["name"] == plan_name:
            return p
    raise ValueError(f"Plan {plan_name} not found in ensemble")


### END ###
