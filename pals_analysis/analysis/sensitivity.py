"""Sensitivity analysis and parameter studies."""

import numpy as np
from ..physics.implantation import makhov_profile
from ..physics.annihilation import calculate_annihilation_profile
from .thickness_solver import solve_for_thickness


def study_interface_width(energies, s_exp, base_layers, width_values):
    """
    Study effect of interface width on fitted thickness.
    
    Parameters
    ----------
    energies : array
        Experimental energies
    s_exp : array
        Experimental S-parameters
    base_layers : list
        Base layer configuration
    width_values : array
        Interface widths to test (nm)
    
    Returns
    -------
    dict
        Results containing fitted thicknesses for each width
    """
    from ..physics.implantation import get_graded_density
    
    results = {
        'widths': width_values,
        'thicknesses': [],
        's_surfaces': []
    }
    
    for w in width_values:
        # Simulate with graded interface
        z = np.linspace(0, 600, 300)
        s_curves = []
        
        for e in energies:
            p_z = makhov_profile(z, e, base_layers)
            c_z = calculate_annihilation_profile(z, p_z, base_layers)
            
            # Graded S(z) profile
            d_ox = base_layers[0]['thickness']
            s_z = 0.52 + (0.575 - 0.52) / (1 + np.exp((z - d_ox) / (w/4)))
            s_val = np.trapezoid(c_z * s_z, z)
            s_curves.append(s_val)
        
        # Fit the simulated data
        d_fit, s_fit = solve_for_thickness(energies, np.array(s_curves))
        results['thicknesses'].append(d_fit)
        results['s_surfaces'].append(s_fit)
    
    results['thicknesses'] = np.array(results['thicknesses'])
    results['s_surfaces'] = np.array(results['s_surfaces'])
    
    return results


def study_diffusion_length(energy, base_layers, L_values, z_max=600):
    """
    Study effect of diffusion length on annihilation profile.
    
    Parameters
    ----------
    energy : float
        Beam energy (keV)
    base_layers : list
        Base layer configuration
    L_values : array
        Diffusion lengths to test (nm)
    z_max : float
        Maximum depth (nm)
    
    Returns
    -------
    dict
        Results containing profiles for each L value
    """
    z = np.linspace(0, z_max, 300)
    
    results = {
        'z': z,
        'L_values': L_values,
        'profiles': []
    }
    
    # Calculate implantation once
    p_z = makhov_profile(z, energy, base_layers)
    
    for L in L_values:
        # Modify diffusion length
        layers_modified = []
        for layer in base_layers:
            layer_copy = layer.copy()
            layer_copy['L_diff'] = L
            layers_modified.append(layer_copy)
        
        c_z = calculate_annihilation_profile(z, p_z, layers_modified)
        results['profiles'].append(c_z)
    
    results['profiles'] = np.array(results['profiles'])
    
    return results


def study_layer_thickness(energies, thickness_values, base_layers):
    """
    Study effect of oxide thickness on S-parameter curve.
    
    Parameters
    ----------
    energies : array
        Energy values (keV)
    thickness_values : array
        Oxide thicknesses to test (nm)
    base_layers : list
        Base layer configuration
    
    Returns
    -------
    dict
        Results containing S-curves for each thickness
    """
    results = {
        'energies': energies,
        'thicknesses': thickness_values,
        's_curves': []
    }
    
    z = np.linspace(0, 600, 300)
    
    for d_ox in thickness_values:
        # Modify thickness
        layers_modified = base_layers.copy()
        layers_modified[0]['thickness'] = d_ox
        
        s_curve = []
        for e in energies:
            p_z = makhov_profile(z, e, layers_modified)
            c_z = calculate_annihilation_profile(z, p_z, layers_modified)
            
            # Sharp interface S(z)
            s_z = np.where(z <= d_ox, 0.575, 0.52)
            s_val = np.trapezoid(c_z * s_z, z)
            s_curve.append(s_val)
        
        results['s_curves'].append(s_curve)
    
    results['s_curves'] = np.array(results['s_curves'])
    
    return results


def monte_carlo_uncertainty(energies, s_exp, s_err, n_iterations=1000):
    """
    Estimate uncertainty using Monte Carlo sampling.
    
    Parameters
    ----------
    energies : array
        Experimental energies
    s_exp : array
        Experimental S-parameters
    s_err : array
        Uncertainties in S-parameters
    n_iterations : int
        Number of Monte Carlo samples
    
    Returns
    -------
    dict
        Results with distributions of fitted parameters
    """
    thicknesses = []
    s_surfaces = []
    
    for i in range(n_iterations):
        # Add noise to data
        s_sample = s_exp + np.random.normal(0, s_err)
        
        try:
            d_fit, s_fit = solve_for_thickness(energies, s_sample)
            thicknesses.append(d_fit)
            s_surfaces.append(s_fit)
        except:
            continue  # Skip failed fits
    
    thicknesses = np.array(thicknesses)
    s_surfaces = np.array(s_surfaces)
    
    return {
        'thickness_mean': np.mean(thicknesses),
        'thickness_std': np.std(thicknesses),
        'thickness_values': thicknesses,
        's_surface_mean': np.mean(s_surfaces),
        's_surface_std': np.std(s_surfaces),
        's_surface_values': s_surfaces
    }