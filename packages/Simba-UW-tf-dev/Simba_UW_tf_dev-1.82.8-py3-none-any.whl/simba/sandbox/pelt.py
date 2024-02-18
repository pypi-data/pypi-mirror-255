import numpy as np
from numba import jit
import numba


def pelt_changepy(cost, length, pen=None):
    """ PELT algorithm to compute changepoints in time series

    Ported from:
        https://github.com/STOR-i/Changepoints.jl
        https://github.com/rkillick/changepoint/
    Reference:
        Killick R, Fearnhead P, Eckley IA (2012) Optimal detection
            of changepoints with a linear computational cost, JASA
            107(500), 1590-1598

    Args:
        cost (function): cost function, with the following signature,
            (int, int) -> float
            where the parameters are the start index, and the second
            the last index of the segment to compute the cost.
        length (int): Data size
        pen (float, optional): defaults to log(n)
    Returns:
        (:obj:`list` of int): List with the indexes of changepoints
    """
    if pen is None:
        pen = np.log(length)

    F = np.zeros(length + 1)
    R = np.array([0], dtype=np.int64)
    candidates = np.zeros(length + 1, dtype=np.int64)

    F[0] = -pen

    for tstar in range(2, length + 1):
        cpt_cands = R
        seg_costs = np.zeros(len(cpt_cands))
        for i in range(0, len(cpt_cands)):
            seg_costs[i] = cost(cpt_cands[i], tstar)

        F_cost = F[cpt_cands] + seg_costs
        F[tstar], tau = find_min(F_cost, pen)
        candidates[tstar] = cpt_cands[tau]

        ineq_prune = [val < F[tstar] for val in F_cost]
        R = [cpt_cands[j] for j, val in enumerate(ineq_prune) if val]
        R.append(tstar - 1)
        R = np.array(R, dtype=np.int64)

    last = candidates[-1]
    changepoints = [last]
    while last > 0:
        last = candidates[last]
        changepoints.append(last)

    return sorted(changepoints)

@jit(nopython=True)
def normal_mean(data, variance):
    i_variance_2 = 1 / (variance ** 2)
    cmm = numba.typed.List([0.0])
    # cmm = [0.0]
    cmm.extend(numba.typed.List(np.cumsum(data).astype(np.float64)))
    print(cmm)
    cmm2 = [0.0]
    cmm2.extend(np.cumsum(np.abs(data)))

    def cost(start, end):
        cmm2_diff = cmm2[end] - cmm2[start]
        cmm_diff = pow(cmm[end] - cmm[start], 2)
        i_diff = end - start
        diff = cmm2_diff - cmm_diff
        return (diff / i_diff) * i_variance_2

    return cost



@jit(nopython=True)
def pelt(data: np.ndarray, cost_func=None, penality= None):

    def find_min(arr, val=0.0):
        return min(arr) + val, np.argmin(arr)

    length = data.shape[0]
    if penality is None: penality = np.log(length)
    if cost_func is None: cost_func = normal_mean(data, np.var(data))
    F = np.zeros(length + 1)
    F[0] = -penality
    R = np.array([0], dtype=np.int64)
    candidates = np.zeros(length + 1, dtype=np.int64)

    for tstar in range(2, length + 1):
        cpt_cands = R
        seg_costs = np.zeros(len(cpt_cands))
        for i in range(0, len(cpt_cands)):
            seg_costs[i] = cost_func(cpt_cands[i], tstar)
        F_cost = F[cpt_cands] + seg_costs
        F[tstar], tau = find_min(F_cost, penality)
        candidates[tstar] = cpt_cands[tau]

        ineq_prune = [val < F[tstar] for val in F_cost]
        R = [cpt_cands[j] for j, val in enumerate(ineq_prune) if val]
        R.append(tstar - 1)
        R = np.array(R, dtype=np.int64)

    last = candidates[-1]
    changepoints = [last]
    while last > 0:
        last = candidates[last]
        changepoints.append(last)
    return sorted(changepoints)



data_a = np.random.normal(0, 0.1, 100)
data_b = np.random.normal(10, 0.1, 100)
data = np.append(data_a, data_b)
cp_mine = pelt(data=data)
print(cp_mine)