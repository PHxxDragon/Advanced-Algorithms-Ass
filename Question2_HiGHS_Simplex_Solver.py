import numpy as np
from scipy import optimize

Array = np.array

# Customer Service Representatives (CSRs)
I = [0]

# Days
J = [[6,9,9,8,3,3,7,8,8,5,3,3,2],       # Monday
        [6,10,7,7,3,4,7,5,9,5,3,4,3],   # Tuesday
        [7,9,9,6,3,4,6,8,7,4,3,3,3],    # Wednesday
        [6,9,8,6,4,4,5,8,7,5,4,3,4],    # Thursday
        [6,7,8,7,3,5,6,7,6,5,3,3,3],    # Friday
        [6,9,9,4,3,3,4,5,5,5,3,3,2],    # Saturday
        [5,7,6,5,4,3,4,5,6,5,3,3,3]]    # Sunday

# Shifts
K = [[1,1,1,1,0,1,1,1,1,0,0,0,0],       # C1
        [0,1,1,1,0,1,1,1,1,1,0,0,0],    # C2
        [0,0,1,1,1,0,1,1,1,1,1,0,0],    # C3
        [0,0,0,1,1,1,1,1,0,1,1,1,0],    # C4
        [0,0,0,0,1,1,1,1,1,0,1,1,1],    # C5
        [1,1,1,1,0,0,0,0,0,1,1,1,1]]    # C6

# Periods
T = ['8h-9h','9h-10h','10h-11h','11h-12h','12h-13h','13h-14h','14h-15h','15h-16h','16h-17h','17h-18h','18h-19h','19h-20h','20h-21h']   

Q1_c = np.full(len(K), 1)
N = np.zeros((len(J),len(K)), dtype = int)
NC = np.zeros(len(J), dtype = int)

# xk_bounds = np.full(len(K), tuple((1,None)))
x0_bounds = (0,None)
x1_bounds = (0,None)
x2_bounds = (0,None)
x3_bounds = (0,None)
x4_bounds = (0,None)
x5_bounds = (0,None)

xk_bounds = [x0_bounds, x1_bounds, x2_bounds, x3_bounds, x4_bounds, x5_bounds]

for j in range(len(J)):
    Q1_A_ub = np.zeros((len(T),len(K)),dtype=int)
    Q1_b_ub = np.zeros(len(T),dtype=int)

    for t in range(len(T)):
        d_t = J[j][t]
        Q1_b_ub[t] = -d_t

        for k in range(len(K)):
            s_kt = K[k][t]
            Q1_A_ub[t][k] = -s_kt
    
    resolution = optimize.linprog(Q1_c, A_ub = Q1_A_ub, b_ub = Q1_b_ub, bounds = xk_bounds, options = {"disp": True}, method = 'highs', integrality=[1, 1, 1, 1, 1, 1]) #integrality=[1, 1, 1, 1, 1, 1]
    N[j] = resolution.x
    NC[j] = np.sum(N[j])
    pass

# Work days per week
nd = len(J)
ne = nd * np.max(NC) - np.sum(NC)

# Number of additional CSR needed when each CSR has 1 day off per week
x = np.ceil((np.max(NC) - ne) / (nd - 1))

# Total CSR needed per week
nc = max(NC) + x

pass


# for k in range(len(K)):
#     pass

# constraints = optimize.LinearConstraint(,lb=)

# min_csr_needed

# s_kt_bound = optimize.Bounds(0, 1)
# s_kt_integrality = np.full_like()
# resolution = optimize.linprog(c, A_ub=A, b_ub=b, bounds=(x0_bounds, x1_bounds), integrality=[1, 1, 1, 1, 1, 1], options={"disp": True})