import numpy as np

def rho(T):

    rho_CeCl_3 = 3.25 + 0.00092 * (T - 817)
    rho_NaCl = 1.556 + 0.000543 * (T-800.17)
    rho_MgCl_2 = 1.68 + 0.000271 * (T-714)

    if T < 826:
        print("Temperature is below the above threshold of MgCl2")

    if T > 817:
        print("Temperature is below the meltingpoint of CeCl3")
    return 0.0808 * rho_CeCl_3 + 0.58443 * rho_NaCl + 0.3516 * rho_MgCl_2


n = np.array([500, 600, 700])

print(rho(n[700]))

