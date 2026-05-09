import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from methods import *

# Task A.2 Test cases
formulaAst = Or(Implies(And(Atom('p'), Atom('q')), Atom('r')), And(Not(Atom('p')), Atom('s')))
print(to_string(formulaAst)) # (p ∧ q → r) ∨ ¬p ∧ s

print(parse(to_string(formulaAst)) == formulaAst) # True

# Task A.3 Test cases
formula = parse("(p ∧ q → r) ∨ ¬p ∧ s")
print(eval(formula, {'p': True, 'q': True, 'r': False, 's': True})) # False

print(truth_table(formula))

print(is_tautology(parse("p ∨ ¬p"))) # True
print(is_tautology(parse("p ∧ ¬p"))) # False

print(is_satisfiable(parse("p ∨ ¬p"))) # True
print(is_satisfiable(parse("p ∧ ¬p"))) # False

print(is_contradiction(parse("p ∨ ¬p"))) # False
print(is_contradiction(parse("p ∧ ¬p"))) # True

# Task A.4 Test cases
formula = parse("¬(p ∨ q) → (¬p ∧ ¬q)")
nnf_formula = to_nnf(formula)
print(to_string(nnf_formula)) # (p ∨ q) ∨ (¬p ∧ ¬q) 

formula = parse("p → (q ∧ r)")
cnf_formula = to_cnf(formula)
print(to_string(cnf_formula)) # (¬p ∨ q) ∧ (¬p ∨ r)

formula1 = parse("¬(p ∧ q)")
formula2 = parse("¬p ∨ ¬q")
print(equivalent(formula1, formula2)) # True

formula1 = parse("¬(p ∨ q)")
formula2 = parse("¬p ∧ ¬q")
print(equivalent(formula1, formula2)) # True

formula1 = parse("p ∧ (q ∨ r)")
formula2 = parse("(p ∧ q) ∨ (p ∧ r)")
print(equivalent(formula1, formula2)) # True