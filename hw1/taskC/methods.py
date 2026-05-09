import random
import time
from taskA.classes.FormulaAST import *
from taskA.methods import *
import z3
import matplotlib.pyplot as plt

def validate_config(constraints: list[Operand], config: dict[str, bool]) -> bool:
    return all(eval(c, config) for c in constraints)

def find_valid_configs(constraints: list[Operand]) -> list[dict[str, bool]]:
    atoms = []
    for c in constraints:
        atoms.extend(extract_atoms(c))
    atoms = list(set(atoms))

    valid_configs = []
    for values in product([False, True], repeat=len(atoms)):
        config = dict(zip(atoms, values))
        if validate_config(constraints, config):
            valid_configs.append(config)
    return valid_configs

def explain_conflict(constraints: list[Operand], config: dict[str, bool]) -> tuple[list[Operand], dict[str, int]]:
    conflicting = []
    for c in constraints:
        if not eval(c, config):
            conflicting.append(c)
    
    valid_configs = find_valid_configs(constraints)
    atoms = []
    for c in constraints:
        atoms.extend(extract_atoms(c))
    atoms = list(set(atoms))

    most_similar_config = {}
    min_diff = float('inf')
    for valid_config in valid_configs:
        count_diff = sum([1 for atom in atoms if config[atom] != valid_config[atom]])
        if count_diff < min_diff:
            min_diff = count_diff
            most_similar_config = valid_config
    return conflicting, most_similar_config

def to_z3(f: Operand, z3_vars: dict[str, z3.BoolRef]) -> z3.BoolRef:
    if isinstance(f, Atom):
        return z3_vars[f.name]
    if isinstance(f, TrueConst):
        return z3.BoolVal(True)
    if isinstance(f, FalseConst):
        return z3.BoolVal(False)
    if isinstance(f, Not):
        return z3.Not(to_z3(f.operand, z3_vars))
    if isinstance(f, And):
        return z3.And(to_z3(f.left, z3_vars), to_z3(f.right, z3_vars))
    if isinstance(f, Or):
        return z3.Or(to_z3(f.left, z3_vars), to_z3(f.right, z3_vars))
    if isinstance(f, Implies):
        return z3.Implies(to_z3(f.left, z3_vars), to_z3(f.right, z3_vars))
    if isinstance(f, Iff):
        l = to_z3(f.left, z3_vars)
        r = to_z3(f.right, z3_vars)
        return z3.And(z3.Implies(l, r), z3.Implies(r, l))
    raise ValueError(f"Unknown formula type: {type(f)}")


def z3_solve(formula: Operand) -> tuple[str, dict[str, bool] | None]:
    atoms = list(set(extract_atoms(formula)))
    
    z3_vars = {name: z3.Bool(name) for name in atoms}
    
    z3_expr = to_z3(formula, z3_vars)
    
    solver = z3.Solver()
    solver.add(z3_expr)
    
    if solver.check() == z3.sat:
        model = solver.model()
        assignment = {}
        for name in atoms:
            val = model.eval(z3_vars[name], model_completion=True)
            assignment[name] = bool(val)
        return "SAT", assignment
    else:
        return "UNSAT", None
    
def generate_random_cnf(count_atoms: int, clauses_length: int, clauses_count: int) -> Operand:
    atoms = [Atom(f"A{i}") for i in range(count_atoms)]
    clauses = []
    for i in range(clauses_count):
        random_atoms = random.choices(atoms, k=clauses_length)
        random_atoms = [Not(atom) if random.random() < 0.5 else atom for atom in random_atoms]
        clause = random_atoms[0]
        for atom in random_atoms[1:]:
            clause = Or(clause, atom)
        clauses.append(clause)
    and_clauses = clauses[0]
    for clause in clauses[1:]:
        and_clauses = And(and_clauses, clause)
    return and_clauses

def truth_table_z3(formula: Operand) -> TruthTable:
    atoms = sorted(extract_atoms(formula))
    z3_vars = {name: z3.Bool(name) for name in atoms}

    solver = z3.Solver()
    table = []

    for values in product([False, True], repeat=len(atoms)):
        interpretation = dict(zip(atoms, values))
        for atom, value in interpretation.items():
            solver.add(z3_vars[atom] == value)
        solver.push()
        result = solver.check() == z3.sat
        table.append((interpretation, result))
        solver.pop()

    return TruthTable(atoms, table, to_string(formula))

def compare_truth_table_perfomance(formula: Operand):
    z0 = time.perf_counter()
    tt = truth_table(formula)
    z1 = time.perf_counter()
    truth_table_time = z1 - z0

    z0 = time.perf_counter()
    tt_z3 = truth_table_z3(formula)
    z1 = time.perf_counter()
    truth_table_z3_time = z1 - z0

    print(f"Truth table time: {truth_table_time}")
    print(f"Truth table time (Z3): {truth_table_z3_time}")

def compare_sat_perfomance(formula: Operand):
    z0 = time.perf_counter()
    tt = is_satisfiable(formula)
    z1 = time.perf_counter()
    is_satisfiable_time = z1 - z0

    z0 = time.perf_counter()
    z3_solve(formula)
    z1 = time.perf_counter()
    z3_solve_time = z1 - z0

    print(f"Is SAT time: {is_satisfiable_time}")
    print(f"Is SAT (Z3) time: {z3_solve_time}")

def plot_satisfiability_ratio():    
    atoms_counts = [10, 25, 50, 100]
    ratio_steps = range(20, 70)
    trials = 10

    results = {}

    for n in atoms_counts:
        probs = []

        for r in ratio_steps:
            ratio = r / 10.0
            clauses_count = int(n * ratio)
            sat_count = 0

            for _ in range(trials):
                formula = generate_random_cnf(n, clauses_length=3, clauses_count=clauses_count)
                res, _ = z3_solve(formula)
                if res == "SAT":
                    sat_count += 1

            probs.append(sat_count / trials)

        results[n] = probs

    plt.figure(figsize=(10, 6))
    colors = ['blue', 'green', 'orange', 'purple']

    for i, n in enumerate(atoms_counts):
        ratios = [r / 10.0 for r in ratio_steps]
        plt.plot(ratios, results[n], marker='o', markersize=3, 
                 label=f'n = {n}', color=colors[i % len(colors)])

    plt.axvline(x=4.26, color='red', linestyle='--', linewidth=1, 
                label=r'Теоретический порог $\alpha$ ( ≈ 4.26)')

    plt.xlabel(r"Ratio $\alpha$")
    plt.ylabel("Probability of SAT")
    plt.title("Phase Transition in Random 3-SAT")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig('satisfiability_ratio.png', dpi=300, bbox_inches='tight')
    plt.show()
