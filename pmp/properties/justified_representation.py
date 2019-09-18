"""
For definitions of Justified Representation, Extended Justified Representation and Proportional Justified Representation
check this paper: https://fpt.akt.tu-berlin.de/publications/skowron_ejr_poly.pdf
"""
import numpy as np
from itertools import product, chain

from ..utils.ilp import *


def has_approvaed_candidate(preference, committee):
    return len(preference.approved & committee) > 0


def justified_representation(profile, committee):
    k = len(committee)
    n = len(profile.preferences)
    m = len(profile.candidates)
    quota = int(n / k)
    justified = True

    appearances = np.zeros(m + 1, dtype=int)
    voters_without_approved_candidate = [v for v in profile.preferences if not has_approvaed_candidate(v, committee)]

    for v in voters_without_approved_candidate:
        for c in v.approved:
            appearances[c] += 1
            if appearances[c] >= quota:
                justified = False
                break
        if not justified:
            break

    return justified


def extended_justified_representation(profile, committee):
    """
    ILP formulation based on paper:
    https://www.ijcai.org/proceedings/2019/0016.pdf
    """
    m = len(profile.candidates)
    n = len(profile.preferences)
    k = len(committee)
    all_ij = np.fromiter(chain.from_iterable(product(range(n), range(m))), int, n * m * 2)
    all_ij.shape = n * m, 2

    ok_for_all_l = True
    for l in range(1, k + 1):
        model = Model()

        # Vi - ith voter is in counterexample group X
        v = ['v{}'.format(i) for i in range(n)]
        v_lb = np.zeros(n)
        v_ub = np.ones(n)
        model.add_variables(v, v_lb, v_ub)

        # Uj - jth candidate is approved by all X members
        u = ['u{}'.format(i) for i in range(m)]
        u_lb = np.zeros(m)
        u_ub = np.ones(m)
        model.add_variables(u, u_lb, u_ub)

        # Objective - does not have impact on quality
        model.set_objective_sense(Objective.maximize)
        model.set_objective(u, np.ones(m))

        # Constraint1 - Ei vi = l * n / k
        # There are l * n / k voters in the group
        vi = np.ones(n)
        model.add_constraint(v, vi, Sense.eq, l * int(n / k))

        # Constraint2 - Ej uj = l
        # Number of candidates
        ui = np.ones(m)
        model.add_constraint(u, ui, Sense.eq, l)

        # Constraint3 - Vij uj + vi <= 1 + [j <- Ai]
        # Each of selected voters approves all of selected candidates
        c3_variables = [['u{}'.format(j), 'v{}'.format(i)] for (i, j) in all_ij]
        c3_coefficients = np.tile(np.array((1., 1.)), n * m)
        c3_coefficients.shape = n * m, 2
        c3_senses = np.full(n * m, Sense.lt)
        c3_rights = [
            1 + (1 if j + 1 in profile.preferences[i].approved else 0) for (i, j) in all_ij
        ]
        model.add_constraints(c3_variables, c3_coefficients, c3_senses, c3_rights)

        # Constraint4 - Vi  m * vi < m + l - (E(j <- W) [j <- Ai])
        # W - winning committee
        c4_variables = [['v{}'.format(i)] for i in range(n)]
        c4_coefficients = np.full(n, m * 1.0)
        c4_coefficients.shape = n, 1
        c4_senses = np.full(n, Sense.lt)
        c4_rights = [m + l - len(committee & profile.preferences[i].approved) - 1 for i in range(n)]
        model.add_constraints(c4_variables, c4_coefficients, c4_senses, c4_rights)

        # End of definition

        model.solve()

        solution_type, _ = model.get_solution_status()
        if solution_type == SolutionType.feasible:
            ok_for_all_l = False
            break

    return ok_for_all_l


def proportional_justified_representation(profile, committee):
    return False
