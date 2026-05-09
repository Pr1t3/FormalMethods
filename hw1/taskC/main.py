import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from taskA.classes.FormulaAST import *
from methods import *

# Task C.1 Test cases
P = Atom("P")
D = Atom("D")
L = Atom("L")
S = Atom("S")

constraints = [
    Implies(P, S),
    Implies(D, L),
    Not(And(S, D)),
    And(Or(P, D), Not(And(P, D))),
    Implies(Not(L), Not(D))
]

config = {"P": True, "D": False, "L": True, "S": False}

print(validate_config(constraints, config))

print(find_valid_configs(constraints))

print(explain_conflict(constraints, config))

# Task C.2 Test cases
print(z3_solve(And(P, Not(P)))) # UNSAT
print(z3_solve(And(P, D))) # SAT

compare_truth_table_perfomance(generate_random_cnf(10, 3, 42)) # My - ~0.012, Z3 - ~0.582

atoms_count = 20
ratio = 4.26
clauses_count = int(atoms_count * ratio)
# compare_sat_perfomance(generate_random_cnf(atoms_count, 3, clauses_count)) # My >>> Z3

plot_satisfiability_ratio()