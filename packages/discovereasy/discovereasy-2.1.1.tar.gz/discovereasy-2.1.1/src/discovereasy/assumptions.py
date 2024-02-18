from typing_extensions import Annotated
from pathlib import Path
from enum import Enum
from yaml import safe_load
import typer

from .types import Node, NodeKind


class Assumption(Node):
    risk: float = 0.0
    evidence: float = 0.0
    risk_normalized: float = 0.0
    evidence_normalized: float = 0.0


class Dimension(str, Enum):
    risk = 'risk'
    evidence = 'evidence'


def main(
    files: list[Path], count: Annotated[int, typer.Option('--count', '-n')] = 5
):
    assumptions = sum(
        [
            [
                Assumption(id=name, **item)
                for name, item in safe_load(f.read_text()).items()
                if item.get('kind') == NodeKind.assumption.value
            ]
            for f in files
        ],
        start=[],
    )

    assumptions = normalize_evidence(normalize_risks(assumptions))

    for i, assumption in enumerate(
        sorted(
            assumptions,
            key=lambda a: -a.risk_normalized + a.evidence_normalized,
        )
    ):
        print(format(assumption))
        if i > count:
            break


def format(assumption: Assumption):
    return f'{assumption.id:8s}: {assumption.desc}  (risk: {assumption.risk}, evidence: {assumption.evidence})'  # noqa: E501


def normalize_risks(assumptions: list[Assumption]) -> list[Assumption]:
    return normalize(assumptions, dim=Dimension.risk)


def normalize_evidence(assumptions: list[Assumption]) -> list[Assumption]:
    return normalize(assumptions, dim=Dimension.evidence)


def normalize(
    assumptions: list[Assumption], dim: Dimension
) -> list[Assumption]:
    vals = [getattr(a, dim.value) for a in assumptions]
    mini = min(vals)
    maxi = max(vals)
    for a in assumptions:
        setattr(
            a,
            dim.value + '_normalized',
            transform(getattr(a, dim.value), mini, maxi),
        )
    return assumptions


def transform(val: float, mini: float, maxi: float) -> float:
    return 2 * (val - mini) / (maxi - mini + 1e-4) - 1
