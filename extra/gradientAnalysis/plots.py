
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.signal import savgol_filter, coherence
from scipy.stats import linregress
from matplotlib.colors import LogNorm
from scipy.ndimage import uniform_filter1d

import sys
sys.path.insert(0, r'C:\Users\jeanv\OneDrive - Delft University of Technology\Uitwisseling - TUDelft\Courses\MEP\Programming\extra')


from gradientAnalysis.functions import find_plateaus, analyze_drift, savgolCompilator, coherenceData, powerlaw, powerlawFitter



# def channelPlotter(channel, time, title, color, rangex=None, rangey=None, labels=None, linestyles=None):
#     plt.figure(figsize=(10, 6))
#     i=0
#     j=0
#     while j < len(time):
#         if len(linestyles) == 1:
#             linestyles = linestyles * len(channel)  # If a single linestyle is provided, repeat it for all channels
#         while i < len(channel):
#             if labels:
#                 plt.plot(time[j], channel[i], color=color[i], lw=1, label=labels[i], linestyle=linestyles[i] if linestyles else '-')
#             else:
#                 plt.plot(time[j], channel[i], color=color[i], lw=1, label=f"Channel {i}", linestyle=linestyles[i] if linestyles else '-')
#             i+=1
#         j+=1
#         i=0  # Reset i for the next time step
#     plt.title(title)
#     plt.xlabel("Time [s]")
#     plt.ylabel("Temperature [°C]")

#     ax = plt.gca()
#     # x-axis range
#     if rangex is not None:
#         plt.xlim(rangex[0], rangex[1])
#     else:
#         plt.gca().relim()           # Recalculate limits based on plotted data
#         plt.gca().autoscale_view()  # Update the view

#     # y-axis range
#     if rangey is not None:
#         plt.ylim(rangey[0], rangey[1])
#     else:
#         plt.gca().relim()
#         plt.gca().autoscale_view()

#     plt.legend()
#     plt.show()

