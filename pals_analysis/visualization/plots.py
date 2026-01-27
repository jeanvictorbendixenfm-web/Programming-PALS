"""Visualization tools for PALS analysis."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def setup_plot_style():
    """Set up nice plotting style for thesis figures."""
    plt.rcParams.update({
        'figure.figsize': (10, 6),
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'legend.fontsize': 10,
        'figure.dpi': 100,
        'savefig.dpi': 300,
        'grid.alpha': 0.3,
    })


def plot_s_parameter_fit(energies, s_exp, d_ox, s_surf, save_as=None):
    """
    Plot S-parameter data with fit.
    
    Parameters
    ----------
    energies : array
        Experimental energies (keV)
    s_exp : array
        Experimental S-parameters
    d_ox : float
        Fitted oxide thickness (nm)
    s_surf : float
        Fitted surface S-parameter
    save_as : str, optional
        Filename to save figure
    """
    from ..analysis.thickness_solver import fit_model
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), 
                                    gridspec_kw={'height_ratios': [3, 1]})
    
    # Main plot
    s_fit = fit_model(energies, d_ox, s_surf)
    ax1.scatter(energies, s_exp, color='red', s=50, zorder=3, label='Experimental Data')
    ax1.plot(energies, s_fit, 'b-', linewidth=2, label=f'Fit: d={d_ox:.1f}nm, S={s_surf:.4f}')
    ax1.axhline(0.52, color='gray', linestyle='--', alpha=0.5, label='Bulk Steel')
    ax1.set_ylabel('S-Parameter', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title('S-Parameter vs Energy', fontsize=14, fontweight='bold')
    
    # Residual plot
    residuals = s_exp - s_fit
    ax2.scatter(energies, residuals, color='purple', s=40, alpha=0.7)
    ax2.axhline(0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Energy (keV)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Residual', fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_as}")
    
    return fig, (ax1, ax2)


def plot_depth_profiles(z, p_z, c_z, d_ox, energy, save_as=None):
    """
    Plot implantation and annihilation profiles.
    
    Parameters
    ----------
    z : array
        Depth grid (nm)
    p_z : array
        Implantation profile
    c_z : array
        Annihilation profile
    d_ox : float
        Oxide thickness (nm)
    energy : float
        Beam energy (keV)
    save_as : str, optional
        Filename to save
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.fill_between(z, 0, p_z, alpha=0.3, color='blue', label='Implantation Region')
    ax.plot(z, p_z, 'b-', linewidth=2, label='Implantation P(z)')
    ax.plot(z, c_z, 'r-', linewidth=2, label='Annihilation C(z)')
    ax.axvline(d_ox, color='black', linestyle='--', linewidth=2, 
               label=f'Interface (d={d_ox:.0f}nm)')
    
    # Shade oxide and steel regions
    ax.axvspan(0, d_ox, alpha=0.1, color='orange', label='Oxide')
    ax.axvspan(d_ox, z.max(), alpha=0.1, color='gray', label='Steel')
    
    ax.set_xlabel('Depth (nm)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability Density (nm⁻¹)', fontsize=12, fontweight='bold')
    ax.set_title(f'Positron Depth Profiles at E = {energy:.1f} keV', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_as}")
    
    return fig, ax


def create_heatmap(energies, depths, s_values, title='S-Parameter Heatmap', 
                   d_ox=None, save_as=None):
    """
    Create 2D heatmap of S-parameter vs energy and depth.
    
    Parameters
    ----------
    energies : array
        Energy values (keV)
    depths : array
        Depth values (nm)
    s_values : 2D array
        S-parameter values (shape: len(energies) x len(depths))
    title : str
        Plot title
    d_ox : float, optional
        Oxide thickness to mark on plot
    save_as : str, optional
        Filename to save
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create custom colormap (blue -> white -> red)
    colors = ['blue', 'white', 'red']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
    
    # Plot heatmap
    im = ax.contourf(energies, depths, s_values.T, levels=50, cmap=cmap)
    
    # Add interface line if provided
    if d_ox is not None:
        ax.axhline(d_ox, color='black', linestyle='--', linewidth=2, 
                   label=f'Oxide/Steel Interface ({d_ox:.0f}nm)')
        ax.legend(loc='upper right')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('S-Parameter', fontsize=12, fontweight='bold')
    
    ax.set_xlabel('Energy (keV)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Depth (nm)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_as}")
    
    return fig, ax


def plot_parameter_sensitivity(param_values, results, param_name, 
                               ylabel='Thickness (nm)', save_as=None):
    """
    Plot how results change with a parameter.
    
    Parameters
    ----------
    param_values : array
        Parameter values tested
    results : array
        Resulting values (e.g., fitted thickness)
    param_name : str
        Name of parameter being varied
    ylabel : str
        Label for y-axis
    save_as : str, optional
        Filename to save
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(param_values, results, 'o-', linewidth=2, markersize=8, color='blue')
    ax.set_xlabel(param_name, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    ax.set_title(f'Sensitivity to {param_name}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_as}")
    
    return fig, ax