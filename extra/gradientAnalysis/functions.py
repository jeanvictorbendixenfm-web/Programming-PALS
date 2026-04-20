# Functions

# Importing packages 

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.signal import savgol_filter, coherence
from scipy.stats import linregress
from scipy.optimize import curve_fit
from scipy.signal import welch, detrend

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

def savgolCompilator(channel, window_length=11, polyorder=3, deriv=0, delta=1.0, deriv_filtered=True):
    filtered = savgol_filter(channel, window_length=window_length, polyorder=polyorder)
    derivative = savgol_filter(channel, window_length=window_length, polyorder=polyorder, deriv=deriv, delta=delta)
    if deriv_filtered == True:
        filtered_derivative = savgol_filter(filtered, window_length=window_length, polyorder=polyorder, deriv=deriv, delta=delta)
    else:
        filtered_derivative = 0
    return filtered, derivative, filtered_derivative

def rangeSelector(channel, timechannel, range):
    xmin, xmax = range[0], range[1]

    mask = (timechannel >= xmin) & (timechannel <= xmax)
    xR = timechannel[mask]
    yR = channel[mask]

    return xR, yR # x-range, y-range, in arrays. 


def coherenceData(channel1, channel2, time1, window_size=4096, step_size=1024, nperseg=512, logaxis=False, freq_range=[0.01, 0.4]):
        # --- Parameters ---
    windows_time = []
    coherence_matrix = []
    a_fits = []
    b_fits = []
    b_errors = []
    freqs = None

    if window_size==0:
        fs_val = 1.0 / np.mean(np.diff(time1))
        f, Cxy = coherence(channel1, channel2, fs=fs_val, nperseg=nperseg)
        a, b = powerlawFitter(freqs, Cxy, freq_range=freq_range, quiet=True)
        return time1[0], freqs, Cxy, a, b

    if window_size > 0:
        for start in range(0, len(channel2) - window_size, step_size):
            end = start + window_size
            
            c1, c2 = channel2[start:end], channel1[start:end]
            t_chunk = time1[start:end]
            
            # Calculate local sampling rate
            fs_val = 1.0 / np.mean(np.diff(t_chunk))
            
            f, Cxy = coherence(c1, c2, fs=fs_val, nperseg=nperseg)

            # Perform fit for this specific window
            try:
                a, b, b_err = powerlawFitter(f, Cxy, freq_range=freq_range, quiet=True)
            except:
                a, b = np.nan, np.nan  # If fit fails, use NaN to keep array length consistent
            
            if freqs is None: freqs = f
            coherence_matrix.append(Cxy)
            windows_time.append(np.mean(t_chunk))
            a_fits.append(a)
            b_fits.append(b)
            b_errors.append(b_err)

    # Convert to array
    Z = np.array(coherence_matrix).T 
    Z_axis = "Coherence [a.u.]"
    
    
    Z_log = 0
    if logaxis:
        Z_log = np.log10(Z) # Added epsilon to avoid log(0)
        Z_axis = "Coherence [a.u.] (log10)"

    return np.array(windows_time), freqs, Z, Z_log, Z_axis, np.array(a_fits), np.array(b_fits), np.array(b_errors)


def singleWelch(channel1, time1, window_size=4096, step_size=1024, nperseg=512, logaxis=False, freq_range=[0.01, 0.4], dtrend=False):
    windows_time = []
    psd_matrix = [] # Renamed from coherence for clarity
    a_fits = []
    b_fits = []
    b_errors = []
    freqs = None

    if window_size == 0:
        fs_val = 1.0 / np.mean(np.diff(time1))
        f, Pxx = welch(channel1, fs=fs_val, nperseg=nperseg)
        # Fix: powerlawFitter returns 3 values (a, b, err)
        a, b, b_err = powerlawFitter(f, Pxx, freq_range=freq_range, quiet=True)
        # Fix: return the same number of variables as the windowed version
        return np.array([time1[0]]), f, Pxx.reshape(-1,1), np.log10(Pxx+1e-9), "PSD [K^2/Hz]", np.array([a]), np.array([b]), np.array([b_err])

    if window_size > 0:
        for start in range(0, len(channel1) - window_size, step_size):
            end = start + window_size
            
            # FIX: Remove the extra channel1 here
            c1 = channel1[start:end]
            if dtrend == True:
                c1 = detrend(c1, type='linear')

            t_chunk = time1[start:end]
            
            fs_val = 1.0 / np.mean(np.diff(t_chunk))
            
            # welch() only takes ONE channel, not (c1, c2)
            f, Pxx = welch(c1, fs=fs_val, nperseg=nperseg)

            try:
                a, b, b_err = powerlawFitter(f, Pxx, freq_range=freq_range, quiet=True)
            except:
                a, b, b_err = np.nan, np.nan, np.nan 
            
            if freqs is None: freqs = f
            psd_matrix.append(Pxx)
            windows_time.append(np.mean(t_chunk))
            a_fits.append(a)
            b_fits.append(b)
            b_errors.append(b_err)

    Z = np.array(psd_matrix).T 
    Z_axis = "PSD [K^2/Hz]"
    
    Z_log = 0
    if logaxis:
        Z_log = np.log10(Z + 1e-9) 
        Z_axis = "PSD [K^2/Hz] (log10)"

    return np.array(windows_time), freqs, Z, Z_log, Z_axis, np.array(a_fits), np.array(b_fits), np.array(b_errors)



def powerlaw(f, a, b):
    return a * np.power(f, b)


def powerlawFitter(freqs, Z, freq_range=[0.01, 0.4], quiet=True):
    mask = (freqs > freq_range[0]) & (freqs < freq_range[1]) 
    f_fit = freqs[mask]
    coh_fit = Z[mask]
    
    # Simple check to ensure we have data to fit
    if len(f_fit) < 2:
        return np.nan, np.nan

    popt, pcov = curve_fit(powerlaw, f_fit, coh_fit, p0=[1, -1.3])
    a_fit, b_fit = popt
    
    if not quiet:
        print(f"Fit result: coh = {a_fit:.7f} * f^({b_fit:.7f})")


    perr = np.sqrt(np.diag(pcov)) 
    b_err = perr[1] # This is the error for the exponent 'b'

    return a_fit, b_fit, b_err