def solveQ4():
    rs1 = [solveQ1(day = days[i], shift_name=shift_name, shifts=shifts, hour_name=hour_name) for i in range(len(days_name))]
    rs2 = solveQ4_1(shift_name=shift_name, days_name=days_name, result_Q1=rs1)
    rs3 = solveQ4_2(shift_name=shift_name, shifts=shifts, hour_name=hour_name, days=days, days_name=days_name, result_Q1=rs1, result_Q2=rs2)

    def getShiftName(arr):
        for i in range(len(arr)):
            if arr[i] == 1:
                return shift_name[i]
        return "EM"

    print("Result Q4: ")
    for i in range(len(rs3)):
        for j in range(len(days_name)):
            sys.stdout.write(getShiftName(rs3[i][j]) + " ")
        print()



def solveQ4_1(shift_name, days_name, result_Q1):
    # Number of CSR required each day (ncj, j = 1, 2, ..., 7)
    csr_required_each_day = [sum([result_Q1[i][j] for j in range(len(shift_name))]) for i in range(len(result_Q1))]
    
    # Number of empty slots (ne)
    empty_slots = len(days_name) * max(csr_required_each_day) - sum(csr_required_each_day)

    try:
        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # objective function: x
        obj_coefficients = [1] 
        var_names = ["x"]
        var_types = ["I"]
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)

        # (nd - 1)x >= max(ncj) - ne
        rows = [[['x'], [len(days_name) - 1]]]
        rhs = [max(csr_required_each_day) - empty_slots]
        senses = ["G"]
        constraint_names = ["empty_slots"]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        rows = [[['x'], [1]]]
        rhs = [csr_required_each_day[5] + csr_required_each_day[6] - max(csr_required_each_day)]
        senses = ["G"]
        constraint_names = ["days_off"]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        problem.solve()
        
        # print("solution status = ", problem.solution.get_status())
        # print("solution value = ", problem.solution.get_objective_value())
        # print("solution = ", problem.solution.get_values())
        # slack = problem.solution.get_linear_slacks()
        x     = problem.solution.get_values()

        # for i in range(len(constraint_names)):
        #     print ("Constraint %s:  Slack = %d" % (constraint_names[i], slack[i]))
        # for i in range(len(var_names)):
        #     print ("%s: %d" % (var_names[i], x[i]))

        return int(x[0])
    except CplexError as e:
        print(e)

