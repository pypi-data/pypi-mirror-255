#!/usr/bin/env python3

import argparse
import pandas as pd

from dataclasses import dataclass
from pandas._typing import Dtype
from pathlib import Path

from .config import Config

type QList = pd.DataFrame
type Encounters = pd.DataFrame


def analysis_results_name(out_dir: Path, args: argparse.Namespace, analysis_type: str):
    return out_dir / f'{args.taskfile.stem}-{analysis_type}.csv'


def enc_dtypes() -> dict[str, Dtype]:
    direction = pd.CategoricalDtype(categories=['b', 'f'])
    phase = pd.CategoricalDtype(categories=['ad', 'init', 'juv', 'sub', 'term'])
    return {
        'significant_size': 'bool',
        'direction': direction,
        'phase': phase,
        'ref': 'Int64',
    }


def data_dir(cfg: Config) -> Path:
    return Path(cfg.get_string('out-dir', './results'))


@dataclass(frozen=True)
class Sides:
    """Represents side lengths of quadrats"""

    x: float
    y: float
