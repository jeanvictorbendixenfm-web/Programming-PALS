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


"""Thickness fitting - Updated to use Numerical Physics Engine."""

# Import the physics engines
from pals_analysis.physics.implantation import makhov_profile
from pals_analysis.physics.annihilation import calculate_annihilation_profile

def numerical_S_curve(energies, d_ox, w, s_surf, s_bulk, model='graded'):
    """
    Generates S(E) curve using the full numerical simulation.
    This captures the 'bump' caused by interface trapping.
    """
    # 1. Define Geometry / Constants
    # You might want to move these to config or pass them as args
    layers = [
        {'thickness': d_ox, 'density': 5.24, 'L_diff': 30},   # Oxide
        {'thickness': 2000, 'density': 8.00, 'L_diff': 150}   # Steel (Substrate)
    ]
    
    z_max = 2000 # nm
    z_grid = np.linspace(0, z_max, 500) # 500 points is usually enough for fitting
    
    # 2. Build S-Parameter Map (S(z))
    # If density/diffusion is graded, S-parameter should likely grade too
    s_map = np.zeros_like(z_grid)
    if model == 'graded':
        s_map = s_surf + (s_bulk - s_surf) / (1 + np.exp(-(z_grid - d_ox) / (w/4.0)))
    else:
        s_map = np.where(z_grid <= d_ox, s_surf, s_bulk)

    # 3. Run Simulation for each Energy
    s_values = []
    
    # Ensure energies is iterable
    energies = np.atleast_1d(energies)
    
    for E in energies:
        # A. Implantation
        p_z = makhov_profile(z_grid, E, layers, model=model, w=w)
        
        # B. Diffusion
        c_z = calculate_annihilation_profile(z_grid, p_z, layers, model=model, w=w)
        
        # C. Calculate S = Integral( C(z) * S(z) )
        s_point = np.trapezoid(c_z * s_map, z_grid)
        s_values.append(s_point)
        
    return np.array(s_values)

def solve_graded_model(energies, s_exp, s_err=None):
    """
    Fits the experimental data using the Graded Interface Model.
    Fits: Thickness (d_ox), Interface Width (w), and Surface S (s_surf).
    """
    print("Running Numerical Graded Solver... (This may take a few seconds)")
    
    # Wrapper for curve_fit to freeze parameters we don't want to fit (like S_bulk)
    def fit_func(E, d, w, s_s):
        # We fix S_bulk to 0.520 (Steel) for stability, or fit it if you prefer
        return numerical_S_curve(E, d_ox=d, w=w, s_surf=s_s, s_bulk=0.520, model='graded')

    # Initial Guesses: d=150nm, width=20nm, S_surf=0.575
    p0 = [150.0, 20.0, 0.575]
    
    # Bounds: d(10-1000), w(1-100), S(0-1)
    bounds = ([10, 1, 0.4], [1000, 200, 0.7])
    
    popt, pcov = curve_fit(fit_func, energies, s_exp, p0=p0, bounds=bounds, sigma=s_err, maxfev=10000)
    
    d_fit, w_fit, s_surf_fit = popt
    return d_fit, w_fit, s_surf_fit