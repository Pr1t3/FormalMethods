def ramsey_kn_dimacs(n):
    var_id = {}
    idx = 1
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            var_id[(i,j)] = idx
            idx += 1

    clauses = []
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            for k in range(j+1, n+1):
                vid_ij = var_id[(i,j)]
                vid_ik = var_id[(i,k)]
                vid_jk = var_id[(j,k)]
                clauses.append([-vid_ij, -vid_ik, -vid_jk])
                clauses.append([vid_ij, vid_ik, vid_jk])

    num_vars = len(var_id)
    num_clauses = len(clauses)

    dimacs = [f"p cnf {num_vars} {num_clauses}"]
    dimacs += [" ".join(map(str, cl)) + " 0" for cl in clauses]
    return "\n".join(dimacs)

with open("ramsey_k5.cnf", "w") as f:
    f.write(ramsey_kn_dimacs(5))

with open("ramsey_k6.cnf", "w") as f:
    f.write(ramsey_kn_dimacs(6))