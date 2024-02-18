import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from mdsdata.MDS1_tensile_test.compute_strain_temperature_stress_data import TrueStressStrainTemperatureCurves

KSI_to_MPa = 345 / 50
MPa_to_KSI = 1 / KSI_to_MPa

def main():
    rng = np.random.default_rng(0)


    steel = TrueStressStrainTemperatureCurves()
    eps_y = steel.yield_strain(T=250)
    strain = np.append(np.linspace(0,eps_y, 50), np.linspace(eps_y, 0.02, 300))
    temperature = np.array([0, 400,  600], dtype=float)

    n_samples = len(strain)

    # define material parameter and the respective noise
    E0 = 206e3 * MPa_to_KSI
    stddev_E0 = 0.05 * E0
    E0_values = rng.normal(E0, stddev_E0, size=n_samples)

    F_y0 = 345 * MPa_to_KSI
    stddev_F_y0 = 0.04 * F_y0
    F_y0_values = rng.normal(F_y0, stddev_F_y0, size=n_samples)

    strain_hardening_exp = 0.503
    stddev_strain_hardening_exp = 0.03 * strain_hardening_exp
    strain_hardening_exp_values = rng.normal(strain_hardening_exp, stddev_strain_hardening_exp, size=n_samples)

    # set the amount of Gaussian noise for stress, strain, and temperature
    stddev_strain = 0.0001
    stddev_stress = 0.5
    stddev_temperature = 0.1


    fig, ax = plt.subplots()

    # Iterate through each data point. For each point, we use a new set
    # # of material parameter that differ by some random noise value.
    all_strain_values = np.empty((n_samples, len(temperature)), dtype=float)
    all_stress_values = np.empty_like(all_strain_values, dtype=float)

    
    for i in range(n_samples):
        steel.E0 = E0_values[i]
        steel.F_y0 = F_y0_values[i]
        steel.n = strain_hardening_exp_values[i]


        for j in range(len(temperature)):
            eps, temp, sig = \
                steel.stress(
                    strain[i], 
                    temperature[j],
                    scale_strain=stddev_strain,
                    scale_temperature=stddev_temperature,
                    scale_stress=stddev_stress
                )
            all_strain_values[i, j] = eps 
            all_stress_values[i, j] = sig 

            label = f"T={temperature[j]}°C" if i == 0 else ""
            ax.plot(eps, sig, '.', ms=4, c=f"C{j}", label=label)

    ax.legend()
    ax.set(xlabel=r"true stress $\sigma$", 
           ylabel=r"true strain $\varepsilon$",
           xlim=(-0.0002, 0.02), 
           ylim=(-1, 70))
    # plt.show()

    columns=[f'{t:.0f}°C' for t in temperature]
    df = pd.DataFrame(data=all_strain_values, columns=columns)
    df.to_csv('strain.csv')

    df = pd.DataFrame(data=all_stress_values, columns=columns)
    df.to_csv('stress.csv')

if __name__ == '__main__':
    main()