import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from methods import *
from classes.FitchProof import *
from taskA.classes.FormulaAST import *

# Task B.2 Test cases
step1 = Step(line=1, formula=Implies(Atom("A"), Atom("C")), rule=Rule.PREMISE, references=[], level=0)
step2 = Step(line=2, formula=Implies(Atom("B"), Atom("C")), rule=Rule.PREMISE, references=[], level=0)
step3 = Step(line=3, formula=Or(Atom("A"), Atom("B")), rule=Rule.PREMISE, references=[], level=0)
step4 = Step(line=4, formula=Atom("A"), rule=Rule.ASSUMPTION, references=[], level=1)
step5 = Step(line=5, formula=Atom("C"), rule=Rule.IMPLIES_ELIM, references=[1, 4], level=1)
step6 = Step(line=6, formula=Atom("B"), rule=Rule.ASSUMPTION, references=[], level=1)
step7 = Step(line=7, formula=Atom("C"), rule=Rule.IMPLIES_ELIM, references=[2, 6], level=1)
step8 = Step(line=8, formula=Atom("C"), rule=Rule.OR_ELIM, references=[3, 4, 5, 6, 7], level=0)

proof = Proof(steps=[step1, step2, step3, step4, step5, step6, step7, step8])

print(check_proof(proof))