def solveQ4_2(shift_name, shifts, hour_name, days, days_name, result_Q1, result_Q2):
    # Number of CSR required each day (ncj, j = 1, 2, ..., 7)
    csr_required_each_day = [sum([result_Q1[i][j] for j in range(len(shift_name))]) for i in range(len(result_Q1))]
    
    # Number of CSR required each shift (nck, k = 1, 2, ..., 6)
    csr_required_each_shift = [sum([result_Q1[i][j] for i in range(len(result_Q1))]) for j in range(len(shift_name))]
    
    # Number of CSR required in a week nc
    csr_required = int(result_Q2 + max(csr_required_each_day))
    
    # CSR names (CSR1, CSR2, ..., CSRnc)
    csr_name = ["CSR" + str(i) for i in range(1, csr_required + 1)]
    
    try:
        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # objective function: all coefficients is 1
        obj_coefficients = [1] * len(csr_name) * len(days_name) * len(shift_name)
        
        # variables: CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR1_Tuesday_C1, CSR1_Tuesday_C2, ..., CSR1_Tuesday_C6, ..., CSRnc_Sunday_C6
        var_names = [csr_name[i] + "_" + days_name[j] + "_" + shift_name[k] for i in range(len(csr_name)) for j in range(len(days_name)) for k in range(len(shift_name))]
        
        # variable types: all variables are binary
        var_types = ["B"] * len(csr_name) * len(days_name) * len(shift_name)
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)

        # Constraint 1:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6], 
        #                  [1, 1, ..., 1]] 
        #                       for every CSR 
        #                           and every day
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for k in range(len(shift_name))], 
                [1] * len(shift_name)] 
                    for i in range(len(csr_name)) 
                        for j in range(len(days_name))]
        
        # Right hand side: 1 for every CSR and every day
        rhs = [1] * len(csr_name) * len(days_name)
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * len(csr_name) * len(days_name)
        
        # constrant names: Con1_CSR1_Monday, Con1_CSR1_Tuesday, ..., Con1_CSRnc_Sunday
        constraint_names = ["Con1_" + csr_name[i] + "_" + days_name[j] for i in range(len(csr_name)) for j in range(len(days_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 2:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR1_Tuesday_C1, ... CSR1_Sunday_C6], 
        #                  [1, 1, ..., 1]] 
        #                      for every CSR
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for j in range(5, 7) for k in range(len(shift_name))], 
                [1] * 2 * len(shift_name)] 
                    for i in range(len(csr_name))]
        
        # Right hand side: nd - 1, for all csr
        rhs = [1] * len(csr_name)
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * len(csr_name)

        # constrant names: Con2_CSR1, Con2_CSR2, ..., Con2_CSRnc
        constraint_names = ["Con2_" + csr_name[i] for i in range(len(csr_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 3:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR2_Monday_C1, ..., CSRnc_Monday_C6], 
        #                  [shift[0][t], shift[1][t], ..., shift[6][t], shift[0][t], ..., shift[6][t]] 
        #                       for every day (Monday - Sunday) 
        #                           and every hour t
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for i in range(len(csr_name)) for k in range(len(shift_name))],
                 [shifts[k][t] for i in range(len(csr_name)) for k in range(len(shift_name))]] 
                    for j in range(len(days_name)) 
                        for t in range(len(hour_name))]
        
        # Right hand side: day[j][t] for every day j and every hour t
        rhs = [days[j][t] for j in range(len(days_name)) for t in range(len(hour_name))]
        
        # Sense: all constraints are greater than or equal to
        senses = ["G"] * len(days_name) * len(hour_name)
        
        # constrant names: Con3_Monday_8h-9h, Con3_Monday_9h-10h, ..., Con3_Sunday_20h-21h
        constraint_names = ["Con3_" + days_name[j] + "_" + hour_name[t] for j in range(len(days_name)) for t in range(len(hour_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 4_1:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Tuesday_C1...], [1, 1, ...]] for every CSR and every shift
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for j in range(len(days_name))],
                [1] * len(days_name)] 
                    for i in range(len(csr_name)) 
                        for k in range(len(shift_name))]
        
        # Right hand side: ceil(nck/nc) for every CSR and every shift
        rhs = [math.ceil(csr_required_each_shift[k]/csr_required) for i in range(len(csr_name)) for k in range(len(shift_name))]
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * len(csr_name) * len(shift_name)

        # constrant names: Con4_1_CSR1_C1, Con4_1_CSR1_C2, ..., Con4_1_CSRnc_C6
        constraint_names = ["Con4_1_" + csr_name[i] + "_" + shift_name[k] for i in range(len(csr_name)) for k in range(len(shift_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 4_2:
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for j in range(len(days_name))],
                [1] * len(days_name)] 
                    for i in range(len(csr_name)) 
                        for k in range(len(shift_name))]
        rhs = [math.floor(csr_required_each_shift[k]/csr_required) for i in range(len(csr_name)) for k in range(len(shift_name))]
        senses = ["G"] * len(csr_name) * len(shift_name)
        constraint_names = ["Con4_2_" + csr_name[i] + "_" + shift_name[k] for i in range(len(csr_name)) for k in range(len(shift_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        problem.solve()

        # print("solution status = ", problem.solution.get_status())
        # print("solution value = ", problem.solution.get_objective_value())
        # print("solution = ", problem.solution.get_values())
        # slack = problem.solution.get_linear_slacks()
        x     = problem.solution.get_values()

        # constraint_names = problem.linear_constraints.get_names()
        # for i in range(len(constraint_names)):
        #     print ("Constraint %s:  Slack = %d" % (constraint_names[i], slack[i]))
        # for i in range(len(var_names)):
        #     print ("%s: %d" % (var_names[i], x[i]))        

        return [[[x[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for k in range(len(shift_name))] for j in range(len(days_name))] for i in range(len(csr_name))]
    except CplexError as e:
        print(e)
