import cplex
from cplex.exceptions import CplexError
import math
import sys

def solveQ1(hour_name, day, shift_name, shifts):    
    try:
        K = len(shift_name)
        T = len(hour_name)

        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # Objective function coefficients: [1, 1, 1, 1, 1, 1]
        obj_coefficients = [1] * K
        # Variable names: ["x1", "x2", "x3", "x4", "x5", "x6"]
        var_names = ["x" + str(i + 1) for i in range(K)]              
        # Variable types (C: continuous, I: integer): ["I", "I", "I", "I", "I", "I"] 
        var_types = ["I"] * K     
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types) 
        
        # left hand side: [[["x1", "x2", "x3", "x4", "x5", "x6"], [1, 0, 0, 0, 0, 1]], ...]
        # right hand side: [6, 9, 9, 8, 3, 3, 7, 8, 8, 5, 3, 3, 2]
        # senses (greater than or equals: G, less than or equals: L, equals: E...): ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G"]
        # x1 + x6 >= 6
        rows = [[var_names, [shifts[k][t] for k in range(K)]] for t in range(T)] 
        rhs = day                            
        senses = ["G"] * T
        constraint_names = hour_name # ["8h-9h", "9h-10h", "10h-11h", "11h-12h", "12h-13h", "13h-14h", "14h-15h", "15h-16h", "16h-17h", "17h-18h", "18h-19h", "19h-20h", "20h-21h"]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        problem.solve()
        # print("solution status = ", problem.solution.get_status())
        # print("solution value = ", problem.solution.get_objective_value())
        # print("solution = ", problem.solution.get_values())
        # slack = problem.solution.get_linear_slacks()
        x = problem.solution.get_values()

        # for i in range(len(hour_name)):
        #     print ("Constraint %s:  Slack = %d" % (hour_name[i], slack[i]))
        # for i in range(len(shifts)):
        #     print ("Shift %s has %d CSR" % (var_names[i], x[i]))

        # print("Result: " + str(x))
        return [int(x[i]) for i in range(len(x))]
    except CplexError as e:
        print(e)

def solveQ2(days_name, csr_required_each_day, empty_slots):
    try:
        J = len(days_name)

        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # objective function: x
        obj_coefficients = [1] 
        var_names = ["x"]
        var_types = ["I"]
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)

        # (nd - 1)x >= max(ncj) - ne
        rows = [[['x'], [J - 1]]]
        rhs = [max(csr_required_each_day) - empty_slots]
        senses = ["G"]
        constraint_names = ["empty_slots"]
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

