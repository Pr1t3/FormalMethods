def unit_propagate(clauses: list[list[int]], assignment: dict[int, bool]) -> tuple[list[list[int]], dict[int, bool]] | None:
    unit = None
    for clause in clauses:
        if len(clause) == 1:
            unit = clause[0]
            break
    if unit is None:
        return clauses, assignment

    assignment[abs(unit)] = unit > 0

    new_clauses = []
    for clause in clauses:
        if unit in clause:
            continue
        if -unit in clause:
            simplified = [lit for lit in clause if lit != -unit]
            if not simplified:
                return None, None
            new_clauses.append(simplified)
        else:
            new_clauses.append(clause)

    return unit_propagate(new_clauses, assignment)


def pure_literal_assign(clauses: list[list[int]], assignment: dict[int, bool]) -> tuple[list[list[int]], dict[int, bool]] | None:
    literals = set()
    for clause in clauses:
        for lit in clause:
            literals.add(lit)
    pure_literals = set()
    for lit in literals:
        if -lit not in literals:
            pure_literals.add(lit)
    if not pure_literals:
        return clauses, assignment

    for lit in pure_literals:
        assignment[abs(lit)] = lit > 0

    new_clauses = []
    for clause in clauses:
        if any(lit in clause for lit in pure_literals):
            continue
        new_clause = [lit for lit in clause if -lit not in pure_literals]
        new_clauses.append(new_clause)

    return pure_literal_assign(new_clauses, assignment)


def recursive_dpll(clauses: list[list[int]], assignment: dict[int, bool]) -> dict[int, bool] | None:
    clauses, assignment = unit_propagate(clauses, assignment)
    if clauses is None:
        return None
    if len(clauses) == 0:
        return assignment

    clauses, assignment = pure_literal_assign(clauses, assignment)
    if clauses is None:
        return None
    if len(clauses) == 0:
        return assignment

    all_vars = {abs(lit) for c in clauses for lit in c}
    variable = None
    for v in all_vars:
        if v not in assignment:
            variable = v
            break
    if variable is None:
        return assignment

    new_assignment = assignment.copy()
    new_assignment[variable] = True
    new_clauses = []
    for clause in clauses:
        if variable in clause:
            continue
        new_clause = [lit for lit in clause if lit != -variable]
        new_clauses.append(new_clause)
    result = recursive_dpll(new_clauses, new_assignment)
    if result is not None:
        return result

    new_assignment = assignment.copy()
    new_assignment[variable] = False
    new_clauses = []
    for clause in clauses:
        if -variable in clause:
            continue
        new_clause = [lit for lit in clause if lit != variable]
        new_clauses.append(new_clause)
    return recursive_dpll(new_clauses, new_assignment)


def dpll(clauses: list[list[int]]) -> dict[int, bool] | None:
    return recursive_dpll(clauses, {})

def parse_dimacs(dimacs_content: str) -> list[list[int]]:
    clauses = []
    for line in dimacs_content.split('\n'):
        line = line.strip()
        if line.startswith('c') or line.startswith('p') or not line:
            continue
        if line:
            clause = list(map(int, line.split()[:-1]))
            clauses.append(clause)
    return clauses