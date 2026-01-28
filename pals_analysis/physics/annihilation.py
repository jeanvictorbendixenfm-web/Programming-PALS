"""Annihilation functions - Updated for Graded Interface."""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

def calculate_annihilation_profile(z_grid, p_z, layers, model='sharp', w=10.0):
    """
    Calculates Diffusion-Annilation Profile C(z).
    Supports 'sharp' and 'graded' diffusion length transitions.
    """
    z_grid = np.asarray(z_grid)
    p_z = np.asarray(p_z)
    dz = z_grid[1] - z_grid[0]
    n_pts = len(z_grid)
    
    # 1. Build Diffusion Length (L) Map
    L_grid = np.zeros_like(z_grid)
    
    if model == 'graded' and len(layers) >= 2:
        # Graded: Sigmoid transition for Diffusion Length
        d_ox = layers[0]['thickness']
        L_ox = layers[0]['L_diff']
        L_sub = layers[1]['L_diff']
        
        L_grid = L_ox + (L_sub - L_ox) / (1 + np.exp(-(z_grid - d_ox) / (w/4.0)))
    else:
        # Sharp: Step function
        curr_z = 0
        for l in layers:
            mask = (z_grid >= curr_z) & (z_grid <= curr_z + l['thickness'])
            L_grid[mask] = l['L_diff']
            curr_z += l['thickness']
    
    # 2. Build Sparse Matrix for Diffusion Equation
    # Equation: L^2 * d2C/dz2 - C = -P
    
    # Coefficients
    # Central difference: d2C/dz2 ~ (C_{i+1} - 2C_i + C_{i-1}) / dz^2
    factor = L_grid**2 / dz**2
    
    main_diag = -2 * factor - 1
    off_diag = factor # simplified; assumes L is constant locally or changes slowly
    
    # Fix off-diagonals to match matrix size (N-1)
    lower = off_diag[1:] 
    upper = off_diag[:-1]
    
    # Boundary Conditions (Reflective surface: C_0 = C_1 -> Neumann)
    # We approximate by adjusting the first matrix row or just ignoring for bulk
    # Here we use standard Dirichlet/Natural setup, ensuring stability
    
    matrix = diags([lower, main_diag, upper], [-1, 0, 1], shape=(n_pts, n_pts)).tocsr()
    
    # 3. Solve
    c_z = spsolve(matrix, -p_z)
    c_z = np.maximum(c_z, 0) # Remove numerical noise < 0
    
    # Normalize
    integral = np.trapezoid(c_z, z_grid)
    return c_z / integral if integral > 0 else c_z