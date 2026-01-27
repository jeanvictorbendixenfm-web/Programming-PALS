"""Implantation functions - from your pals.ipynb."""

import numpy as np


def makhov_profile(z_grid, energy_kev, layers):
    """
    YOUR implementation from pals.ipynb Cell 4.
    
    Parameters
    ----------
    z_grid : array
        Depth points (nm)
    energy_kev : float
        Beam energy (keV)
    layers : list of dict
        Each with 'thickness' and 'density'
    
    Returns
    -------
    array
        Normalized implantation profile P(z)
    """
    n, m, A = 1.6, 2.0, 4.0
    
    z_grid = np.asarray(z_grid)
    densities = np.zeros_like(z_grid)
    mass_depth = np.zeros_like(z_grid)
    
    curr_z = 0
    acc_mass = 0
    
    for l in layers:
        mask = (z_grid >= curr_z) & (z_grid <= curr_z + l['thickness'])
        densities[mask] = l['density']
        mass_depth[mask] = acc_mass + (z_grid[mask] - curr_z) * l['density'] * 0.1
        acc_mass += l['thickness'] * l['density'] * 0.1
        curr_z += l['thickness']
    
    xi_0 = (A * max(energy_kev, 0.01)**n) / 0.886
    p_z = ((m * mass_depth**(m-1) / xi_0**m) * np.exp(-(mass_depth/xi_0)**m)) * densities
    
    return p_z / np.trapezoid(p_z, z_grid)


def energy_to_mean_depth(energies, d_ox, rho_ox, rho_sub):
    """YOUR implementation from pals.ipynb Cell 6."""
    A, n = 4.0, 1.6
    mean_depths = []
    
    for E in energies:
        mass_capacity = A * (E**n)
        oxide_mass_limit = rho_ox * d_ox * 0.1
        
        if mass_capacity <= oxide_mass_limit:
            z_bar = mass_capacity / (rho_ox * 0.1)
        else:
            remaining_mass = mass_capacity - oxide_mass_limit
            z_bar = d_ox + remaining_mass / (rho_sub * 0.1)
        
        mean_depths.append(z_bar)
    
    return np.array(mean_depths)


def get_graded_density(z, d_ox, w, rho_ox, rho_sub):
    """YOUR implementation from pals.ipynb Cell 8."""
    return rho_ox + (rho_sub - rho_ox) / (1 + np.exp(-(z - d_ox) / (w/4)))