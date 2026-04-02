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

def plot_thermal_results(time, grad, deriv, indices, plateau_info, 
                         inset_data=None, zoom_window=(4000, 10000), 
                         color='blue', title="Curve", label_data="Raw", ylabel_data=r"$\Delta$T [°C]"):
    """
    Creates the main plot with staggered labels and the requested inset.
    """
    fig, ax1 = plt.subplots(figsize=(14, 10))
    
    # Main Data
    ax1.plot(time, grad, color=color, label=label_data, lw=1.5, alpha=1)
    #ax1.scatter(time[indices], grad[indices], color='green', s=2, label='Steady State')

    # Staggered Labeling with Drift (Trend) Lines
    height_levels = [15, 35, 55, 75]
    for i, p in enumerate(plateau_info):
        # Draw the actual "Fitted" trend line instead of a flat hline
        t_line = np.array(p['t_range'])
        y_line = p['slope'] * t_line + p['intercept']
        ax1.plot(t_line, y_line, color='black', lw=2.5, zorder=5)
        
        # Labeling
        offset = height_levels[i % len(height_levels)]
        # We show the average and the drift rate
        label_text = f"{p['avg']:.2f} °C\nSlope: {p['slope']:.2e}"
        
        ax1.annotate(
            label_text, xy=(p['t_mid'], p['avg']), xytext=(0, offset),
            textcoords="offset points", ha='center', va='bottom',
            fontsize=8, fontweight='bold', color='red',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8),
            arrowprops=dict(arrowstyle='-', color='red', alpha=0.3)
        )

    # Inset Logic
    if inset_data is not None:
        # [left, bottom, width, height] as fractions
        ax_ins = ax1.inset_axes([0.5, 0.6, 0.45, 0.35])
        
        # Plot Immersion (from your provided tuple/dict)
        imm_t, imm_v = inset_data['immersion']
        ax_ins.plot(imm_t, imm_v, color='blue', lw=1, label='Immersion')
        ax_ins.set_ylabel("Depth [mm]", color='blue', fontsize=8)
        
        # Twin for Furnace Temp
        ax_ins2 = ax_ins.twinx()
        fur_t, fur_v = inset_data['furnace']
        ax_ins2.plot(fur_t, fur_v, color='magenta', lw=1)
        ax_ins2.set_ylabel("Furnace [°C]", color='magenta', fontsize=8)
        
        ax_ins.set_xlim(zoom_window)
        ax_ins.set_title("Immersion & Furnace Profile", fontsize=9, fontweight='bold')
        ax_ins.grid(True, alpha=0.2)

    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel(ylabel_data)
    ax1.set_xlim(zoom_window)
    ax1.set_title(title, fontweight='bold')
    ax1.legend(loc='lower left')
    plt.show()

    