"""Implantation functions - from your pals.ipynb."""

import numpy as np


"""Implantation functions - Updated for Graded Interface."""

import numpy as np

def makhov_profile(z_grid, energy_kev, layers, model='sharp', w=10.0):
    """
    Calculates Implantation Profile P(z).
    Supports 'sharp' (step function) and 'graded' (sigmoid) interfaces.
    """
    n, m, A = 1.6, 2.0, 4.0
    
    z_grid = np.asarray(z_grid)
    densities = np.zeros_like(z_grid)
    mass_depth = np.zeros_like(z_grid)
    
    # 1. Build Density Map
    if model == 'graded' and len(layers) >= 2:
        # Graded: Sigmoid transition between Layer 0 and Layer 1
        d_ox = layers[0]['thickness']
        rho_ox = layers[0]['density']
        rho_sub = layers[1]['density']
        
        # Sigmoid function centered at d_ox with width w
        # The factor 4 ensures 'w' represents roughly the 10%-90% transition width
        densities = rho_ox + (rho_sub - rho_ox) / (1 + np.exp(-(z_grid - d_ox) / (w/4.0)))
    else:
        # Sharp: Step function (Default)
        curr_z = 0
        for l in layers:
            mask = (z_grid >= curr_z) & (z_grid <= curr_z + l['thickness'])
            densities[mask] = l['density']
            curr_z += l['thickness']

    # 2. Calculate Mass Depth (Cumulative Density)
    # We integrate density * dz to get depth in g/cm^2
    dz = z_grid[1] - z_grid[0]
    # np.cumsum is faster and accurate enough for dense grids
    # 0.1 conversion factor if density is g/cm3 and z is nm -> microgram/cm2
    mass_depth = np.cumsum(densities * dz) * 0.1 
    
    # 3. Calculate Makhov Profile
    # Ensure energy is not zero to avoid division errors
    eff_E = np.maximum(energy_kev, 0.01)
    xi_0 = (A * eff_E**n) / 0.886
    
    # The Makhov formula P(z) = dP/dz
    p_xi = (m * mass_depth**(m-1) / xi_0**m) * np.exp(-(mass_depth/xi_0)**m)
    
    # Convert P(mass) to P(z) by multiplying by density (Jacobian)
    p_z = p_xi * densities
    
    # Normalize
    integral = np.trapezoid(p_z, z_grid)
    return p_z / integral if integral > 0 else p_z


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