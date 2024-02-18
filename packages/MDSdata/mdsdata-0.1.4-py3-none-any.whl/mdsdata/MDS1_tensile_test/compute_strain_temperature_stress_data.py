# This is an implementation of the NIST report 
# https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.1907.pdf
# eq. 4.3, p. 91


import numpy as np
import matplotlib.pyplot as plt


class TrueStressStrainTemperatureCurves:
    T_ambient = 20. ##in °C
    
    def __init__(self):
        # For rolled structural steel, Table 2.2, p.19:
        self.r = {1: 7.514, 2: 1., 3: 588., 4: 676., 5: 0.09}  #  parameter for yield stress (r1..r5)
        self.k = {1: 7.82, 2: 540, 3: 145.9, 4: 0.759}  #  parameter for resulting stress
        self.n = 0.503  #  strain hardening exponent,
        self.e = {1: 3.768, 2: 1.0, 3: 639, 4: 1650}
        self.F_y0 = 50 # 50  ksi  345 MPa)
        self.E0 = 29900  # 29900 #ksi (206 GPa) is the value at ambient temperature (T=20°C)
        self.eps0_dot = 8.333e-5  # in 1/s
        self.KSI_to_MPa = 345 / 50
        

    def youngs_modulus(self, T):
        e = self.e
        # eq. 2.2
        #dT = T - 20  # 20 = ambient temperature
        dT = np.where(T < self.T_ambient, 0, T - self.T_ambient)
        return self.E0 * (np.exp(-0.5 * (dT / e[3]) ** e[1] - 0.5 * (dT / e[4]) ** e[2]))

    def yield_stress(self, T):  # F_y(T)
        r = self.r
        #dT = T - 20  # 20 = ambient temperature
        dT = np.where(T < self.T_ambient, 0, T - self.T_ambient)
        return self.F_y0 * (r[5] + (1 - r[5]) * np.exp(-0.5 * (dT / r[3]) ** r[1] - 0.5*(dT / r[4]) ** r[2]))

    def yield_strain(self, T):
        return self.yield_stress(T) / self.youngs_modulus(T)

    # true stress/strain!
    def _stress_function(self, strain, temperature):
        k = self.k
        eps_y = self.yield_strain(temperature)
        sig_y = self.yield_stress(temperature)
        deps = np.where(strain <= eps_y, 0, strain - eps_y)
        return np.where(strain <= eps_y, 
                        self.youngs_modulus(temperature) * strain, 
                        sig_y + \
                        (k[3] - k[4] * self.F_y0) * \
                            np.exp(-(temperature / k[2]) ** k[1]) * (deps ** self.n)
                       )

    def stress(self, 
               strain: (float, np.ndarray, list), 
               temperature: (float, np.ndarray, list),
               scale_strain=0., 
               scale_temperature=0, 
               scale_stress=0.):
        """Superimpose stress value with Laplacian noise
        
        scale_strain/temperature models the uncertainty of the input variables
        scale_stress models the uncertainty of the model
        
        :param scale_strain: amplitude of randomness superimposed on top of strain
        :param scale_temperature: amplitude of randomness superimposed on top of temperature
        :param scale_stress: amplitude of randomness superimposed on top of the resulting stress
        :returns: stresses either as 2D array or as 1D array (depending on if both strain and 
                  temperature are 1D arrays or not)
        """
        strain_is_scalar = isinstance(strain, (float, int))
        temp_is_scalar = isinstance(temperature, (float, int))
        strain = np.array([strain]) if strain_is_scalar else np.array(strain)
        temperature = np.array([temperature]) if temp_is_scalar else np.array(temperature)
        assert (strain.ndim == 1) and (temperature.ndim == 1), \
            "strain and temperature must be either scalars or 1D numpy arrays"
        
        temp_2D, strain_2D = np.meshgrid(temperature, strain)

        stress_2D = self._stress_function(strain_2D, temp_2D) + np.random.laplace(loc=0, scale=scale_stress, size=strain_2D.shape)

        strain_2D = strain_2D + np.random.laplace(loc=0, scale=scale_strain, size=strain_2D.shape)
        temp_2D = temp_2D + np.random.laplace(loc=0, scale=scale_temperature, size=temp_2D.shape)
                
        #noisy_stress = stress_2D[:, 0] if strain_is_scalar or temp_is_scalar else stress_2D
        #noisy_strain = strain + delta_strain
        #noisy_temp = temperature + delta_temp
        #return noisy_strain, noisy_temp, noisy_stress
        return strain_2D, temp_2D, stress_2D



def main():
    steel = TrueStressStrainTemperatureCurves()
    eps_y = steel.yield_strain(T=250)

    strain = np.append(np.linspace(0,eps_y, 50), np.linspace(eps_y, 0.01, 300))
    temperature = np.array([20, 250, 500, 600])

    eps, temp, sig = steel.stress(strain, temperature, scale_strain=0.00011, scale_temperature=0, scale_stress=1.)
    lines = plt.plot(eps, sig, '.', lw=0, ms=2)
    plt.legend(lines, [f"T={T}°C" for T in temperature])

    eps, temp, sig = steel.stress(strain, temperature)
    plt.gca().set_prop_cycle(None)
    plt.plot(eps, sig, lw=1., ls='-')


    plt.show()



if __name__ == '__main__':
    main()