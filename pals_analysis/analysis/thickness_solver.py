"""Thickness fitting - from your pals-solver.ipynb."""

import numpy as np
from scipy.optimize import curve_fit


def theoretical_S_curve(E, d_ox, S_surf):
    """YOUR implementation from pals-solver.ipynb Cell 1."""
    RHO_OX = 5.24
    A, N = 4.0, 1.6
    S_BULK_STEEL = 0.52
    
    E = np.atleast_1d(E)
    mass_capacity = A * (E**N)
    oxide_mass_limit = RHO_OX * d_ox * 0.1
    xi_0 = (A * E**N) / 0.886
    fraction_oxide = 1 - np.exp(-(oxide_mass_limit / xi_0)**2)
    
    s_pred = (fraction_oxide * S_surf) + ((1 - fraction_oxide) * S_BULK_STEEL)
    return s_pred if len(s_pred) > 1 else float(s_pred[0])


def solve_for_thickness(energies, s_exp):
    """YOUR implementation from pals-solver.ipynb Cell 1."""
    popt, pcov = curve_fit(theoretical_S_curve, energies, s_exp, p0=[20, 0.54])
    return popt[0], popt[1]  # d_ox, S_surf


def fit_model(E, d_ox, S_ox):
    """YOUR implementation from pals-solver.ipynb Cell 2."""
    RHO_OX = 5.24
    A, N = 4.0, 1.6
    S_BULK_STEEL = 0.52
    
    E = np.atleast_1d(E)
    mass_capacity = A * (E**N)
    oxide_mass_limit = RHO_OX * d_ox * 0.1
    xi_0 = mass_capacity / 0.886
    f_ox = 1 - np.exp(-(oxide_mass_limit / xi_0)**2)
    
    s_pred = f_ox * S_ox + (1 - f_ox) * S_BULK_STEEL
    return s_pred if len(s_pred) > 1 else float(s_pred[0])