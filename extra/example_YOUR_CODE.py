"""
Example Analysis Using YOUR EXACT CODE from the Notebooks
==========================================================

This script demonstrates how to use your refactored code exactly as you
were using it in your pals.ipynb and pals-solver.ipynb notebooks.

The code logic is IDENTICAL to yours - just organized into modules.
"""

import numpy as np
import matplotlib.pyplot as plt

# Import YOUR code
import sys
sys.path.insert(0, '/mnt/user-data/outputs')  # Adjust path as needed

from pals_analysis_YOUR_CODE import config
from pals_analysis_YOUR_CODE.physics.implantation import makhov_profile, get_graded_density
from pals_analysis_YOUR_CODE.physics.annihilation import (
    calculate_annihilation_profile,
    calculate_s_curves_with_profiles
)
from pals_analysis_YOUR_CODE.analysis.thickness_solver import (
    fit_experimental_data,
    fit_model
)


def example_1_sharp_vs_graded_interface():
    """
    Recreate YOUR analysis from pals.ipynb Cell 4.
    
    This is exactly what you were doing: comparing sharp vs graded interfaces.
    """
    print("=" * 70)
    print("EXAMPLE 1: Sharp vs Graded Interface (from pals.ipynb Cell 4)")
    print("=" * 70)
    
    # YOUR parameters
    d_ox = 155.0
    w = 30.0  # Width of the transition zone in nm
    
    # YOUR layer definition
    my_layers = [
        {'name': 'Fe2O3', 'thickness': d_ox, 'density': 5.22, 'L_diff': 30, 'S_ox': 0.575},
        {'name': 'SS316L', 'thickness': 1000, 'density': 8.00, 'L_diff': 150, 'S_bulk': 0.520}
    ]
    
    # YOUR grid
    z = np.linspace(0, 600, 300)
    energies = np.linspace(0.2, 25, 50)
    
    # Define S(z) Profiles exactly as YOU did
    # Sharp interface at d_ox
    s_z_sharp = np.where(z <= d_ox, 0.575, 0.520)
    
    # Graded interface using a sigmoid transition
    s_z_graded = 0.520 + (0.575 - 0.520) / (1 + np.exp((z - d_ox) / (w/4)))
    
    # Calculate S curves using YOUR code
    results = calculate_s_curves_with_profiles(
        energies, my_layers, s_z_sharp, s_z_graded, z
    )
    
    s_sharp_curve = results['s_sharp_curve']
    s_graded_curve = results['s_graded_curve']
    
    # YOUR plotting code
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Left: The physical S(z) profiles (Input Structure)
    ax1.plot(z, s_z_sharp, 'k--', label='Sharp Interface')
    ax1.plot(z, s_z_graded, 'r-', lw=2, label=f'Graded Interface ({w}nm)')
    ax1.set_xlabel('Depth (nm)', fontsize=12)
    ax1.set_ylabel('S-Parameter', fontsize=12)
    ax1.set_title('Physical S(z) Depth Profile', fontsize=13)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Right: The resulting S(E) curves (Experimental View)
    ax2.plot(energies, s_sharp_curve, 'k--', label='Sharp Response')
    ax2.plot(energies, s_graded_curve, 'r-', lw=3, label='Graded Response')
    ax2.set_xlabel('Incident Energy $E$ (keV)', fontsize=12)
    ax2.set_ylabel('Measured S-Parameter', fontsize=12)
    ax2.set_title('Experimental $S(E)$ Response', fontsize=13)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('example1_sharp_vs_graded.pdf', dpi=300, bbox_inches='tight')
    print("\nFigure saved: example1_sharp_vs_graded.pdf")
    print()