def channelPlotter(channel, time, title, color, rangex=None, rangey=None, labels=None, linestyles=None, ax=None, twin=False, extratwin=False, epsilon=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    if linestyles is None: linestyles = ['-'] * len(channel)
    elif len(linestyles) == 1: linestyles = linestyles * len(channel)

    # Determine which channels belong to the main axis vs the twin axis
    # If twin is True, we assume the LAST channel in the list is the derivative
    main_channels_count = len(channel) - (2 if (twin and extratwin) else 1 if twin else 0)

    # 1. Plot Main Channels (Temperature)
    for i in range(main_channels_count):
        if isinstance(labels, list):
            lbl = labels[i] if i < len(labels) else f"Channel {i}"
        else:
            lbl = labels if labels else f"Channel {i}"
            
        t_data = time[i] if len(time) > i else time[0]
        ax.plot(t_data, channel[i], color=color[i], lw=1, label=lbl, linestyle=linestyles[i])

    # 2. Plot Twin Channel (Derivative)
    if twin:
        ax_twin = ax.twinx()
        # Use the last index for the derivative
        t_twin = time[-1] if len(time) == len(channel) else time[0]
        if extratwin == True:
            ax_twin.fill_between([t_twin[0],t_twin[-1]], -epsilon, epsilon, color='orange', alpha=0.3, label='Steady Window')
            ax_twin.plot(t_data, channel[-2], color=color[-2], lw=1, label=lbl, linestyle=linestyles[-2])
            ax_twin.set_ylim(-0.005, 0.005)
        ax_twin.plot(t_twin, channel[-1], color=color[-1], lw=1, 
                     label=labels[-1] if labels else "Derivative", linestyle=linestyles[-1])
        ax_twin.set_ylabel("Rate [°C/s]", color=color[-1])
        ax_twin.tick_params(axis='y', labelcolor=color[-1])
        
        # Combine legends so they don't overlap
        lines, labs = ax.get_legend_handles_labels()
        lines2, labs2 = ax_twin.get_legend_handles_labels()
        ax.legend(lines + lines2, labs + labs2, loc='best', fontsize=8)
    elif labels:
        ax.legend(loc='best', fontsize="xx-large")

    # 3. Formatting
    if title: ax.set_title(title, fontsize=22)
    ax.set_xlabel("Time [s]", fontsize=20)
    ax.set_ylabel("Temperature [°C]", color="black", fontsize=20)
    ax.tick_params(axis='y', labelcolor="black")
    
   
    # 4. SMART SCALING (Only for Main Axis Channels)
    if rangex is not None:
        ax.set_xlim(rangex[0], rangex[1])
        if rangey is None:
            y_min_list, y_max_list = [], []
            # CRITICAL: Only loop through main_channels_count
            for i in range(main_channels_count):
                t_data = time[i] if len(time) > i else time[0]
                mask = (t_data >= rangex[0]) & (t_data <= rangex[1])
                if np.any(mask):
                    y_min_list.append(np.min(channel[i][mask]))
                    y_max_list.append(np.max(channel[i][mask]))
            
            if y_min_list:
                y_min, y_max = min(y_min_list), max(y_max_list)
                margin = (y_max - y_min) * 0.05 if y_max != y_min else 1.0
                ax.set_ylim(y_min - margin, y_max + margin)

    if rangey is not None:
        ax.set_ylim(rangey[0], rangey[1])



def coherencePlotter(windows_time, freqs, Z, Z_axis, window_size, step_size, nperseg, runID="Run 3.1", cmap="viridis"):
    # Plotting of Coherence
    plt.figure(figsize=(10, 6))

        # Using LogNorm to see the power-law decay clearly
        
    im = plt.pcolormesh(windows_time, np.log10(freqs+0.001), Z, shading='gouraud', 
                    vmin=Z.min(), vmax=Z.max(), cmap=cmap)

    plt.ylabel('Frequency (log10) [Hz]')
    plt.xlabel('Time (Experiment Progress) [s]')
    plt.title(f'Coherence Spectrogram of {runID} \n  $w={window_size}, s={step_size}, nperseg = {nperseg}$')
    plt.colorbar(im, label=Z_axis)
    plt.show()


def coherenceFitPlotter(freqs, Z_slice, a_fit_val, b_fit_val, windows_time=None, b_fits_array=None, b_errors=None):
    """
    freqs: frequency array
    Z_slice: a single column (window) of coherence data
    a_fit_val, b_fit_val: specific fit params for that slice
    windows_time: array of window centers
    b_fits_array: the array of all b_fit values over time
    """
    
    # Plot 1: The Spectrum + The Fit Line (Log-Log)
    plt.figure(figsize=(10, 5))
    plt.loglog(freqs, Z_slice, lw=0.5, label="Data Slice", color="blue")
    plt.loglog(freqs, powerlaw(freqs, a_fit_val, b_fit_val), color="green", label=f"Fit: b={b_fit_val:.2f}")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Coherence")
    plt.legend()
    plt.title("Power Law Fit Check")
    plt.show()

    # Plot 2: Evolution of b over time
    if windows_time is not None and b_fits_array is not None:
        plt.figure(figsize=(12, 5))
        plt.errorbar(windows_time, b_fits_array, yerr=b_errors, fmt='o', 
                 ecolor='black', elinewidth=1, capsize=2, 
                 label='Measured Exponent $b \pm \sigma$', markersize=0.5)
        plt.axhline(-1.3, color='red', ls='--', label='Target (-1.3)')
        plt.xlabel("Time [s]")
        plt.ylabel("Exponent Value")
        plt.title("Evolution of Power Law Exponent $b$")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()   
    

def plotOverviewDashboard(runID, f, win_t, Z_coh, Z_psd0, Z_psd1, b_coh, b_psd0, b_psd1, a_coh, b_errors=None, cmap="magma", color_singlechannels=["red","blue"]):
    # a_coh is now included in the arguments
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    fig.suptitle(f"Spectral Analysis: {runID}", fontsize=18, fontweight='bold')

    # 3. Bottom Left: PSD Heatmap (Log Scale)
    im2 = axs[1, 0].pcolormesh(win_t, np.log10(f+0.001), np.log10(Z_psd1), shading='gouraud', cmap=cmap)
    axs[1, 0].set_title("Hot Intrasaline Energy Density (log10 PSD)")
    axs[1, 0].set_ylabel("Frequency (log10) [Hz]")
    axs[1, 0].set_xlabel("Time [s]")
    fig.colorbar(im2, ax=axs[1, 0])


    # 1. Top Left: Coherence Heatmap
    im3 = axs[0, 0].pcolormesh(win_t, np.log10(f+0.001), np.log10(Z_psd0), shading='gouraud', cmap=cmap)
    axs[0, 0].set_title("Cold Intrasaline Energy Density (log10 PSD)")
    axs[0, 0].set_ylabel("Frequency (log10) [Hz]")
    axs[0, 0].set_xlabel("Time [s]")
    fig.colorbar(im3, ax=axs[0, 0])


    # 2. Top Right: Exponent Evolution
    axs[0, 1].plot(win_t, b_psd0, label='CH0 Exponent', alpha=1, color=color_singlechannels[0])
    axs[0, 1].plot(win_t, b_psd1, label='CH1 Exponent', alpha=1, color=color_singlechannels[1])
    axs[0, 1].errorbar(win_t, b_coh, yerr=b_errors, fmt='o', color='black',
                       ecolor='black', elinewidth=1, capsize=1, ms=3,
                       label='Coherence $b \pm \sigma$')
    axs[0, 1].axhline(-1.33, color='r', ls='--', label='Theory (-1.33)')
    axs[0, 1].set_title("Evolution of Scaling Exponents ($b$)")
    axs[0, 1].set_ylabel("Exponent Value")
    axs[0, 1].legend(loc='best', fontsize='small')
    axs[0, 1].set_xlabel("Time [s]")
    axs[0, 1].grid(True, alpha=0.2)


    # 4. Bottom right: Coherence Heatmap
    im1 = axs[1, 1].pcolormesh(win_t, np.log10(f+0.001), np.log10(Z_coh), shading='gouraud', cmap=cmap, vmin=np.log10(Z_coh).min(), vmax=np.log10(Z_coh).max())
    axs[1, 1].set_title("Dual-Channel Coherence (log10)")
    axs[1, 1].set_ylabel("Frequency (log10) [Hz]")
    axs[1, 1].set_xlabel("Time [s]")
    fig.colorbar(im1, ax=axs[1, 1])
    

    plt.show()

def plotOverviewDashboard(runID, f, win_t, Z_coh, Z_psd0, Z_psd1, b_coh, b_psd0, b_psd1, a_coh, b_errors=None, cmap="magma", color_singlechannels=["red","blue"], location="intra"):
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    fig.suptitle(f"Spectral Analysis: {runID}", fontsize=22, fontweight='bold')

    # --- CALCULATE GLOBAL PSD LIMITS ---
    # Convert to log10 once to make calculations cleaner
    log_psd0 = np.log10(Z_psd0)
    log_psd1 = np.log10(Z_psd1)
    
    # Find the min and max across BOTH channels
    psd_vmin = min(log_psd0.min(), log_psd1.min())
    psd_vmax = max(log_psd0.max(), log_psd1.max())

    # 1. Top Left: Cold Channel PSD Heatmap
    im_psd0 = axs[0, 0].pcolormesh(win_t, np.log10(f+0.001), log_psd0, 
                                   shading='gouraud', cmap=cmap, 
                                   vmin=psd_vmin, vmax=psd_vmax) # Set shared range
    axs[0, 0].set_title("Cold Intrasaline Energy Density (log10 PSD)", fontsize=21)
    if location=="extra":
        axs[0, 0].set_title("Cold Extrasaline Energy Density (log10 PSD)", fontsize=21)
    axs[0, 0].set_ylabel("Frequency (log10) [Hz]", fontsize=20)
    axs[0, 0].set_xlabel("Time [s]", fontsize=20)
    fig.colorbar(im_psd0, ax=axs[0, 0], label="dB/Hz")

    # 3. Bottom Left: Hot Channel PSD Heatmap
    im_psd1 = axs[1, 0].pcolormesh(win_t, np.log10(f+0.001), log_psd1, 
                                   shading='gouraud', cmap=cmap, 
                                   vmin=psd_vmin, vmax=psd_vmax) # Set shared range
    axs[1, 0].set_title("Hot Intrasaline Energy Density (log10 PSD)", fontsize=21)
    if location=="extra":
        axs[1, 0].set_title("Hot Extrasaline Energy Density (log10 PSD)", fontsize=21)
    axs[1, 0].set_ylabel("Frequency (log10) [Hz]", fontsize=20)
    axs[1, 0].set_xlabel("Time [s]")
    fig.colorbar(im_psd1, ax=axs[1, 0], label="dB/Hz")

    # 2. Top Right: Exponent Evolution
    axs[0, 1].plot(win_t, b_psd0, label='CH0 Exponent', alpha=1, color=color_singlechannels[0])
    axs[0, 1].plot(win_t, b_psd1, label='CH1 Exponent', alpha=1, color=color_singlechannels[1])
    if b_errors is not None:
        axs[0, 1].errorbar(win_t, b_coh, yerr=b_errors, fmt='o', color='black',
                           ecolor='black', elinewidth=1, capsize=1, ms=3,
                           label='Coherence $b \pm \sigma$')
    else:
        axs[0, 1].plot(win_t, b_coh, 'ko', ms=3, label='Coherence $b$')
        
    axs[0, 1].axhline(-1.33, color='r', ls='--', label='Theory (-1.33)')
    axs[0, 1].set_title("Evolution of Scaling Exponents ($b$)", fontsize=21)
    axs[0, 1].set_ylabel("Exponent Value", fontsize=20)
    axs[0, 1].set_xlabel("Time [s]", fontsize=20)
    axs[0, 1].legend(loc='best', fontsize='small')
    axs[0, 1].grid(True, alpha=0.2)

    # 4. Bottom right: Coherence Heatmap
    # Note: Coherence is 0 to 1, so log10(Z_coh) will be 0 to -inf. 
    # Usually coherence is plotted on a linear scale, but kept your log10 logic here:
    log_coh = np.log10(Z_coh)
    im1 = axs[1, 1].pcolormesh(win_t, np.log10(f+0.001), log_coh, 
                               shading='gouraud', cmap=cmap, 
                               vmin=log_coh.min(), vmax=log_coh.max())
    axs[1, 1].set_title("Dual-Channel Coherence (log10)", fontsize=21)
    axs[1, 1].set_ylabel("Frequency (log10) [Hz]", fontsize=20)
    axs[1, 1].set_xlabel("Time [s]", fontsize=20)
    fig.colorbar(im1, ax=axs[1, 1])

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

def savgolCalcPlotter(channel1, time, window_length=51, polyorder=4, deriv=0, delta=1.0):
    Ts, Td = savgolCompilator(channel1, window_length=window_length, 
                                polyorder=polyorder, deriv=deriv, delta=delta)
    
    fig, ax1 = plt.subplots(figsize=(10, 8))
    ax2 = ax1.twinx()  # Create a second y-axis for the derivative

    print(Td)
    # Top Plot: Raw vs Smoothed
    #ax1.plot(channel1, time, label='Raw', color='crimson', lw=1)
    ax2.plot(Ts, Td, label='Derivative', color='green', lw=1)
    ax1.plot(Ts, time, label='Savgol Smoothed', color='teal', lw=1)
    ax1.plot(channel1, time, label='Raw', color='crimson', lw=1)
    ax2.set_ylim(Td.min() * 1.1, Td.max() * 1.1)  # Add some padding to the y-limits of the derivative
    ax1.set_xlabel("Temperature [°C]")
    ax1.set_ylabel("Time [s]")
    ax2.set_ylabel("Rate of Change [°C/s]")
    ax1.set_title("Savintsky-Golay Smoothing and Derivative of Temperature Channel for $w={window_length}$ and $p={polyorder}$".format(window_length=window_length, polyorder=polyorder))
    ax1.legend()
    ax2.legend()
    plt.tight_layout()
    plt.show()






# plt.figure(figsize=(16, 8))

# xmin_vals = [18000, 25000,30000]
# nperseg_vals = [512, 512, 512]
# color = ["darkgreen", "green", "teal", "blue", "darkblue"]
# window_ch0 = 2001
# window_ch1 = 2001
# window_ch2 = 2001
# window_ch3 = 2001
# window_grad = window_ch0
# poly_ch0 = 3
# poly_ch1 = 3
# poly_ch2 = 3
# poly_ch3 = 3
# poly_grad = poly_ch0

# for i in range(len(xmin_vals)):
#         # Parameters and data shortening to range


#     xmin = xmin_vals[i]
#     xmax = 87000

    
#     ## Channel 0
#     CH0_timeR, CH0_yR = rangeSelector(CH0run3_1, timerun3_1, [xmin, xmax])
#     ## Channel 1 
#     CH1_timeR, CH1_yR = rangeSelector(CH1run3_1, timerun3_1, [xmin, xmax])
#     ## Channel 2
#     CH2_timeR, CH2_yR = rangeSelector(CH2run3_1, timerun3_1, [xmin, xmax])
#     ## Channel 3
#     CH3_timeR, CH3_yR = rangeSelector(CH3run3_1, timerun3_1, [xmin, xmax])
#     ## Gradient
#     gradrun3_timeR, gradrun3_yR = rangeSelector(CH1run3_1-CH0run3_1, timerun3_1, [xmin, xmax])
    
#     dt = np.mean(np.diff(CH0_timeR))
#     fs_val = 1.0 / dt
#     print(np.mean(np.diff(CH0_timeR)))
#     print(fs_val)
#     print(xmax-xmin)
#     print(f"hello  {timerun3_1[-1]}")

#     # dt = np.mean(np.diff(CH3_timeR))
#     # fs_val3 = 1.0 / dt

#     # 1. Calculate the Coherence between the two heights
#     # This tells you: "At frequency X, how much do these two sensors agree?"
#     f_coh, coh = coherence(CH1_yR, CH0_yR, fs=fs_val, nperseg=nperseg_vals[i])
#     #f_coh2, coh2 = coherence(CH3_yR, CH2_yR, fs=fs_val3, nperseg=512)
#     mask = (f_coh > 0.01) & (f_coh < 0.4) 
#     f_fit = f_coh[mask]
#     coh_fit = coh[mask]

#     popt, pcov = curve_fit(powerlaw, f_fit, coh_fit, p0=[1, -1])
#     a_fit, b_fit = popt
#     print(f"Fit result: coh = {a_fit:.7f} * f^({b_fit:.7f})")
#     plt.loglog(f_coh, coh, color=color[i], lw=0.5, ls="-")
#     plt.loglog(f_coh, powerlaw(f_coh, a_fit, b_fit), )
#     #plt.plot(f_coh2, coh2, color="red")


# plt.title("Coherence between 15mm and 55mm Sensors")
# plt.yscale("log")
# plt.xlabel("Frequency [Hz]")
# plt.ylabel("Coherence (0 to 1)")
# plt.grid(True)
# plt.show()