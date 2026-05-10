def cdcl(clauses: list[list[int]]) -> dict[int, bool] | None:
    all_clauses = [c[:] for c in clauses]

    assignment = {}
    var_level = {}
    trail = []
    activity = {abs(lit): 0.0 for c in clauses for lit in c}
    current_level = 0

    while True:
        changed = True
        conflict_clause = None
        while changed:
            changed = False
            for clause in all_clauses:
                satisfied = False
                unassigned = []
                for lit in clause:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)

                if satisfied:
                    continue
                if not unassigned:
                    conflict_clause = clause
                    break
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    v = abs(lit)
                    assignment[v] = (lit > 0)
                    var_level[v] = current_level
                    trail.append((lit, current_level, clause))
                    changed = True
            if conflict_clause:
                break

        if conflict_clause and current_level == 0:
            return None

        if conflict_clause:
            conflict_lits = set(conflict_clause)

            while True:
                current_level_lits = [
                    l for l in conflict_lits
                    if var_level.get(abs(l), 0) == current_level
                ]
                if len(current_level_lits) <= 1:
                    break

                pivot = None
                for lit in current_level_lits:
                    for t_lit, _, reason in trail:
                        if t_lit == -lit and reason is not None:
                            pivot = lit
                            break
                    if pivot is not None:
                        break

                if pivot is None:
                    break

                conflict_lits.remove(pivot)
                for t_lit, _, reason in reversed(trail):
                    if t_lit == -pivot:
                        for l in reason:
                            if l != -pivot:
                                conflict_lits.add(l)
                        break

            learned = list(conflict_lits)
            if not learned:
                return None

            all_clauses.append(learned)

            for lit in learned:
                activity[abs(lit)] += 1.0
            for v in activity:
                activity[v] *= 0.95

            levels = sorted(
                [var_level.get(abs(lit), 0) for lit in learned],
                reverse=True
            )
            backjump_level = levels[1] if len(levels) > 1 else 0

            while trail and trail[-1][1] > backjump_level:
                lit, lev, _ = trail.pop()
                v = abs(lit)
                del assignment[v]
                del var_level[v]
            current_level = backjump_level
            continue

        if len(assignment) == len(activity):
            return assignment

        unassigned_vars = [v for v in activity if v not in assignment]
        if not unassigned_vars:
            return None
        decision_var = max(unassigned_vars, key=lambda v: activity[v])
        current_level += 1
        assignment[decision_var] = True
        var_level[decision_var] = current_level
        trail.append((decision_var, current_level, None))

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