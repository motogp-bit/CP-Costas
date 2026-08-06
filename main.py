import time
from ortools.sat.python import cp_model

def add_lex_less_or_equal(model, arr1, arr2, name_prefix="lex"):
    n = len(arr1)
    is_eq_prefix = model.NewBoolVar(f'{name_prefix}_eq_0')
    model.Add(is_eq_prefix == 1)
    
    for i in range(n):
        model.Add(arr1[i] <= arr2[i]).OnlyEnforceIf(is_eq_prefix)
        if i < n - 1:
            next_eq = model.NewBoolVar(f'{name_prefix}_eq_{i+1}')
            curr_eq = model.NewBoolVar(f'{name_prefix}_match_{i}')
            
            model.Add(arr1[i] == arr2[i]).OnlyEnforceIf(curr_eq)
            model.Add(arr1[i] != arr2[i]).OnlyEnforceIf(curr_eq.Not())
            
            model.AddBoolAnd([is_eq_prefix, curr_eq]).OnlyEnforceIf(next_eq)
            model.AddBoolOr([is_eq_prefix.Not(), curr_eq.Not()]).OnlyEnforceIf(next_eq.Not())
            
            is_eq_prefix = next_eq

def solve_array_configuration():
    model = cp_model.CpModel()
    n = 17

    A_vars = [model.NewIntVar(1, n, f'A_{i}') for i in range(1, n + 1)]
    model.AddAllDifferent(A_vars)
    A_rev = [A_vars[n - 1 - i] for i in range(n)]
    add_lex_less_or_equal(model, A_vars, A_rev, name_prefix="gen_rev")
    
    A_comp = [n + 1 - A_vars[i] for i in range(n)]
    add_lex_less_or_equal(model, A_vars, A_comp, name_prefix="gen_comp")

    T = {}
    abs_T = {}
    abs_vars_list = []
    
    for w in range(1, n):
        for j in range(1, n - w + 1):
            t_var = model.NewIntVarFromDomain(
                cp_model.Domain.FromIntervals([[-n + 1, -1], [1, n - 1]]), f'T_{w}_{j}'
            )
            abs_var = model.NewIntVar(1, n - 1, f'absT_{w}_{j}')
            
            model.Add(t_var == A_vars[j + w - 1] - A_vars[j - 1])
            model.AddAbsEquality(abs_var, t_var)
            
            T[(w, j)] = t_var
            abs_T[(w, j)] = abs_var
            abs_vars_list.append(abs_var)

    max_w = (n - 1) // 2
    for j in range(1, n + 1):
        col_vars = [T[(w, j)] for w in range(1, max_w + 1) if (w, j) in T]
        if len(col_vars) > 1:
            model.AddAllDifferent(col_vars)

    for w in range(1, n):
        model.AddAllDifferent([T[(w, j)] for j in range(1, n - w + 1)])

    for k in range(1, n):
        k_indicators = []
        for var in abs_vars_list:
            b = model.NewBoolVar('')
            model.Add(var == k).OnlyEnforceIf(b)
            model.Add(var != k).OnlyEnforceIf(b.Not())
            k_indicators.append(b)
        model.Add(sum(k_indicators) == n - k)

    w_conditions = []
    for w in range(1, n):
        row_vars = [T[(w, j)] for j in range(1, n - w + 1)]
        
        has_1 = model.NewBoolVar(f'has_1_w{w}')
        has_m1 = model.NewBoolVar(f'has_m1_w{w}')
        has_2 = model.NewBoolVar(f'has_2_w{w}')
        has_m2 = model.NewBoolVar(f'has_m2_w{w}')

        for target, flag in [(1, has_1), (-1, has_m1), (2, has_2), (-2, has_m2)]:
            match_flags = [model.NewBoolVar('') for _ in row_vars]
            for rv, mf in zip(row_vars, match_flags):
                model.Add(rv == target).OnlyEnforceIf(mf)
                model.Add(rv != target).OnlyEnforceIf(mf.Not())
            model.AddBoolOr(match_flags).OnlyEnforceIf(flag)
            model.AddBoolAnd([mf.Not() for mf in match_flags]).OnlyEnforceIf(flag.Not())

        cond1 = model.NewBoolVar(f'cond1_w{w}')
        model.AddBoolAnd([has_1, has_m1]).OnlyEnforceIf(cond1)

        cond2 = model.NewBoolVar(f'cond2_w{w}')
        model.AddBoolAnd([has_2, has_m2]).OnlyEnforceIf(cond2)

        w_cond = model.NewBoolVar(f'w_cond_{w}')
        model.AddBoolOr([cond1, cond2]).OnlyEnforceIf(w_cond)
        w_conditions.append(w_cond)

    model.AddBoolOr(w_conditions)

    model.AddDecisionStrategy(
        A_vars, 
        cp_model.CHOOSE_FIRST, 
        cp_model.SELECT_MIN_VALUE
    )

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f'Assignment successful.')
        sequence = [solver.Value(var) for var in A_vars]
        print(f'A = {sequence}')
    else:
        print(f'No valid assignment exists.')

if __name__ == '__main__':
    start_time = time.time()
    solve_array_configuration()
    end_time = time.time()
    print(f"Time: {end_time - start_time:.2f} seconds")