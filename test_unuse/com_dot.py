from test_unuse.get_Ap import get_Ap
from scipy.optimize import linprog


y = [60]
Ap = get_Ap(41500, 6000)
print(len(Ap)*len(Ap[0]))

