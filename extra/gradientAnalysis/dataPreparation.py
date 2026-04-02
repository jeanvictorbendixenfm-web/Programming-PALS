import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


Path = r"C:\Users\jeanv\OneDrive - Delft University of Technology\Uitwisseling - TUDelft\Courses\MEP\Experiments\nic\temperature_measurements"

# Loading data from the text files
global dataRun2
dataRun2 = np.loadtxt(Path + r"\Round2_copy.txt", delimiter="\t")
global dataRun1
dataRun1 = np.loadtxt(Path + r"\Round1_copy.txt", delimiter="\t")
global dataRun1_75015mm
dataRun1_75015mm = np.loadtxt(Path + r"\15mm750C_run1_copy.txt", delimiter="\t")
global dataRun3_part1
dataRun3_part1 = np.loadtxt(Path + r"\Round3_part1.txt", delimiter="\t")
global dataRun3_part2
dataRun3_part2 = np.loadtxt(Path + r"\Round3_part2.txt", delimiter="\t")

global timerun2, CH0run2, CH1run2, CH2run2, CH3run2
global timerun1, CH0run1, CH1run1, CH2run1, CH3run1
global timerun1_75015mm, CH0run1_75015mm, CH1run1_75015mm, CH2run1_75015mm, CH3run1_75015mm
global timerun3_part1, CH0run3_part1, CH1run3_part1, CH2run3_part1, CH3run3_part1
global timerun3_part2, CH0run3_part2, CH1run3_part2, CH2run3_part2, CH3run3_part2


timerun2 = dataRun2[:, 0]  # Time in [s]
CH0run2 = dataRun2[:, 1]   # Channel 0: Cold salt temperature in [°C]
CH1run2 = dataRun2[:, 2]   # Channel 1: Hot salt temperature in [°C]
CH2run2 = dataRun2[:, 3]   # Channel 2: Cold outer temperature in [°C] (called Copper Temp)
CH3run2 = dataRun2[:, 4]   # Channel 3: Hot outer temperature in [°C] (called Alumina Temp)

timerun1 = dataRun1[:, 0]
CH0run1 = dataRun1[:, 1]
CH1run1 = dataRun1[:, 2]
CH2run1 = dataRun1[:, 3]
CH3run1 = dataRun1[:, 4]

timerun1_75015mm = dataRun1_75015mm[:, 0]
CH0run1_75015mm = dataRun1_75015mm[:, 1]
CH1run1_75015mm = dataRun1_75015mm[:, 2]
CH2run1_75015mm = dataRun1_75015mm[:, 3]
CH3run1_75015mm = dataRun1_75015mm[:, 4]


timerun3_part1 = dataRun3_part1[:, 0]
CH0run3_part1 = dataRun3_part1[:, 1]
CH1run3_part1 = dataRun3_part1[:, 2]
CH2run3_part1 = dataRun3_part1[:, 3]
CH3run3_part1 = dataRun3_part1[:, 4]

timerun3_part2 = dataRun3_part2[:, 0]
CH0run3_part2 = dataRun3_part2[:, 1]
CH1run3_part2 = dataRun3_part2[:, 2]
CH2run3_part2 = dataRun3_part2[:, 3]
CH3run3_part2 = dataRun3_part2[:, 4]


## Events occuring doing operation
events_run2 = [
    (2100, "Melting event"),
    (2358, r"5V cooling"),
    (2690, r"8V cooling"),
    (2800, r"12V cooling"),
    (3100, r"$\uparrow$ Argon flow"),
    (4600, r"$\downarrow$ 7 [mm]"),
    (5600, r"$\downarrow$ Argon flow"),
    (6000, r"$\downarrow$ 5 [mm]"),
    (7000, r"$\downarrow$ 10 [mm]"),

    (7200, r"$T_{f} = 900 [°C]$"),
    (7700, r"$\uparrow$ Argon flow"),
    (8000, r"$14V$ cooling"),
    (8500, r"$\downarrow$ 10 [mm]"),
    (8750, r"$T_{f} = 1000 [°C]$")]



