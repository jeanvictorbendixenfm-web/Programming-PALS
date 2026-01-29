"""Thickness fitting - from your pals-solver.ipynb."""

import numpy as np
from scipy.optimize import curve_fit
from pals_analysis.physics.implantation import makhov_profile
from pals_analysis.physics.annihilation import calculate_annihilation_profile


def theoretical_S_curve(E, d_ox, S_surf, RHO_OX=5.24, S_BULK_STEEL=0.52):
    """
    Calculate theoretical S-parameter curve for a given energy, oxide
    thickness and surface S-parameter.

    input:
    - E : float or array
    - d_ox : float
    - S_surf : float

    """
    RHO_OX = 5.24
    A, N = 40, 1.6, # microgram cm^-2 keV^-N
    S_BULK_STEEL = 0.52
    
    # Ensure E is array for consistent calculations
    E = np.atleast_1d(E), # keV
    
    # Oxide mass limit (g/cm2)
    # Conversion rate to ensure fraction.
    d_ox_micro =  d_ox * 0.1
    
    # 
    z_0 = (A * E**N) / (RHO_OX * 0.886) # Units in markdown above.

    # The fraction of positrons present in the oxide layer.
    fraction_oxide = 1 - np.exp(-(d_ox_micro / z_0)**2)
    
    # Predicted S-parameter. It simply linerarly combines the contributions from
    # each S-parameter in the layers. 
    s_pred = (fraction_oxide * S_surf) + ((1 - fraction_oxide) * S_BULK_STEEL)
    return s_pred if len(s_pred) > 1 else float(s_pred[0])


def solve_for_thickness(energies, s_exp):
    """
    This function finds the d_ox and S_surf that fits the given experimental data
    with a S-curve.

    input:
    - energies : array, NumPy, length energies = s_exp
    - s_exp : array, NumPy
    
    """

    # It fets a theoretical S-curve to it and estimates the thickness of the oxides
    # and the S-parameter at the surface.
    popt, pcov = curve_fit(theoretical_S_curve, energies, s_exp, p0=[20, 0.54])
    return popt[0], popt[1]  # d_ox, S_surf


def numerical_S_curve(energies, d_ox, w, s_surf, s_bulk, model='graded'):
    """
    Generates S(E) curve using the full numerical simulation.
    This captures the 'bump' caused by interface trapping.
    """
    # Defining Geometry / Constants
    layers = [
        {'thickness': d_ox, 'density': 5.24, 'L_diff': 30},   # Oxide
        {'thickness': 2000, 'density': 8.00, 'L_diff': 150}   # Steel (Substrate)
    ]
    
    z_max = 2000 # nm
    z_grid = np.linspace(0, z_max, 1000) # Max is changeable.
    
    # S-Parameter Map, S(z)
    s_map = np.zeros_like(z_grid)


    if model == 'graded':
        s_map = s_surf + (s_bulk - s_surf) / (1 + np.exp(-(z_grid - d_ox) / (w/4.0)))
    if model == 'layered':
        # Here we attribute S-parameters solemnly based on layer.
        s_map = np.where(z_grid <= d_ox, s_surf, s_bulk)
    else:
        # Added this cause honestly so many things can go wrong.
        raise ValueError(f"Unknown model type: {model}")

    # Generate an empty s_value array for simulation.
    s_values = []
    
    # Ensure energies is iterable
    energies = np.atleast_1d(energies)
    
    for E in energies:
        # We define the profile for each energy in the grid, taken
        # into account the model and layers.
        p_z = makhov_profile(z_grid, E, layers, model=model, w=w)
        
        # Diffusion is applied to get the annihilation profile using the 
        # distribution of positron in each cell. 
        c_z = calculate_annihilation_profile(z_grid, p_z, layers, model=model, w=w)
        
        # S = Integral( C(z) * S(z) )
        # This reassigns the S-parameter to each cell now that positrons have 
        # implanted and diffused.
        s_point = np.trapezoid(c_z * s_map, z_grid)
        s_values.append(s_point)
        
    return np.array(s_values)

def solve_graded_model(energies, s_exp, s_err=None):
    """
    Fits the experimental data using the Graded Interface Model.
    Fits: Thickness (d_ox), Interface Width (w), and Surface S (s_surf).
    """
    print("Fitting...")
    
    # This just wraps the numerical S-curve to be used in curve_fit
    def fit_func(E, d, w, s_s):
        # We fix S_bulk to 0.520 (Steel) for stability, or fit it if you prefer
        return numerical_S_curve(E, d_ox=d, w=w, s_surf=s_s, s_bulk=0.520, model='graded')

    # Initial values: d=150nm, width=20nm, S_surf=0.575
    p0 = [100.0, 15.0, 0.575]
    
    # Bounds: d(10-1000), w(1-100), S(0-1)
    # These prevent divergence or unphysical fits.
    bounds = ([10, 1, 0.4], [1000, 200, 0.7])
    
    popt, pcov = curve_fit(fit_func, energies, s_exp, p0=p0, bounds=bounds, sigma=s_err, maxfev=10000)
    
    d_fit, w_fit, s_surf_fit = popt
    return d_fit, w_fit, s_surf_fit

