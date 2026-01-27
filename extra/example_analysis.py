"""
Example PALS Analysis Script
=============================

Complete workflow for analyzing PALS experimental data.

This script demonstrates:
1. Loading experimental data
2. Data validation
3. Fitting to determine oxide thickness
4. Uncertainty analysis
5. Creating publication-quality figures

Author: [Your Name]
Date: January 2025
"""

import numpy as np
import matplotlib.pyplot as plt

# Import PALS analysis package
from pals_analysis import config
from pals_analysis.physics import simulate_pas_experiment
from pals_analysis.analysis import (
    solve_for_thickness,
    calculate_reduced_chi_squared,
    bootstrap_uncertainty
)
from pals_analysis.visualization import (
    setup_thesis_style,
    plot_s_parameter_fit,
    plot_bootstrap_distribution
)
from pals_analysis.utils import (
    validate_data,
    create_layer_config,
    print_fit_summary
)


def main():
    """Main analysis workflow."""
    
    # ========================================================================
    # 1. SETUP
    # ========================================================================
    
    print("=" * 70)
    print("PALS ANALYSIS - OXIDE THICKNESS DETERMINATION")
    print("=" * 70)
    print()
    
    # Configure plotting for thesis
    setup_thesis_style()
    
    # Print current configuration
    print("Material Configuration:")
    print(f"  Oxide (Fe₂O₃): ρ = {config.RHO_OXIDE} g/cm³")
    print(f"  Steel (SS316L): ρ = {config.RHO_STEEL} g/cm³, S = {config.S_BULK_STEEL}")
    print(f"  Makhov parameters: A = {config.MAKHOV_A}, n = {config.MAKHOV_N}")
    print()
    
    # ========================================================================
    # 2. LOAD EXPERIMENTAL DATA
    # ========================================================================
    
    print("Loading experimental data...")
    
    # Example data (replace with your actual data file)
    # energies, s_exp, s_err = load_from_file('data/sample1.csv')
    
    # For this example, use sample data
    energies = np.array([1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 15.0, 20.0])  # keV
    s_exp = np.array([0.5740, 0.5680, 0.5620, 0.5510, 0.5350, 0.5280, 0.5210, 0.5200])
    s_err = np.full_like(s_exp, 0.002)  # 0.002 uncertainty for all points
    
    print(f"  Loaded {len(energies)} data points")
    print(f"  Energy range: {energies.min():.1f} - {energies.max():.1f} keV")
    print()
    
    # ========================================================================
    # 3. DATA VALIDATION
    # ========================================================================
    
    print("Validating data...")
    is_valid, warnings = validate_data(energies, s_exp, s_err)
    
    if warnings:
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("  Data validation passed ✓")
    print()
    
    if not is_valid:
        print("ERROR: Data validation failed. Please fix data issues.")
        return
    
    # ========================================================================
    # 4. FIT DATA TO DETERMINE OXIDE THICKNESS
    # ========================================================================
    
    print("Fitting S-parameter curve...")
    print("  Method: Nonlinear least-squares (curve_fit)")
    print()
    
    # Perform fit
    d_ox, s_ox, d_err, s_err_fit, fit_info = solve_for_thickness(
        energies, 
        s_exp, 
        s_err,
        method='curve_fit'
    )
    
    # Check if fit was successful
    if not fit_info['success']:
        print("WARNING: Fit may not have converged properly")
        if 'error' in fit_info:
            print(f"Error: {fit_info['error']}")
    
    # Print results
    print_fit_summary(d_ox, s_ox, d_err, s_err_fit, fit_info['chi_squared'])
    
    # Calculate reduced chi-squared
    chi2_red = calculate_reduced_chi_squared(s_exp, fit_info['s_fit'], s_err, n_params=2)
    print(f"Reduced χ²: {chi2_red:.3f}")
    
    if chi2_red > 3:
        print("  Note: High χ² may indicate systematic errors or underestimated uncertainties")
    elif chi2_red < 0.3:
        print("  Note: Low χ² may indicate overestimated uncertainties")
    else:
        print("  Good fit quality ✓")
    print()
    
    # ========================================================================
    # 5. UNCERTAINTY ANALYSIS (BOOTSTRAP)
    # ========================================================================
    
    print("Performing bootstrap uncertainty analysis...")
    print("  (This may take a minute...)")
    
    d_boot, s_boot, d_std_boot, s_std_boot, boot_results = bootstrap_uncertainty(
        energies, s_exp, s_err, n_bootstrap=500
    )
    
    print(f"  Bootstrap results:")
    print(f"    Thickness: {d_boot:.2f} ± {d_std_boot:.2f} nm")
    print(f"    S-parameter: {s_boot:.4f} ± {s_std_boot:.4f}")
    print()
    
    # Compare with fit uncertainties
    print("  Comparison with fit uncertainties:")
    print(f"    Thickness ratio: {d_std_boot/d_err:.2f}x")
    print(f"    S-parameter ratio: {s_std_boot/s_err_fit:.2f}x")
    print()
    
    # ========================================================================
    # 6. CREATE FIGURES
    # ========================================================================
    
    print("Creating figures...")
    
    # Main S-parameter fit plot
    fig1, axes1 = plot_s_parameter_fit(
        energies, s_exp, s_err, d_ox, s_ox,
        show_residuals=True,
        show_depth_axis=True,
        title="PALS Analysis: SS316L/Fe₂O₃ System",
        save_as='results/s_parameter_fit.pdf'
    )
    
    # Bootstrap distribution plot
    fig2, axes2 = plot_bootstrap_distribution(
        boot_results, d_ox, s_ox,
        save_as='results/bootstrap_distributions.pdf'
    )
    
    print("  Figures saved to results/ directory")
    print()
    
    # ========================================================================
    # 7. OPTIONAL: COMPARE WITH SIMULATION
    # ========================================================================
    
    print("Running physics simulation for comparison...")
    
    # Create layer configuration using fitted parameters
    layers_fitted = create_layer_config(
        d_ox=d_ox,
        s_ox=s_ox,
        s_sub=config.S_BULK_STEEL
    )
    
    # Simulate
    sim_results = simulate_pas_experiment(energies, layers_fitted)
    
    print(f"  Simulated {len(energies)} energy points")
    
    # Compare simulated vs fitted values
    s_sim = sim_results['s_parameters']
    max_diff = np.max(np.abs(s_sim - fit_info['s_fit']))
    print(f"  Max difference (sim vs fit): {max_diff:.5f}")
    print()
    
    # ========================================================================
    # 8. SAVE RESULTS
    # ========================================================================
    
    print("Saving numerical results...")
    
    results_dict = {
        'oxide_thickness_nm': d_ox,
        'thickness_uncertainty_nm': d_err,
        'thickness_bootstrap_std_nm': d_std_boot,
        'oxide_s_parameter': s_ox,
        's_parameter_uncertainty': s_err_fit,
        's_parameter_bootstrap_std': s_std_boot,
        'chi_squared': fit_info['chi_squared'],
        'reduced_chi_squared': chi2_red,
        'n_data_points': len(energies),
        'energy_range_kev': f"{energies.min():.1f} - {energies.max():.1f}"
    }
    
    # Save to file
    from pals_analysis.utils import save_results
    save_results('results/analysis_summary.txt', results_dict)
    
    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print()
    print("Key Results:")
    print(f"  Oxide thickness: {d_ox:.1f} ± {d_err:.1f} nm")
    print(f"  Oxide S-parameter: {s_ox:.4f} ± {s_err_fit:.4f}")
    print(f"  χ²_red: {chi2_red:.2f}")
    print()
    print("Output files:")
    print("  - results/s_parameter_fit.pdf")
    print("  - results/bootstrap_distributions.pdf")
    print("  - results/analysis_summary.txt")
    print()
    
    # Show plots
    plt.show()


if __name__ == "__main__":
    # Create results directory if it doesn't exist
    from pathlib import Path
    Path("results").mkdir(exist_ok=True)
    
    # Run analysis
    main()
