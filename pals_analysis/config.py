"""Configuration - all constants in one place."""

import numpy as np

# Material properties
RHO_OXIDE = 5.24      # Fe2O3 density (g/cm³)
RHO_STEEL = 8.00      # SS316L density (g/cm³)

# Makhov parameters (from your code: n, m, A = 1.6, 2.0, 4.0)
MAKHOV_A = 4.0
MAKHOV_N = 1.6
MAKHOV_M = 2.0

# S-parameters
S_BULK_STEEL = 0.52

# Diffusion lengths (nm)
L_DIFF_OXIDE = 30
L_DIFF_STEEL = 150

# Your experimental data from pals-solver.ipynb Cell 2
YOUR_DATA = np.array([
    [0.2, 0.58], [1.0, 0.568], [1.9, 0.574], [2.5, 0.58], [3.5, 0.578],
    [4.1, 0.5670], [5.1, 0.5650], [6.1, 0.5545], [6.9, 0.5440], [7.9, 0.5430],
    [8.8, 0.5360], [10.0, 0.5330], [10.7, 0.5300], [12.0, 0.5250], [12.9, 0.5240],
    [14.0, 0.5245], [15.1, 0.5250], [16.2, 0.5210], [17.5, 0.5240], [18.5, 0.5240],
    [19.5, 0.5200], [21.0, 0.5150], [22.2, 0.5100], [23.5, 0.5200]
])