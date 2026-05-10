def generate_petersen_3coloring_dimacs():
    vertices = list(range(10))

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
        (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
        (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)
    ]

    num_colors = 3
    num_vertices = len(vertices)

    def var_index(v, c):
        return v * num_colors + c + 1

    clauses = []

    for v in vertices:
        vars_for_v = [var_index(v, c) for c in range(num_colors)]

        clauses.append(vars_for_v)

        for i in range(len(vars_for_v)):
            for j in range(i + 1, len(vars_for_v)):
                clauses.append([-vars_for_v[i], -vars_for_v[j]])

    for u, v in edges:
        for c in range(num_colors):
            clauses.append([-var_index(u, c), -var_index(v, c)])

    num_vars = num_vertices * num_colors
    num_clauses = len(clauses)

    dimacs_lines = []
    dimacs_lines.append(f"p cnf {num_vars} {num_clauses}")

    for clause in clauses:
        clause_str = " ".join(map(str, clause)) + " 0"
        dimacs_lines.append(clause_str)

    return "\n".join(dimacs_lines)

with open("petersen_graph.cnf", "w") as f:
    f.write(generate_petersen_3coloring_dimacs())