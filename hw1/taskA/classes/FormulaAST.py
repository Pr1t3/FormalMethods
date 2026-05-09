from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Operand:
    precedence: ClassVar[int] = 0

@dataclass(frozen=True)
class Atom(Operand):
    name: str
    precedence: ClassVar[int] = 6

@dataclass(frozen=True)
class Not(Operand):
    operand: Operand
    precedence: ClassVar[int] = 5

@dataclass(frozen=True)
class And(Operand):
    left: Operand
    right: Operand
    precedence: ClassVar[int] = 4
@dataclass(frozen=True)
class Or(Operand):
    left: Operand
    right: Operand
    precedence: ClassVar[int] = 3

@dataclass(frozen=True)
class Implies(Operand):
    left: Operand
    right: Operand
    precedence: ClassVar[int] = 2


@dataclass(frozen=True)
class Iff(Operand):
    left: Operand
    right: Operand
    precedence: ClassVar[int] = 1

@dataclass(frozen=True)
class TrueConst(Operand):
    precedence: ClassVar[int] = 6

@dataclass(frozen=True)
class FalseConst(Operand):
    precedence: ClassVar[int] = 6