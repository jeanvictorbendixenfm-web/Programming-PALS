"""Annihilation functions - from your pals.ipynb."""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve


def calculate_annihilation_profile(z_grid, p_z, layers):
    """
    YOUR implementation from pals.ipynb Cell 4.
    
    Parameters
    ----------
    z_grid : array
        Depth points (nm)
    p_z : array
        Implantation profile from makhov_profile
    layers : list of dict
        Each with 'thickness' and 'L_diff'
    
    Returns
    -------
    array
        Normalized annihilation profile C(z)
    """
    z_grid = np.asarray(z_grid)
    p_z = np.asarray(p_z)
    dz = z_grid[1] - z_grid[0]
    
    # Build L_diff array
    L_grid = np.zeros_like(z_grid)
    curr_z = 0
    for l in layers:
        mask = (z_grid >= curr_z) & (z_grid <= curr_z + l['thickness'])
        L_grid[mask] = l['L_diff']
        curr_z += l['thickness']
    
    # Build matrix
    main_diag = -2 * (L_grid**2 / dz**2) - 1
    off_diag_lower = L_grid[1:]**2 / dz**2
    off_diag_upper = L_grid[1:]**2 / dz**2
    
    matrix = diags([off_diag_lower, main_diag, off_diag_upper], 
                   [-1, 0, 1], shape=(len(z_grid), len(z_grid))).tocsr()
    
    # Solve
    c_z = spsolve(matrix, -p_z)
    c_z = np.maximum(c_z, 0)
    
    return c_z / np.trapezoid(c_z, z_grid)