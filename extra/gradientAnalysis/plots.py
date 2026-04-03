
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.signal import savgol_filter
from scipy.stats import linregress


def channelPlotter(channel, time, title, color, range=None, labels=None, ls=None):
    plt.figure(figsize=(10, 6))
    i=0
    j=0
    while j < len(time):
        if len(ls) == 1:
            ls = ls * len(channel)  # If a single linestyle is provided, repeat it for all channels
        while i < len(channel):
            print(f"i = {i}")
            if labels:
                plt.plot(time[j], channel[i], color=color[i], lw=1, label=labels[i], linestyle=ls[i] if ls else '-')
            else:
                plt.plot(time[j], channel[i], color=color[i], lw=1, label=f"Channel {i}", linestyle=ls[i] if ls else '-')
            i+=1
        print(f"j = {j}")
        j+=1
        i=0  # Reset i for the next time step
    plt.title(title)
    plt.xlabel("Time [s]")
    plt.ylabel("Temperature [°C]")
    if range is not None:
        plt.xlim(range[0,0], range[0,1])  # Focus on the specified time range
        plt.ylim(range[1,0], range[1,1])  # Focus on the specified temperature range
    plt.legend()
    plt.show()

def experimentPlotter(run1_data, run1_time, run2_data, run2_time, 
                      title="Comparison of Salt Runs", labels1=None, labels2=None, **kwargs):
    """
    Plots two sets of 4 channels, each with its own independent time array.
    
    run1_data: List of 4 arrays [CH0, CH1, CH2, CH3] for Set 1
    run1_time: Time array for Set 1
    run2_data: List of 4 arrays [CH0, CH1, CH2, CH3] for Set 2
    run2_time: Time array for Set 2
    """
    plt.figure(figsize=(12, 7))
    
    # Consistent colors for the 4 physical sensor locations
    colors = ['royalblue', 'crimson', 'seagreen', 'darkorange']
    
    # --- Plot Set 1 (Solid Lines) ---
    for i, ch in enumerate(run1_data):
        lbl = labels1[i] if labels1 else f"Run 1 - CH{i}"
        # Standard plt.plot(x, y) - x and y MUST match in length
        plt.plot(run1_time, ch, color=colors[i], linestyle='-', label=lbl, **kwargs)
        
    # --- Plot Set 2 (Dashed Lines) ---
    for i, ch in enumerate(run2_data):
        lbl = labels2[i] if labels2 else f"Run 2 - CH{i}"
        plt.plot(run2_time, ch, color=colors[i], linestyle='--', label=lbl, **kwargs)

    # --- Automatic X-Axis Scaling ---
    # Finds the absolute maximum time value between both runs
    max_t = max(np.max(run1_time), np.max(run2_time))
    plt.xlim(min(np.min(run1_time), np.min(run2_time)), max_t)

    # Formatting
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Time [s]")
    plt.ylabel("Temperature [°C]")
    plt.grid(True, which='both', ls=':', alpha=0.5)
    plt.legend(loc='upper right', ncol=2, fontsize=8)
    plt.tight_layout()
    plt.show()

# --- HOW TO CALL IT ---
# run1 = [CH0_1, CH1_1, CH2_1, CH3_1]
# run2 = [CH0_2, CH1_2, CH2_2, CH3_2]
# experimentPlotter(run1, time1, run2, time2, alpha=0.8)


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

    