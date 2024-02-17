"""
ENSEMBLE & SCORES METADATA
"""

from typing import Any, Dict

import os, pwd, datetime
from importlib.metadata import version

from rdabase import cycle, plan_type


def shared_metadata(
    xx: str,
    repo: str,
) -> Dict[str, Any]:
    """Create the shared metadata for ensembles and scores."""

    shared: Dict[str, Any] = dict()

    shared["username"] = pwd.getpwuid(os.getuid()).pw_name

    timestamp = datetime.datetime.now()
    shared["date_created"] = timestamp.strftime("%x")
    shared["time_created"] = timestamp.strftime("%X")

    shared["repository"] = repo

    shared["state"] = xx
    shared["cycle"] = cycle
    shared["plan_type"] = plan_type
    shared["units"] = "VTD"

    return shared


def ensemble_metadata(
    *,
    xx: str,
    ndistricts: int,
    size: int,
    method: str,
    repo: str = "rdatools/rdaensemble",
) -> Dict[str, Any]:
    """Create the metadata for an ensemble."""

    ensemble: Dict[str, Any] = shared_metadata(xx, repo)

    ensemble["ndistricts"] = ndistricts
    ensemble["method"] = method
    ensemble["size"] = size

    return ensemble


def scores_metadata(
    *,
    xx: str,
    plans: str,
    repo: str = "rdatools/rdaensemble",
) -> Dict[str, Any]:
    """Create the metadata for ensemble scores."""

    scores: Dict[str, Any] = shared_metadata(xx, repo)

    head, tail = os.path.split(plans)
    scores["plans"] = tail
    scores["rdascore"] = version("rdascore")

    return scores


### END ###
