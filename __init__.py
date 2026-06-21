# Root package shim for backwards compatibility.
# This file allows imports like `from map_loader import load_map_file` when
# `src` is on PYTHONPATH and the package is installed via `pip install -e .`.

from src.wiz_drive import *  # noqa: F401,F403
