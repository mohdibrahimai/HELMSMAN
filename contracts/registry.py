"""Helpers for loading contract definitions from disk.

Contracts are stored in YAML files within a directory. This module
provides a simple loader that walks a directory tree, parses each YAML
file and instantiates a `Contract` object using the Pydantic models.

The loader silently ignores files that cannot be parsed as YAML or do
not conform to the contract schema. Any validation errors will be
propagated to the caller. Duplicate contract IDs are allowed but
override earlier definitions; the last one wins.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml
from pydantic import ValidationError

from .schemas import Contract


def _find_yaml_files(root: Path) -> Iterable[Path]:
    """Yield all YAML files under the given directory.

    This function traverses the directory tree and yields files with
    extension `.yml` or `.yaml`. Non-existing directories are ignored.
    """
    if not root.exists() or not root.is_dir():
        return
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith(('.yaml', '.yml')):
                yield Path(dirpath) / name


def load_contracts(directory: str) -> Dict[str, Contract]:
    """Load all contracts from YAML files in the given directory.

    :param directory: path to a directory containing contract YAML files
    :returns: mapping from contract id to Contract object
    :raises ValidationError: if any contract file is malformed
    """
    root = Path(directory)
    contracts: Dict[str, Contract] = {}
    for path in _find_yaml_files(root):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            if data is None:
                continue
            contract = Contract(**data)
            contracts[contract.id] = contract
        except ValidationError as ve:
            raise ve
        except Exception:
            # Ignore files that can't be parsed as valid contracts
            continue
    return contracts