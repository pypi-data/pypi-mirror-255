from typing import Callable, Iterator
from typing_extensions import Annotated
import textwrap
from jinja2 import PackageLoader, Environment
from yaml import safe_load
import typer
from .types import Node, NodeKind, NodeFocus


class NoNodes(Exception):
    pass


def is_descendent(node: Node, of: Node, ref: dict[str, Node]) -> bool:
    if node.parent == of.id or node.id == of.id:
        return True
    elif node.parent == 'root':
        return False
    else:
        return is_descendent(ref[node.parent], of=of, ref=ref)


def filter_desc(
    nodes: dict[str, Node], predicate: Callable[[Node], bool]
) -> dict[str, Node]:
    with_pred = list(filter_pred(nodes, predicate).values())
    return {
        n.id: n
        for n in nodes.values()
        if any(is_descendent(n, of=m, ref=nodes) for m in with_pred)
    }


def filter_no_desc(
    nodes: dict[str, Node], predicate: Callable[[Node], bool]
) -> dict[str, Node]:
    with_pred = list(filter_pred(nodes, predicate).values())
    return {
        n.id: n
        for n in nodes.values()
        if not any(is_descendent(n, of=m, ref=nodes) for m in with_pred)
    }


def filter_branches(nodes: dict[str, Node], predicate: Callable[[Node], bool]):
    keep, drop = [], []
    for n in nodes.values():
        if predicate(n):
            keep.append(n.id)
        else:
            drop.append(n.id)

    for _ in range(len(keep)):
        keep2 = []
        for idx in keep:
            n = nodes[idx]
            if n.parent in drop:
                drop.append(n.id)
            else:
                keep2.append(n.id)
        keep = keep2
        if len(keep) == 0:
            break
    return {idx: nodes[idx] for idx in keep}


def filter_pred(
    nodes: dict[str, Node], predicate: Callable[[Node], bool]
) -> dict[str, Node]:
    return {n.id: n for n in nodes.values() if predicate(n)}


def is_opportunity(n: Node) -> bool:
    return n.kind == NodeKind.opportunity


def is_solution(n: Node) -> bool:
    return n.kind == NodeKind.solution


def is_assumption(n: Node) -> bool:
    return n.kind == NodeKind.assumption


def has_prior_at_least(prio: int) -> Callable[[Node], bool]:
    def p(n: Node) -> bool:
        return n.prio >= prio

    return p


def children(of: Node, nodes: Iterator[Node]) -> Iterator[Node]:
    return (n for n in nodes if n.parent == of.id)


def risk_and_evidence(nodes: Iterator[Node]) -> float | None:
    has_assumptions = False
    total = 0.0
    for node in nodes:
        if node.kind == NodeKind.assumption:
            if node.risk is None or node.evidence is None:
                raise ValueError(
                    'Assumption nodes must have risk and evidence,'
                    f' but node {node.id} has not.'
                )
            total += node.risk - node.evidence
            has_assumptions = True
    if has_assumptions:
        return total
    else:
        return None


def project_back_risk_and_evidence(nodes: dict[str, Node]) -> dict[str, Node]:
    for key, node in nodes.items():
        if node.kind == NodeKind.solution:
            node.okness = risk_and_evidence(
                children(node, iter(nodes.values()))
            )
    return nodes


def main(
    filenames: list[str],
    opportunities: Annotated[
        bool, typer.Option('--opportunities', '-o')
    ] = False,
    solutions: Annotated[bool, typer.Option('--solutions', '-s')] = False,
    assumptions: Annotated[bool, typer.Option('--assumptions', '-a')] = False,
    priority: Annotated[int, typer.Option('--priority', '-p')] = 5,
    project_risk_and_evidence: Annotated[
        bool, typer.Option('--project-risk-and-evidence', '-r')
    ] = False,
):

    predicates = []
    if opportunities:
        predicates.append(is_opportunity)
    if solutions:
        predicates.append(is_solution)
    if assumptions:
        predicates.append(is_assumption)

    nodes = {}
    for filename in filenames:
        with open(filename) as f:
            nodes.update(
                {i: Node(id=i, **vals) for i, vals in safe_load(f).items()}
            )

    if any([n.focus == NodeFocus.focussed for n in nodes.values()]):
        nodes = filter_desc(nodes, lambda n: n.focus == NodeFocus.focussed)
    if any([n.focus == NodeFocus.hidden for n in nodes.values()]):
        nodes = filter_no_desc(nodes, lambda n: n.focus == NodeFocus.hidden)

    nodes = filter_branches(nodes, has_prior_at_least(priority))
    if not nodes:
        raise NoNodes(f'No nodes with priority >= {priority}')
    if predicates:
        nodes = filter_pred(nodes, lambda n: any([p(n) for p in predicates]))
        if not nodes:
            raise NoNodes(f'No nodes with {predicates}')

    if not assumptions and project_risk_and_evidence:
        nodes = project_back_risk_and_evidence(nodes)

    font = 'Helvetica,Arial,sans-serif'
    properties = ' '.join(['shape="Mrecord"'])
    styles = {
        NodeKind.opportunity: 'style="filled" fillcolor="#ffeeaa"',
        NodeKind.solution: 'style="filled" fillcolor="#aaffff"',
        NodeKind.assumption: 'styel="filled" fillcolor="#aaffaa"',
    }

    for node in nodes.values():
        node.desc = '<br/>'.join(textwrap.wrap(node.desc, width=40))
        if node.parent not in nodes:
            node.parent = 'root'

    env = Environment(loader=PackageLoader('discovereasy'))

    template = env.get_template('graphs.j2.dot')
    print(
        template.render(
            nodes=nodes.values(),
            fontspec=font,
            properties=properties,
            styles=styles,
        )
    )