def solveQ3(shift_name, shifts, hour_name, days, days_name, csr_name, csr_required_each_shift, csr_required):        
    try:
        I = len(csr_name)
        J = len(days_name)
        K = len(shift_name)
        T = len(hour_name)
    
        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # objective function: all coefficients is 1
        obj_coefficients = [1] * I * J * K
        
        # variables: CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR1_Tuesday_C1, CSR1_Tuesday_C2, ..., CSR1_Tuesday_C6, ..., CSRnc_Sunday_C6
        var_names = [csr_name[i] + "_" + days_name[j] + "_" + shift_name[k] for i in range(I) for j in range(J) for k in range(K)]
        
        # variable types: all variables are binary
        var_types = ["B"] * I * J * K
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)

        # Constraint 1:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6], 
        #                  [1, 1, ..., 1]] 
        #                       for every CSR 
        #                           and every day
        rows = [[[var_names[k + j * K + i * J * K] for k in range(K)], 
                [1] * K] 
                    for i in range(I) 
                        for j in range(J)]
        
        # Right hand side: 1 for every CSR and every day
        rhs = [1] * I * J
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * I * J
        
        # constrant names: Con1_CSR1_Monday, Con1_CSR1_Tuesday, ..., Con1_CSRnc_Sunday
        constraint_names = ["Con1_" + csr_name[i] + "_" + days_name[j] for i in range(I) for j in range(J)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 2:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR1_Tuesday_C1, ... CSR1_Sunday_C6], 
        #                  [1, 1, ..., 1]] 
        #                      for every CSR
        rows = [[[var_names[k + j * K + i * J * K] for j in range(J) for k in range(K)], 
                [1] * J * K] 
                    for i in range(I)]
        
        # Right hand side: nd - 1, for all csr
        rhs = [J - 1] * I
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * I

        # constrant names: Con2_CSR1, Con2_CSR2, ..., Con2_CSRnc
        constraint_names = ["Con2_" + csr_name[i] for i in range(I)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 3:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR2_Monday_C1, ..., CSRnc_Monday_C6], 
        #                  [shift[0][t], shift[1][t], ..., shift[6][t], shift[0][t], ..., shift[6][t]] 
        #                       for every day (Monday - Sunday) 
        #                           and every hour t
        rows = [[[var_names[k + j * K + i * J * K] for i in range(I) for k in range(K)],
                 [shifts[k][t] for i in range(I) for k in range(K)]] 
                    for j in range(J) 
                        for t in range(T)]
        
        # Right hand side: day[j][t] for every day j and every hour t
        rhs = [days[j][t] for j in range(J) for t in range(T)]
        
        # Sense: all constraints are greater than or equal to
        senses = ["G"] * J * T
        
        # constrant names: Con3_Monday_8h-9h, Con3_Monday_9h-10h, ..., Con3_Sunday_20h-21h
        constraint_names = ["Con3_" + days_name[j] + "_" + hour_name[t] for j in range(J) for t in range(T)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 4_1:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Tuesday_C1...], [1, 1, ...]] for every CSR and every shift
        rows = [[[var_names[k + j * K + i * J * K] for j in range(J)],
                [1] * J] 
                    for i in range(I) 
                        for k in range(K)]
        
        # Right hand side: ceil(nck/nc) for every CSR and every shift
        rhs = [math.ceil(csr_required_each_shift[k]/csr_required) for i in range(I) for k in range(K)]
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * I * K

        # constrant names: Con4_1_CSR1_C1, Con4_1_CSR1_C2, ..., Con4_1_CSRnc_C6
        constraint_names = ["Con4_1_" + csr_name[i] + "_" + shift_name[k] for i in range(I) for k in range(K)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 4_2:
        rows = [[[var_names[k + j * K + i * J * K] for j in range(J)],
                [1] * J] 
                    for i in range(I) 
                        for k in range(K)]
        rhs = [math.floor(csr_required_each_shift[k]/csr_required) for i in range(I) for k in range(K)]
        senses = ["G"] * I * K
        constraint_names = ["Con4_2_" + csr_name[i] + "_" + shift_name[k] for i in range(I) for k in range(K)]
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

        return [[[x[k + j * K + i * J * K] for k in range(K)] for j in range(J)] for i in range(I)]
    except CplexError as e:
        print(e)

def Q1_2_3():
    days = [[6, 9, 9, 8, 3, 3, 7, 8, 8, 5, 3, 3, 2], #Monday
        [6, 10, 7, 7,3, 4, 7, 5, 9, 5, 3, 4, 3], #Tuesday
        [7, 9, 9, 6, 3, 4, 6, 8, 7, 4, 3, 3, 3], #Wednesday
        [6, 9, 8, 6, 4, 4, 5, 8, 7, 5, 4, 3, 4], #Thursday
        [6, 7, 8, 7, 3, 5, 6, 7, 6, 5, 3, 3, 3], #Friday
        [6, 9, 9, 4, 3, 3, 4, 5, 5, 5, 3, 3, 2], #Saturday
        [5, 7, 6, 5, 4, 3, 4, 5, 6, 5, 3, 3, 3]] #Sunday
    days_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hour_name = ["8h-9h", "9h-10h", "10h-11h", "11h-12h", "12h-13h", "13h-14h", "14h-15h", "15h-16h", "16h-17h", "17h-18h", "18h-19h", "19h-20h", "20h-21h"]
    shifts = [[1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0], #C1
        [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0], #C2
        [0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0], #C3
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0], #C4
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1], #C5
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]] #C6
    shift_name = ["C1", "C2", "C3", "C4", "C5", "C6"]

    rs1 = [solveQ1(day = days[i], shift_name=shift_name, shifts=shifts, hour_name=hour_name) for i in range(len(days_name))]
    
    # Number of CSR required each day (ncj, j = 1, 2, ..., 7)
    csr_required_each_day = [sum([rs1[i][j] for j in range(len(shift_name))]) for i in range(len(rs1))]
    # Number of empty slots (ne)
    empty_slots = len(days_name) * max(csr_required_each_day) - sum(csr_required_each_day)

    rs2 = solveQ2(days_name=days_name, csr_required_each_day=csr_required_each_day, empty_slots=empty_slots)
    
    # Number of CSR required each shift (nck, k = 1, 2, ..., 6)
    csr_required_each_shift = [sum([rs1[i][j] for i in range(len(rs1))]) for j in range(len(shift_name))]
    
    # Number of CSR required in a week nc
    csr_required = rs2 + max(csr_required_each_day)

    # CSR names (CSR1, CSR2, ..., CSRnc)
    csr_name = ["CSR" + str(i) for i in range(1, csr_required + 1)]
    rs3 = solveQ3(shift_name=shift_name, shifts=shifts, hour_name=hour_name, csr_name=csr_name, days=days, days_name=days_name, csr_required=csr_required, csr_required_each_shift=csr_required_each_shift)
    
    sumRS1 = [sum(rs1[i]) for i in range(len(rs1))]
    print("Result Q1: " + " ".join(f"Day {i}: {sumRS1[i]}" for i in range(len(sumRS1))))
    print(f"Result Q2: x = {rs2}, number of CSR = {rs2 + max(sumRS1)}")

    def getShiftName(arr):
        for i in range(len(arr)):
            if arr[i] == 1:
                return shift_name[i]
        return "EM"

    print("Result Q3: ")
    for i in range(len(rs3)):
        for j in range(len(days_name)):
            sys.stdout.write(getShiftName(rs3[i][j]) + " ")
        print()

