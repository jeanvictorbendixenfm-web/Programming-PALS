# Functions

# Importing packages 

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.signal import savgol_filter
from scipy.stats import linregress

def find_plateaus(time, data, window=500, poly=1, epsilon=0.001, gap_thresh=100):
    """
    Smooths data, calculates derivative, and groups indices into "plateaus".
    """
    # Savitzky-Golay for smoothing and 1st derivative
    deriv = savgol_filter(data, window, poly, deriv=1, delta=time[1]-time[0])
    
    # Identify indices where slope is near zero
    indices = np.where((deriv < epsilon) & (deriv > -epsilon))[0]
    
    # Grouping indices by gaps
    gaps = np.where(np.diff(indices) > gap_thresh)[0] + 1
    groups = np.split(indices, gaps)
    
    # Filter out tiny flickers (less than 10 points)
    groups = [g for g in groups if len(g) > 10]
    # Sort by time
    groups = sorted(groups, key=lambda x: time[x[0]])
    
    return deriv, indices, groups

def analyze_drift(time, data, groups):
    """
    Calculates the 'Micro-Slope' of each plateau to check for upward trends.
    """
    results = []
    for region in groups:
        t_part = time[region]
        d_part = data[region]
        slope, intercept, _, _, _ = linregress(t_part, d_part)
        results.append({
            'avg': np.mean(d_part),
            'slope': slope,
            'intercept': intercept,
            't_mid': (t_part[0] + t_part[-1]) / 2,
            't_range': (t_part[0], t_part[-1])
        })
    return results

