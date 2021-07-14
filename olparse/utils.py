from pathlib import Path
from typing import Set


def get_project_root() -> Path:
    return Path(__file__).parent.parent.resolve()


def load_laws() -> Set:
    with (get_project_root() / "resource" / "laws.txt").open(
        "r", encoding="utf-8"
    ) as r:
        laws = {x.strip() for x in r}
    return laws
