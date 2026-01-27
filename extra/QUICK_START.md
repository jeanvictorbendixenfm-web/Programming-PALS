# PALS Analysis Package - Quick Start Guide

## Installation (2 minutes)

### Step 1: Place the package in your working directory

```bash
# Option A: Move to your thesis directory
mv pals_analysis /path/to/your/thesis/code/

# Option B: Use it from downloads
cd /path/to/downloads/pals_analysis/..
```

### Step 2: Install dependencies

```bash
pip install numpy scipy matplotlib --break-system-packages
```

### Step 3: Test the installation

```python
# In Python or Jupyter
import sys
sys.path.insert(0, '/path/to/parent/directory')  # Adjust path

from pals_analysis import config
config.print_config()
```

If this works, you're ready to go! ✅

## Your First Analysis (5 minutes)

### Example 1: Quick Fit

```python
import numpy as np
from pals_analysis.analysis import solve_for_thickness
from pals_analysis.visualization import setup_thesis_style, plot_s_parameter_fit

# Setup plotting
setup_thesis_style()

# Your data
energies = np.array([1, 2, 3, 5, 8, 10, 15, 20])
s_exp = np.array([0.574, 0.568, 0.562, 0.551, 0.535, 0.528, 0.521, 0.520])
s_err = np.full(8, 0.002)

# Fit
d_ox, s_ox, d_err, s_err, info = solve_for_thickness(energies, s_exp, s_err)

print(f"Thickness: {d_ox:.1f} ± {d_err:.1f} nm")
print(f"S-oxide: {s_ox:.4f} ± {s_err:.4f}")

# Plot
plot_s_parameter_fit(energies, s_exp, s_err, d_ox, s_ox, save_as='my_fit.pdf')
```

That's it! You now have:
- Fitted oxide thickness
- Publication-quality PDF figure
- All uncertainties calculated

### Example 2: Run Complete Analysis

```bash
# Copy the example script
cp example_analysis.py my_analysis.py

# Edit with your data
# nano my_analysis.py  # or use VS Code

# Run it
python my_analysis.py
```

This creates:
- `results/s_parameter_fit.pdf` - Main figure
- `results/bootstrap_distributions.pdf` - Uncertainty analysis
- `results/analysis_summary.txt` - All numerical results

## Common Tasks

### Load Your CSV Data

```python
from pals_analysis.utils import load_experimental_data

data = load_experimental_data('your_data.csv')
energies = data['energies']
s_values = data['s_parameters']
s_errors = data['s_errors']
```

Expected CSV format:
```csv
Energy (keV), S-parameter, Error
1.0, 0.574, 0.002
2.0, 0.568, 0.002
...
```

### Change Material Properties

Edit `pals_analysis/config.py`:

```python
# For your specific oxide
RHO_OXIDE = 5.3  # Your measured density
S_BULK_STEEL = 0.51  # Your bulk S-parameter
```

### Create Depth Profile Plot

```python
from pals_analysis.physics import makhov_profile, calculate_annihilation_profile
from pals_analysis.visualization import plot_depth_profiles
from pals_analysis.utils import create_layer_config

# Setup
z = np.linspace(0, 500, 500)
layers = create_layer_config(d_ox=100)

# Calculate profiles
impl = makhov_profile(z, energy_kev=5, layers=layers)
ann = calculate_annihilation_profile(z, impl, layers)

# Plot
plot_depth_profiles(z, impl, ann, d_ox=100, energy_kev=5, 
                   save_as='depth_profile.pdf')
```

### Simulate an Energy Scan

```python
from pals_analysis.physics import simulate_pas_experiment
from pals_analysis.visualization import plot_energy_scan

energies = np.linspace(0.5, 25, 20)
layers = create_layer_config(d_ox=150, s_ox=0.54)

results = simulate_pas_experiment(energies, layers)
plot_energy_scan(results, save_as='simulation.pdf')
```

## Jupyter Notebook Template

```python
# Cell 1: Setup
import numpy as np
import matplotlib.pyplot as plt
from pals_analysis import config
from pals_analysis.analysis import solve_for_thickness
from pals_analysis.visualization import *
from pals_analysis.utils import *

setup_thesis_style()

# Cell 2: Load Data
data = load_experimental_data('my_data.csv')
energies = data['energies']
s_exp = data['s_parameters']
s_err = data['s_errors']

# Validate
is_valid, warnings = validate_data(energies, s_exp, s_err)
for w in warnings:
    print(w)

# Cell 3: Fit
d_ox, s_ox, d_err, s_err, info = solve_for_thickness(energies, s_exp, s_err)
print_fit_summary(d_ox, s_ox, d_err, s_err, info['chi_squared'])

# Cell 4: Plot
fig, ax = plot_s_parameter_fit(energies, s_exp, s_err, d_ox, s_ox)
plt.show()

# Cell 5: Save Results
results = {
    'thickness_nm': d_ox,
    'thickness_err_nm': d_err,
    's_oxide': s_ox,
    's_err': s_err
}
save_results('results.txt', results)
```

## File Organization

Recommended structure for your thesis:

```
your_thesis/
├── data/
│   ├── sample1.csv
│   ├── sample2.csv
│   └── ...
├── pals_analysis/          # The package
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_analysis.ipynb
│   └── 03_figures.ipynb
├── results/
│   ├── figures/
│   └── fits/
└── scripts/
    └── analyze_all.py
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pals_analysis'"

```python
# Add this at the top of your script/notebook
import sys
sys.path.insert(0, '/full/path/to/parent/directory')
import pals_analysis
```

### "DeprecationWarning: trapz is deprecated"

Update NumPy:
```bash
pip install --upgrade numpy --break-system-packages
```

### Fit not converging

Try different initial values:
```python
d_ox, s_ox, *_ = solve_for_thickness(
    energies, s_exp, s_err,
    initial_guess=[100, 0.56],  # Try different starting point
    bounds=([50, 0.52], [300, 0.58])  # Adjust bounds
)
```

### Figures look wrong

Make sure you called:
```python
from pals_analysis.visualization import setup_thesis_style
setup_thesis_style()  # Call this once at the start
```

## Getting More Help

1. **Read the full README**: `pals_analysis/README.md`
2. **Check function documentation**: All functions have detailed docstrings
3. **Look at examples**: `example_analysis.py` shows complete workflow
4. **Read the summary**: `REFACTORING_SUMMARY.md` explains the structure

## Next Steps

1. ✅ Install and test the package
2. ✅ Try the quick fit example above
3. ✅ Load your own data
4. ✅ Run analysis on your samples
5. ✅ Generate thesis figures
6. ✅ Add thesis section references to docstrings

---

**You're ready to analyze your PALS data! 🚀**

Questions? Check the README or examine the example_analysis.py script.
