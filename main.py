import math
from ortools.sat.python import cp_model

def solve_array_configuration():
    model = cp_model.CpModel()
    n = 32

    A = {}
    for i in range(1, n + 1):
        A[i] = model.NewIntVar(1, n, f'A_{i}')
    
    model.AddAllDifferent(list(A.values()))
    T = {}
    for w in range(1, n):
        for j in range(1, n - w + 1):
            domain = cp_model.Domain.FromIntervals([[-n + 1, -1], [1, n - 1]])
            T[(w, j)] = model.NewIntVarFromDomain(domain, f'T_{w}_{j}')
            
            model.Add(T[(w, j)] == A[j + w] - A[j])

    max_w = math.floor((n - 1) / 2)
    for j in range(1, n + 1):
        col_vars = []
        for w in range(1, max_w + 1):
            if (w, j) in T:
                col_vars.append(T[(w, j)])
        if len(col_vars) > 1:
            model.AddAllDifferent(col_vars)

    abs_T = {}
    for w in range(1, n):
        for j in range(1, n - w + 1):
            abs_T[(w, j)] = model.NewIntVar(1, n - 1, f'absT_{w}_{j}')
            model.AddAbsEquality(abs_T[(w, j)], T[(w, j)])

    for k in range(1, n):
        k_indicators = []
        for w in range(1, n):
            for j in range(1, n - w + 1):
                is_k = model.NewBoolVar(f'is_{k}_{w}_{j}')
                model.Add(abs_T[(w, j)] == k).OnlyEnforceIf(is_k)
                model.Add(abs_T[(w, j)] != k).OnlyEnforceIf(is_k.Not())
                k_indicators.append(is_k)
        model.Add(sum(k_indicators) == n - k)

    w_conditions = []
    for w in range(1, n):
        has_1 = model.NewBoolVar(f'has_1_w{w}')
        has_m1 = model.NewBoolVar(f'has_m1_w{w}')
        has_2 = model.NewBoolVar(f'has_2_w{w}')
        has_m2 = model.NewBoolVar(f'has_m2_w{w}')

        b_1 = []
        b_m1 = []
        b_2 = []
        b_m2 = []
        for j in range(1, n - w + 1):
            b1 = model.NewBoolVar(f'b1_{w}_{j}')
            model.Add(T[(w, j)] == 1).OnlyEnforceIf(b1)
            model.Add(T[(w, j)] != 1).OnlyEnforceIf(b1.Not())
            b_1.append(b1)

            bm1 = model.NewBoolVar(f'bm1_{w}_{j}')
            model.Add(T[(w, j)] == -1).OnlyEnforceIf(bm1)
            model.Add(T[(w, j)] != -1).OnlyEnforceIf(bm1.Not())
            b_m1.append(bm1)

            b2 = model.NewBoolVar(f'b2_{w}_{j}')
            model.Add(T[(w, j)] == 2).OnlyEnforceIf(b2)
            model.Add(T[(w, j)] != 2).OnlyEnforceIf(b2.Not())
            b_2.append(b2)

            bm2 = model.NewBoolVar(f'bm2_{w}_{j}')
            model.Add(T[(w, j)] == -2).OnlyEnforceIf(bm2)
            model.Add(T[(w, j)] != -2).OnlyEnforceIf(bm2.Not())
            b_m2.append(bm2)

        model.AddMaxEquality(has_1, b_1)
        model.AddMaxEquality(has_m1, b_m1)
        model.AddMaxEquality(has_2, b_2)
        model.AddMaxEquality(has_m2, b_m2)

        cond1 = model.NewBoolVar(f'cond1_w{w}')
        model.AddMinEquality(cond1, [has_1, has_m1])

        cond2 = model.NewBoolVar(f'cond2_w{w}')
        model.AddMinEquality(cond2, [has_2, has_m2])

        w_cond = model.NewBoolVar(f'w_cond_{w}')
        model.AddMaxEquality(w_cond, [cond1, cond2])
        w_conditions.append(w_cond)

    model.AddBoolOr(w_conditions)

    model.Add(T[(n - 3, 2)] == T[(n - 2, 1)] + T[(n - 2, 2)] - T[(n - 1, 1)])

    for w in range(1, n):
        model.AddAllDifferent([T[(w, j)] for j in range(1, n - w + 1)])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f'Assignment successful.')
        sequence = [solver.Value(A[i]) for i in range(1, n + 1)]
        print(f'A = {sequence}')
    else:
        print(f'No valid assignment exists.')

if __name__ == '__main__':
    solve_array_configuration()