def solveQ4_1_Step2(days_name, csr_required_each_day, empty_slots):
    try:
        J = len(days_name)

        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # objective function: x
        obj_coefficients = [1] 
        var_names = ["x"]
        var_types = ["I"]
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)

        # (nd - 1)x >= max(ncj) - ne
        rows = [[['x'], [J - 1]]]
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
        x     = problem.solution.get_values()

        return int(x[0])
    except CplexError as e:
        print(e)

def solveQ4_1_Step3(shift_name, shifts, hour_name, days, days_name, csr_name, csr_required_each_shift, csr_required):
    try:
        I = len(csr_name)
        J = len(days_name)
        K = len(shift_name)
        T = len(hour_name)

        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # objective function: all coefficients is 1
        obj_coefficients = [1] * I * J * K
        
        # variables: CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR1_Tuesday_C1, CSR1_Tuesday_C2, ..., CSR1_Tuesday_C6, ..., CSRnc_Sunday_C6
        var_names = [csr_name[i] + "_" + days_name[j] + "_" + shift_name[k] for i in range(len(csr_name)) for j in range(len(days_name)) for k in range(len(shift_name))]
        
        # variable types: all variables are binary
        var_types = ["B"] * I * J * K
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)

        # Constraint 1:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6], 
        #                  [1, 1, ..., 1]] 
        #                       for every CSR 
        #                           and every day
        rows = [[[var_names[k + j * K + i * J * K] for k in range(K)], 
                [1] * K] 
                    for i in range(I) 
                        for j in range(J)]
        
        # Right hand side: 1 for every CSR and every day
        rhs = [1] * I * J
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * I * J
        
        # constrant names: Con1_CSR1_Monday, Con1_CSR1_Tuesday, ..., Con1_CSRnc_Sunday
        constraint_names = ["Con1_" + csr_name[i] + "_" + days_name[j] for i in range(I) for j in range(len(days_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 2:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR1_Tuesday_C1, ... CSR1_Sunday_C6], 
        #                  [1, 1, ..., 1]] 
        #                      for every CSR
        rows = [[[var_names[k + j * K + i * J * K] for j in range(5, 7) for k in range(K)], 
                [1] * 2 * K] 
                    for i in range(I)]
        
        # Right hand side: nd - 1, for all csr
        rhs = [1] * I
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * I

        # constrant names: Con2_CSR1, Con2_CSR2, ..., Con2_CSRnc
        constraint_names = ["Con2_" + csr_name[i] for i in range(I)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 3:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR2_Monday_C1, ..., CSRnc_Monday_C6], 
        #                  [shift[0][t], shift[1][t], ..., shift[6][t], shift[0][t], ..., shift[6][t]] 
        #                       for every day (Monday - Sunday) 
        #                           and every hour t
        rows = [[[var_names[k + j * K + i * J * K] for i in range(I) for k in range(K)],
                 [shifts[k][t] for i in range(I) for k in range(K)]] 
                    for j in range(J) 
                        for t in range(T)]
        
        # Right hand side: day[j][t] for every day j and every hour t
        rhs = [days[j][t] for j in range(J) for t in range(T)]
        
        # Sense: all constraints are greater than or equal to
        senses = ["G"] * J * T
        
        # constrant names: Con3_Monday_8h-9h, Con3_Monday_9h-10h, ..., Con3_Sunday_20h-21h
        constraint_names = ["Con3_" + days_name[j] + "_" + hour_name[t] for j in range(J) for t in range(T)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 4_1:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Tuesday_C1...], [1, 1, ...]] for every CSR and every shift
        rows = [[[var_names[k + j * K + i * J * K] for j in range(J)],
                [1] * J] 
                    for i in range(I) 
                        for k in range(K)]
        
        # Right hand side: ceil(nck/nc) for every CSR and every shift
        rhs = [math.ceil(csr_required_each_shift[k]/csr_required) for i in range(I) for k in range(K)]
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * I * K

        # constrant names: Con4_1_CSR1_C1, Con4_1_CSR1_C2, ..., Con4_1_CSRnc_C6
        constraint_names = ["Con4_1_" + csr_name[i] + "_" + shift_name[k] for i in range(I) for k in range(K)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 4_2:
        rows = [[[var_names[k + j * K + i * J * K] for j in range(J)],
                [1] * J] 
                    for i in range(I) 
                        for k in range(K)]
        rhs = [math.floor(csr_required_each_shift[k]/csr_required) for i in range(I) for k in range(K)]
        senses = ["G"] * I * K
        constraint_names = ["Con4_2_" + csr_name[i] + "_" + shift_name[k] for i in range(I) for k in range(K)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        problem.solve()
        x     = problem.solution.get_values()      

        return [[[x[k + j * K + i * J * K] for k in range(K)] for j in range(J)] for i in range(I)]
    except CplexError as e:
        print(e)

def Q4_1():
    days = [[6, 9, 9, 8, 3, 3, 7, 8, 8, 5, 3, 3, 2], #Monday
        [6, 10, 7, 7,3, 4, 7, 5, 9, 5, 3, 4, 3], #Tuesday
        [7, 9, 9, 6, 3, 4, 6, 8, 7, 4, 3, 3, 3], #Wednesday
        [6, 9, 8, 6, 4, 4, 5, 8, 7, 5, 4, 3, 4], #Thursday
        [6, 7, 8, 7, 3, 5, 6, 7, 6, 5, 3, 3, 3], #Friday
        [6, 9, 9, 4, 3, 3, 4, 5, 5, 5, 3, 3, 2], #Saturday
        [5, 7, 6, 5, 4, 3, 4, 5, 6, 5, 3, 3, 3]] #Sunday
    days_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hour_name = ["8h-9h", "9h-10h", "10h-11h", "11h-12h", "12h-13h", "13h-14h", "14h-15h", "15h-16h", "16h-17h", "17h-18h", "18h-19h", "19h-20h", "20h-21h"]
    shifts = [[1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0], #C1
        [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0], #C2
        [0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0], #C3
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0], #C4
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1], #C5
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]] #C6
    shift_name = ["C1", "C2", "C3", "C4", "C5", "C6"]


    rs1 = [solveQ1(day = days[i], shift_name=shift_name, shifts=shifts, hour_name=hour_name) for i in range(len(days_name))]
    
    # Number of CSR required each day (ncj, j = 1, 2, ..., 7)
    csr_required_each_day = [sum([rs1[i][j] for j in range(len(shift_name))]) for i in range(len(rs1))]
    # Number of empty slots (ne)
    empty_slots = len(days_name) * max(csr_required_each_day) - sum(csr_required_each_day)

    rs2 = solveQ4_1_Step2(days_name=days_name, csr_required_each_day=csr_required_each_day, empty_slots=empty_slots)

    # Number of CSR required each shift (nck, k = 1, 2, ..., 6)
    csr_required_each_shift = [sum([rs1[i][j] for i in range(len(rs1))]) for j in range(len(shift_name))]
    
    # Number of CSR required in a week nc
    csr_required = rs2 + max(csr_required_each_day)

    # CSR names (CSR1, CSR2, ..., CSRnc)
    csr_name = ["CSR" + str(i) for i in range(1, csr_required + 1)]
    rs3 = solveQ4_1_Step3(shift_name=shift_name, shifts=shifts, hour_name=hour_name, csr_name=csr_name, days=days, days_name=days_name, csr_required=csr_required, csr_required_each_shift=csr_required_each_shift)

    def getShiftName(arr):
        for i in range(len(arr)):
            if arr[i] == 1:
                return shift_name[i]
        return "EM"

    print("Result Q4 (1): ")
    for i in range(len(rs3)):
        for j in range(len(days_name)):
            sys.stdout.write(getShiftName(rs3[i][j]) + " ")
        print()

