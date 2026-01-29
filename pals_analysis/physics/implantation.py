import numpy as np


"""Implantation functions """

import numpy as np

def makhov_profile(z_grid, energy_kev, layers, model='sharp', w=10.0):
    """
    Calculates Implantation Profile P(z).
    This is based on the Makhov profile and adapted here to multiple layers.
    """

    # Basic parameters for Makhov Model. 2 is for positrons
    N, m, A = 1.6, 2.0, 4.0
    
    # Generates appropriate arrays.
    z_grid = np.asarray(z_grid)
    densities = np.zeros_like(z_grid)
    
    # 1. Build Density Map
    if model == 'graded' and len(layers) >= 2:
        # Graded: Sigmoid transition between Layer 0 and Layer 1
        # NEEDS ADJUSTMENT FOR MORE LAYERS!
        d_ox = layers[0]['thickness']
        rho_ox = layers[0]['density']
        rho_sub = layers[1]['density']
        
        # Sigmoid function centered at d_ox with width w
        # The factor 4 ensures 'w' represents roughly the 12%-88% transition width
        # of the sigmoid function.
        densities = rho_ox + (rho_sub - rho_ox) / (1 + np.exp(-(z_grid - d_ox) / (w/4.0)))
    else:
        # Step function density profile.
        # We go through each layer by saying "everything is this layer is this
        # density" and then we move on to the next layer.
        # This function supports >2 layers.
        curr_z = 0
        for l in layers:
            mask = (z_grid >= curr_z) & (z_grid <= curr_z + l['thickness'])
            densities[mask] = l['density']
            curr_z += l['thickness']

    # 2. Calculate Mass Depth (Cumulative Density)
    # We integrate density * dz to get depth in g/cm^2
    dz = z_grid[1] - z_grid[0]
    # np.cumsum is fast and works for dense grids.

    # This results in the mass depth.
    xi = np.cumsum(densities * dz) * 0.1 
     # 0.1 conversion factor so that resulting mass in units mu g /cm^2. 
    
    # 3. Calculate Makhov Profile
    # Ensure energy is not zero to avoid division errors
    eff_E = np.maximum(energy_kev, 0.01)

    # We convert z_0 to xi_0 which is similar to a mass distribution,
    xi_0 = (A * eff_E**N) / 0.886
    
    # The Makhov formula P(z) = dP/dz
    p_xi = (m * xi**(m-1) / xi_0**m) * np.exp(-(xi/xi_0)**m)
    
    # Convert P(mass) to P(z) by multiplying by density (Jacobian)
    # P(z) d(z) = P(xi) d(xi), so P(z) = P(xi) * d(xi)/d(z) = P(xi) * densities
    p_z = p_xi * densities
    
    # Normalize
    integral = np.trapezoid(p_z, z_grid)

    if integral <= 0:
        print("Warning: Makhov profile integral is non-positive, check parameters.")
    
    # Returns Makhov profile
    return p_z / integral if integral > 0 else p_z


def energy_to_mean_depth(energies, d_ox, rho_ox, rho_sub):
    """
    This function calculates the mean implantation depth z_bar 
    based on a simplified two-layer model (oxide and substrate).
    It uses the empirical relation for the mean depth.
    NEEDS ADJUSTMENT FOR MORE LAYERS!

    """
    A, N = 4.0, 1.6
    mean_depths = []
    
    for E in energies:
        mass_capacity = A * (E**N)
        # Again convert to avoid issues with units. It makes it easier
        # to correct apply the mean depth equation for each energy and in
        # each layer.
        d_ox_micro = rho_ox * d_ox * 0.1
        
        if mass_capacity <= d_ox_micro:
            z_bar = mass_capacity / (rho_ox * 0.1)
        else:
            remaining_mass = mass_capacity - d_ox_micro
            z_bar = d_ox + remaining_mass / (rho_sub * 0.1)
        
        mean_depths.append(z_bar)
    
    return np.array(mean_depths)


def get_graded_density(z, d_ox, w, rho_ox, rho_sub):
    """
    This function returns a graded density profile using a sigmoid function.
    NEEDS ADJUSTMENT FOR MORE LAYERS!
    """
    return rho_ox + (rho_sub - rho_ox) / (1 + np.exp(-(z - d_ox) / (w/4)))