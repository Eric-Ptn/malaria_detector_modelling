import math
import constants as c

# build optical model assuming perfect Gaussian beam
# https://en.wikipedia.org/wiki/Gaussian_beam
# TODO: not sure if it's more convenient to define optical signal power in terms of watts or peak intensity
# https://en.wikipedia.org/wiki/Polarization_(waves)
# defining polarization using angle and ellipticity
class OpticalSignal:
    def __init__(self, power_watts, wavelength_m, polarization_angle, polarization_ellipticity,
                  waist_radius_m = None, divergence_rad = None, FWHM_m = None):
        self.power_watts = power_watts
        self.wavelength_m = wavelength_m

        if polarization_angle >= 180:
            raise Exception('Polarization must be in range 0 <= x < 180.')
        self.polarization_angle = polarization_angle
        self.polarization_ellipticity = polarization_ellipticity

        # one of these three must be known to approximate laser intensity distribution
        self.waist_radius_m = waist_radius_m
        self.divergence_rad = divergence_rad
        self.FWHM_m = FWHM_m

        if waist_radius_m:
            self.divergence_rad = wavelength_m / (math.pi * c.n_air * self.waist_radius_m)
            self.FWHM_m = math.sqrt(2.0 * math.log(2.0)) * self.waist_radius_m
        elif divergence_rad:
            self.waist_radius_m = wavelength_m / (math.pi * c.n_air * self.divergence_rad)
            self.FWHM_m = math.sqrt(2.0 * math.log(2.0)) * self.waist_radius_m
        elif FWHM_m:
            self.waist_radius_m = self.FWHM_m / math.sqrt(2.0 * math.log(2.0))
            self.divergence_rad = wavelength_m / (math.pi * c.n_air * self.waist_radius_m)
        else:
            raise Exception('Must define one of waist radius, divergence, or FWHM.')
        
        # intensity of beam at the center
        self.peak_intensity_Wm2 = 2 * self.power_watts / (math.pi * self.waist_radius_m**2)

        # Rayleigh range
        self.z_r = math.pi * self.waist_radius_m**2 * c.n_air / self.wavelength_m

    def intensity_Wm2(self, r, z):
        w_z = self.__spot_radius_m(self.waist_radius_m, z, self.z_r)
        return self.peak_intensity_Wm2 * (self.waist_radius_m / w_z)**2 * math.exp(-2 * r**2 / w_z**2)
    
    def __spot_radius_m(self, z):
        return self.waist_radius_m * math.sqrt(1 + (z / self.z_r)**2)
    
    def __repr__(self):
        return f'Watts: {self.power_watts:.2e}, Wavelength m: {self.wavelength_m:.2e}, Polarization Angle deg: {self.polarization_angle:.2f}, Polarization Ellipticity: {self.polarization_ellipticity:.2f}, FWHM m: {self.FWHM_m:.2e}'


class ElectricalSignal:
    def __init__(self, voltage_amplitude, waveform, freq, dc_offset):
        self.voltage_amplitude = voltage_amplitude
        self.waveform = waveform
        self.freq = freq
        self.dc_offset = dc_offset 

    def v_min(self):
        return self.dc_offset - self.voltage_amplitude

    def v_max(self):
        return self.dc_offset + self.voltage_amplitude
    