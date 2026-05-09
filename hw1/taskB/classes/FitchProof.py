from taskA.classes.FormulaAST import Operand
from dataclasses import dataclass
from enum import Enum

class Rule(Enum):
    def __init__(self, display_name, num_refs):
        self.display_name = display_name
        self.num_refs = num_refs

    PREMISE = ("Premise", 0)
    ASSUMPTION = ("Assumption", 0)
    AND_INTRO = ("∧i", 2)
    AND_ELIM = ("∧e", 1)
    OR_INTRO = ("∨i", 1)
    OR_ELIM = ("∨e", 5)
    IMPLIES_INTRO = ("→i", 2)
    IMPLIES_ELIM = ("→e", 2)
    NOT_INTRO = ("¬i", 2)
    NOT_ELIM = ("¬e", 2)
    BOTTOM_ELIM = ("⊥e", 1)


@dataclass(frozen=True)
class Step:
    line: int
    formula: Operand
    rule: Rule
    references: list[int]
    level: int

@dataclass(frozen=True)
class Proof:
    steps: list[Step]