# 1. Define your conditions (The Time Intervals)
# You can add as many as you want here
conditions_furnace_run2 = [
    (timerun2 >= 0)    & (timerun2 < 7500),   # Pre-heating/Start
    (timerun2 >= 7500) & (timerun2 < 8500),   # First Plateau (750C)
    (timerun2 >= 8500) & (timerun2 < 10000),   # Second Plateau (900C)
    (timerun2 >= 10000)                       # Final Plateau (1000C)
]

conditions_furnace_run3 = [
    (timerun3_part1 >= 0)    & (timerun3_part1 < 6860),   # Pre-heating/Start
    (timerun3_part1 >= 6860) &    (timerun3_part1 < 10600),   # First Plateau (750C)
    (timerun3_part1 >= 10600) &    (timerun3_part1 < 11880),   # Second Plateau (900C)
    (timerun3_part1 >= 11880) &    (timerun3_part1 < 19000),   # Final Plateau (1000C)
    (timerun3_part1 >= 19000)                       # Final Plateau (1000C)
]

conditions_immersion_run2 = [
    (timerun2 >= 0)    & (timerun2 < 4600),   # Pre-heating/Start
    (timerun2 >= 4600) & (timerun2 < 6000),   # First Plateau (750C)
    (timerun2 >= 6000) & (timerun2 < 7000),   # Second Plateau (900C)
    (timerun2 >= 7000) & (timerun2 < 8500),   # Third Plateau (1000C)
    (timerun2 >= 8500)                       # Final Plateau (1000C)
]

conditions_immersion_run3 = [
    (timerun3_part1 >= 0)    & (timerun3_part1 < 10600),   # Pre-heating/Start
    (timerun3_part1 >= 10600)   # First Plateau (750C)
                     # Final Plateau (1000C)
]

# 2. Define the Temperature values for those intervals
values_furnace_run2 = [
    750,    # Room Temp
    900,   # 15mm Immersion Step
    1000,   # 1000C Step
    1000,

]

values_immersion_run2 = [
    -15,    # Room Temp
    -22,   # 15mm Immersion Step
    -27,   # 1000C Step
    -37,
    -47, 
]

values_furnace_run3 = [
    650,    # Room Temp
    700,   # 15mm Immersion Step
    750,   # 1000C Step
    850,
    850,
]

values_immersion_run3 = [
    -47,
    -52 
]

print(f"Time length: {len(timerun2)}")

# 3. Create the 1D temperature array
furnace_temps_run3 = np.select(conditions_furnace_run3, values_furnace_run3, default=0)
furnace_temps_run2 = np.select(conditions_furnace_run2, values_furnace_run2, default=0)
immersion_depths_run3 = np.select(conditions_immersion_run3, values_immersion_run3, default=0)
immersion_depths_run2 = np.select(conditions_immersion_run2, values_immersion_run2, default=0)

# 4. Combine into your (N, 2) array for your plotter
furnaceTemperatureTime_run2 = np.column_stack((timerun2, furnace_temps_run2))
furnaceTemperatureTime_run3 = np.column_stack((timerun3_part1, furnace_temps_run3))
furnaceImmersionTime_run2 = np.column_stack((timerun2, immersion_depths_run2))
furnaceImmersionTime_run3 = np.column_stack((timerun3_part1, immersion_depths_run3))


# Furnace and immersion depths of all data runs
fig, ax1 = plt.subplots(figsize=(12, 6), sharex=False)

ax1.plot(furnaceTemperatureTime_run3[:, 0], furnaceTemperatureTime_run3[:, 1], label='Run 3', color='lightcoral', lw=1)
ax1.plot(furnaceTemperatureTime_run2[:, 0], furnaceTemperatureTime_run2[:, 1], label='Run 2', color='darkred', lw=1)
ax2 = ax1.twinx()
ax2.plot(furnaceImmersionTime_run3[:, 0], furnaceImmersionTime_run3[:, 1], label='Immersion Depth', color='darkblue', lw=1)
ax2.plot(furnaceImmersionTime_run2[:, 0], furnaceImmersionTime_run2[:, 1], label='Immersion Depth', color='skyblue', lw=1)
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Furnace Temperature [°C]', color='red')
ax2.set_ylabel('Immersion Depth [mm]', color='blue')
plt.show()

