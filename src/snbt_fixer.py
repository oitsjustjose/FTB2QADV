"""
AUTHOR: Jose Stovall | oitsjustjose@git
LICENSE: MIT
"""

from typing import Any, Dict

import nbtlib
import snbtlib


def get_fixed_snbt_dict(file_path: str) -> Dict[str, Any]:
    """
    FTB Quests doesn't properly use Commas when saving their SNBT (idiots)
    This script properly inserts them again
    """

    with open(file_path, "r", encoding="utf-8") as f_handle:
        data = f_handle.readlines()
    # Iterate over all rows, checking to see if a comma might go here
    # This will place excess commas in cases of ]}, }], etc. Clean up later
    for idx, row in enumerate(data):
        clean = row.replace("\n", "").replace("\t", "")
        if clean.endswith("{") or clean.endswith("["):
            continue
        data[idx] = f"{clean},"

    as_str = " ".join(data)
    as_str = as_str.replace("], ", "],")
    as_str = as_str.replace("}, ", "},")
    for sym1 in ["}", "]"]:
        for sym2 in ["}", "]"]:
            as_str = as_str.replace(f"{sym1},{sym2}", f"{sym1}{sym2}")
    as_str = as_str[: len(as_str) - 1]

    snbt = snbtlib.loads(as_str)
    snbt: Dict[str, Any] = snbt
    return snbt