def solveQ4_2(csr_name, plan_name, week_name, days_off_week_plan, days_off):
    try:
        I = len(csr_name)
        W = len(week_name)
        L = len(plan_name)

        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)
        obj_coefficients = [1] * I * W * L
        var_names = [csr_name[i] + "_" + week_name[w] + "_" + plan_name[l] for i in range(I) for w in range(W) for l in range(L)]
        var_types = ["B"] * I * W * L
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)
        
        #Constraint 1:
        rows = [[[var_names[l + w * L + i * L * W] for l in range(L)], 
                [1] * L] 
                    for i in range(I)
                        for w in range(W)]
        rhs = [1] * I * W
        senses = ["E"] * I * W
        constraint_names = ["Con1_" + csr_name[i] + "_" + week_name[w] for i in range(I) for w in range(W)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 2:
        rows = [[[var_names[l + w * L + i * L * W] for i in range(I)], 
                [1] * I] 
                    for w in range(W)
                        for l in range(L)]
        rhs = [1] * L * W
        senses = ["E"] * L * W
        constraint_names = ["Con2_" + plan_name[l] + "_" + week_name[w] for w in range(W) for l in range(L)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 3_1:
        rows = [[[var_names[l + w * L + i * L * W] for w in range(W) for l in range(L)], 
                [days_off_week_plan[w][l] for w in range(W) for l in range(L)]] 
                        for i in range(I)]
        rhs = [math.ceil(days_off / I) for i in range(I)]
        senses = ["L"] * I
        constraint_names = ["Con2_1_" + csr_name[i] for i in range(I)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 3_2:
        rows = [[[var_names[l + w * L + i * L * W] for w in range(W) for l in range(L)], 
                [days_off_week_plan[w][l] for w in range(W) for l in range(L)]] 
                        for i in range(I)]
        rhs = [math.floor(days_off / I) for i in range(I)]
        senses = ["G"] * I
        constraint_names = ["Con2_2_" + csr_name[i] for i in range(I)]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        problem.solve()
        x = problem.solution.get_values()
        return [[[int(x[l + w * L + i * L * W]) for l in range(L)] for w in range(W)] for i in range(I)]
    
    except CplexError as e:
        print(e)

def Q4_2():
    days = [[[6, 9, 9, 8, 3, 3, 7, 8, 8, 5, 3, 3, 2], #Monday
        [6, 10, 7, 7,3, 4, 7, 5, 9, 5, 3, 4, 3], #Tuesday
        [7, 9, 9, 6, 3, 4, 6, 8, 7, 4, 3, 3, 3], #Wednesday
        [6, 9, 8, 6, 4, 4, 5, 8, 7, 5, 4, 3, 4], #Thursday
        [6, 7, 8, 7, 3, 5, 6, 7, 6, 5, 3, 3, 3], #Friday
        [6, 9, 9, 4, 3, 3, 4, 5, 5, 5, 3, 3, 2], #Saturday
        [5, 7, 6, 5, 4, 3, 4, 5, 6, 5, 3, 3, 3]], #Sunday

        [[7, 9, 8, 8, 3, 3, 7, 8, 8, 5, 3, 3, 3],
        [6, 11, 7, 7,3, 4, 7, 5, 9, 9, 3, 4, 7],
        [7, 9, 11, 6, 3, 4, 6, 4, 7, 4, 3, 3, 3],
        [6, 9, 8, 6, 5, 4, 5, 8, 7, 5, 4, 3, 4], 
        [6, 7, 8, 7, 3, 6, 6, 7, 8, 5, 3, 5, 3], 
        [6, 7, 9, 4, 3, 3, 6, 5, 5, 5, 4, 3, 2],
        [5, 7, 6, 5, 4, 3, 4, 5, 6, 5, 3, 3, 3]],

        [[7, 9, 8, 8, 3, 3, 7, 8, 8, 5, 3, 3, 4],
        [6, 9, 7, 7, 5, 4, 7, 5, 9, 7, 3, 4, 7],
        [7, 9, 8, 6, 3, 7, 6, 4, 7, 4, 3, 3, 3],
        [6, 9, 8, 6, 5, 4, 5, 8, 7, 5, 4, 3, 6], 
        [6, 7, 8, 7, 3, 6, 7, 7, 8, 5, 5, 5, 3], 
        [6, 5, 9, 5, 3, 3, 6, 5, 5, 5, 4, 2, 2],
        [5, 7, 6, 5, 4, 3, 4, 5, 6, 5, 3, 3, 3]],

        [[7, 9, 8, 8, 3, 3, 7, 8, 8, 5, 3, 3, 5],
        [6, 9, 7, 7,3, 4, 7, 5, 9, 9, 3, 6, 7],
        [7, 9, 6, 6, 3, 4, 6, 4, 7, 4, 3, 3, 3],
        [6, 9, 8, 6, 5, 4, 7, 8, 7, 5, 4, 3, 4], 
        [6, 7, 8, 7, 3, 6, 6, 7, 9, 5, 3, 7, 3], 
        [6, 7, 9, 5, 3, 3, 6, 5, 5, 3, 4, 3, 2],
        [5, 7, 6, 5, 4, 3, 4, 5, 6, 5, 3, 3, 5]]]
    week_name = ["Week1", "Week2", "Week3", "Week4"]
    days_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hour_name = ["8h-9h", "9h-10h", "10h-11h", "11h-12h", "12h-13h", "13h-14h", "14h-15h", "15h-16h", "16h-17h", "17h-18h", "18h-19h", "19h-20h", "20h-21h"]
    shifts = [[1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0], #C1
        [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0], #C2
        [0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0], #C3
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0], #C4
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1], #C5
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]] #C6
    shift_name = ["C1", "C2", "C3", "C4", "C5", "C6"]

    rs1 = [[solveQ1(day = days[w][i], shift_name=shift_name, shifts=shifts, hour_name=hour_name) for i in range(len(days_name))] for w in range(len(week_name))]
    # Number of CSR required each day (ncwj, w = 1, 2, ..., 4, j = 1, 2, ..., 7)
    csr_required_each_day = [[sum([rs1[w][j][k] for k in range(len(shift_name))]) for j in range(len(days_name))] for w in range(len(week_name))]
    # Number of empty slots each week (new, w = 1, 2, ..., 4)
    empty_slots = [len(days_name) * max(csr_required_each_day[w]) - sum(csr_required_each_day[w]) for w in range(len(week_name))]
    rs2 = [solveQ2(days_name=days_name, empty_slots=empty_slots[w], csr_required_each_day=csr_required_each_day[w]) for w in range(len(week_name))]

    # Number of CSR required each shift each week (ncwk, w = 1, 2, ... 4, k = 1, 2, ..., 6)
    csr_required_each_shift = [[sum([rs1[w][j][k] for j in range(len(days_name))]) for k in range(len(shift_name))] for w in range(len(week_name))]
    # Number of CSR required in a week nc
    csr_required = max([rs2[w] + max(csr_required_each_day[w]) for w in range(len(week_name))])
    # CSR names (CSR1, CSR2, ..., CSRnc)
    csr_name = ["CSR" + str(i + 1) for i in range(0, csr_required)]
    rs3 = [solveQ3(shift_name=shift_name, shifts=shifts, hour_name=hour_name, csr_name=csr_name, days=days[w], days_name=days_name, csr_required=csr_required, csr_required_each_shift=csr_required_each_shift[w]) for w in range(len(week_name))]
    
    days_off_week_plan = [[1 - sum([rs3[w][i][6][k] for k in range(len(shift_name))]) for i in range(len(csr_name))] for w in range(len(week_name))]
    # Number of days off in all week
    days_off = sum(sum(days_off_week_plan[w]) for w in range(len(week_name)))

    plan_name = ["Plan" + str(i + 1) for i in range(0, len(csr_name))]
    rs4 = solveQ4_2(csr_name=csr_name, week_name=week_name, plan_name=plan_name, days_off_week_plan=days_off_week_plan, days_off=days_off)

    def getPlanName(arr):
        for i in range(len(arr)):
            if arr[i] == 1:
                return plan_name[i]
        return "EM"
    
    def getPlanIndex(arr):
        for i in range(len(arr)):
            if arr[i] == 1:
                return i
        return -1
    
    def getShiftName(arr):
        for i in range(len(arr)):
            if arr[i] == 1:
                return shift_name[i]
        return "EM"
    
    def getPlanContent(arr):
        return " ".join(getShiftName(arr[i]) for i in range(len(arr)))

    
    print("Result Q4 (2): ")
    for w in range(len(week_name)):
        print(week_name[w])
        for i in range(len(csr_name)):
            print(csr_name[i] + " " + getPlanName(rs4[i][w]) + " " + getPlanContent(rs3[w][getPlanIndex(rs4[i][w])]))
        print()


if __name__ == "__main__":
    #Q1_2_3()
    #Q4_1()
    Q4_2()
