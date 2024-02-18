from enum import Enum
from pydantic import BaseModel


class NodeKind(str, Enum):
    opportunity = 'opportunity'
    solution = 'solution'
    assumption = 'assumption'


class NodeFocus(str, Enum):
    focussed = 'focussed'
    hidden = 'hidden'
    neutral = 'neutral'


class Node(BaseModel):
    id: str
    desc: str
    parent: str = 'root'
    kind: NodeKind = NodeKind.opportunity
    prio: int = 5
    focus: NodeFocus = NodeFocus.neutral
    risk: float | None = None
    evidence: float | None = None
    # This would be the sum of the difference risk - evidence for all children
    okness: float | None = None
