from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from Parser.token_type import TokenType

class Node:
    pass

@dataclass
class Var(Node):
    name: str

@dataclass
class Assign(Node):
    name: str
    value: Node

@dataclass
class BinOp(Node):
    op: TokenType
    left: Node
    right: Node
    pos: int

@dataclass
class Call(Node):
    name: str
    args: List[Node]
    pos: int

@dataclass
class Return(Node):
    value: Node
    pos: int

@dataclass
class Text(Node):
    value: str

@dataclass
class If(Node):
    label: Optional[str]
    condition: Node
    then_body: List[Node]
    else_body: Optional[List[Node]]

@dataclass
class While(Node):
    label: Optional[str]
    condition: Node
    body: List[Node]

@dataclass
class Loop(Node):
    label: Optional[str]
    body: List[Node]

@dataclass
class Break(Node):
    label: Optional[str]

@dataclass
class Continue(Node):
    label: Optional[str]