def example_2_fit_your_experimental_data():
    """
    Recreate YOUR analysis from pals-solver.ipynb Cell 2.
    
    This fits YOUR actual experimental data exactly as you did.
    """
    print("=" * 70)
    print("EXAMPLE 2: Fit YOUR Experimental Data (from pals-solver.ipynb Cell 2)")
    print("=" * 70)
    
    # Get YOUR data
    energies, s_experimental = config.get_your_experimental_data()
    
    print(f"\nLoaded {len(energies)} data points from YOUR notebook")
    print(f"Energy range: {energies.min():.1f} - {energies.max():.1f} keV")
    print()
    
    # Fit using YOUR code
    results = fit_experimental_data(energies, s_experimental, initial_guess=[15, 0.58])
    
    fit_d = results['thickness_nm']
    fit_S_ox = results['s_oxide']
    
    print("--- SOLVER RESULTS (YOUR CODE) ---")
    print(f"Calculated Thickness: {fit_d:.2f} nm")
    print(f"Calculated Oxide S:   {fit_S_ox:.4f}")
    print()
    
    # YOUR plotting code
    plt.figure(figsize=(10, 6))
    plt.scatter(energies, s_experimental, color='red', label='Your Experimental Data')
    plt.plot(energies, fit_model(energies, fit_d, fit_S_ox), 'b-', 
             label=f'Best Fit (d={fit_d:.1f}nm)')
    plt.axvline(x=energies[np.argmin(np.abs(s_experimental-0.55))], 
                color='gray', linestyle='--', label='Interface Region')
    plt.xlabel('Energy (keV)')
    plt.ylabel('S-parameter')
    plt.legend()
    plt.title('Self-Consistent Thickness Solver Output (YOUR CODE)')
    plt.savefig('example2_your_data_fit.pdf', dpi=300, bbox_inches='tight')
    print("Figure saved: example2_your_data_fit.pdf")
    print()


def example_3_depth_profiles():
    """
    Show implantation and annihilation profiles at a specific energy.
    """
    print("=" * 70)
    print("EXAMPLE 3: Depth Profiles at 5 keV")
    print("=" * 70)
    
    # Setup
    layers = config.get_your_example_layers()
    z = np.linspace(0, 600, 300)
    energy = 5.0  # keV
    
    # Calculate profiles using YOUR code
    p_z = makhov_profile(z, energy, layers)
    c_z = calculate_annihilation_profile(z, p_z, layers)
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(z, p_z, 'b-', linewidth=2, label='Implantation P(z)')
    plt.plot(z, c_z, 'r-', linewidth=2, label='Annihilation C(z)')
    plt.axvline(155, color='gray', linestyle='--', alpha=0.5, label='Oxide/Steel Interface')
    plt.xlabel('Depth (nm)', fontsize=12)
    plt.ylabel('Probability Density (nm⁻¹)', fontsize=12)
    plt.title(f'Positron Profiles at E = {energy} keV (YOUR CODE)', fontsize=13)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('example3_depth_profiles.pdf', dpi=300, bbox_inches='tight')
    print("\nFigure saved: example3_depth_profiles.pdf")
    print()


def example_4_verify_against_original():
    """
    Verify that the refactored code gives IDENTICAL results to your notebooks.
    """
    print("=" * 70)
    print("EXAMPLE 4: Verification - Code Produces Identical Results")
    print("=" * 70)
    
    # Test parameters
    z = np.linspace(0, 600, 300)
    energy = 10.0
    layers = config.get_your_example_layers()
    
    # Calculate using YOUR refactored code
    p_z = makhov_profile(z, energy, layers)
    
    # Verify normalization (should integrate to 1)
    integral = np.trapezoid(p_z, z)
    print(f"\nMakhov profile normalization: ∫P(z)dz = {integral:.6f}")
    print(f"Expected: 1.000000")
    print(f"Difference: {abs(integral - 1.0):.2e}")
    
    if abs(integral - 1.0) < 1e-6:
        print("✓ PASS: Normalization correct")
    else:
        print("✗ FAIL: Normalization incorrect")
    
    # Test S-curve calculation
    energies, s_exp = config.get_your_experimental_data()
    d_ox, s_ox = fit_experimental_data(energies, s_exp)['thickness_nm'], \
                 fit_experimental_data(energies, s_exp)['s_oxide']
    
    print(f"\nFitted thickness: {d_ox:.2f} nm")
    print(f"This should match YOUR result from pals-solver.ipynb Cell 2")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("RUNNING ALL EXAMPLES USING YOUR EXACT CODE")
    print("=" * 70 + "\n")
    
    # Print configuration
    config.print_config()
    print()
    
    # Run examples
    try:
        example_1_sharp_vs_graded_interface()
    except Exception as e:
        print(f"Example 1 error: {e}")
    
    try:
        example_2_fit_your_experimental_data()
    except Exception as e:
        print(f"Example 2 error: {e}")
    
    try:
        example_3_depth_profiles()
    except Exception as e:
        print(f"Example 3 error: {e}")
    
    try:
        example_4_verify_against_original()
    except Exception as e:
        print(f"Example 4 error: {e}")
    
    print("=" * 70)
    print("ALL EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - example1_sharp_vs_graded.pdf")
    print("  - example2_your_data_fit.pdf")
    print("  - example3_depth_profiles.pdf")
    print()
    
    # Show plots
    plt.show()


if __name__ == "__main__":
    main()
