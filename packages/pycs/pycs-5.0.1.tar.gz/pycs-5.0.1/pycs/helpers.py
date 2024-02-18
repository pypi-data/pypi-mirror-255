from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .node import CN


def get_output_dir(cfg: CN, *, mkdir=True, base_dir=Path("output")) -> Path:
    output_dir = base_dir / cfg.NAME
    if mkdir:
        output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _get_output_dir_cli() -> None:
    parser = argparse.ArgumentParser("Get output dir for cfg", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("cfg_path", type=Path)
    parser.add_argument("--mkdir", action="store_true", help="Will create the directory if it doesn't exist")
    parser.add_argument("--base-dir", type=Path, default=Path("output"), help="Base directory for all output dirs")
    args = parser.parse_args()

    cfg = CN.load(args.cfg_path)
    dir_ = get_output_dir(cfg, mkdir=args.mkdir, base_dir=args.base_dir)
    sys.stdout.write(str(dir_))
