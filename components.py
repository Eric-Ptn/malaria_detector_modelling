from signals import OpticalSignal

class Laser():
    def __init__(self, name, laser_watts, wavelength_m, waist_radius_m = None, divergence_rad = None, FWHM_m = None):
        self.name = name
        self.laser_watts = laser_watts
        self.wavelength_m = wavelength_m
        self.waist_radius_m = waist_radius_m
        self.divergence_rad = divergence_rad
        self.FWHM_m = FWHM_m

        if not self.waist_radius_m or self.divergence_rad or self.FWHM_m:
            raise Exception('Must define one of waist radius, divergence, or FWHM.')

    def get_output(self):
        # fix polarization def
        return OpticalSignal(self.laser_watts, self.wavelength_m, 0, 1, self.waist_radius_m, self.divergence_rad, self.FWHM_m)


# inherit methods from here for optical surfaces
# if I can find models or rules of thumb for changes to beam waist through surfaces, I will implement that
class OpticalSurface():
    def __init__(self, name, transmission_polarization_angle = None, reflection_polarization_angle = None, 
                 transmission_polarization_ellipticity = None, reflection_polarization_ellipticity = None, 
                 transmission_coeff = None, reflection_coeff = None):
        self.name = name
        self.transmission_polarization_angle = transmission_polarization_angle
        self.reflection_polarization_angle = reflection_polarization_angle
        self.transmission_polarization_ellipticity = transmission_polarization_ellipticity
        self.reflection_polarization_ellipticity = reflection_polarization_ellipticity

        self.transmission_coeff = transmission_coeff
        self.reflection_coeff = reflection_coeff

        if not (self.transmission_coeff or self.reflection_coeff):
            raise Exception('Must define transmission or reflection coefficient.')
        elif not self.transmission_coeff:
            self.transmission_coeff = 1 - self.reflection_coeff
        elif not self.reflection_coeff:
            self.reflection_coeff = 1 - self.transmission_coeff
        elif self.transmission_coeff + self.reflection_coeff != 1:
            raise Exception('Transmission and reflection coefficients must sum to 1')
    
    # if the polarization parameters are not specified in __init__, the output has the same polarization as input
    def get_output_transmitted(self, input_signal):
        if not isinstance(input_signal, OpticalSignal):
            raise TypeError('Input to optical surface must be an optical signal.')
        
        transmission_polarization_angle = self.transmission_polarization_angle if self.transmission_polarization_angle is not None else input_signal.polarization_angle
        transmission_polarization_ellipticity = self.transmission_polarization_ellipticity if self.transmission_polarization_ellipticity is not None else input_signal.polarization_ellipticity      

        return OpticalSignal(input_signal.power_watts * self.transmission_coeff, input_signal.wavelength_m, 
                             transmission_polarization_angle, transmission_polarization_ellipticity, 
                             input_signal.waist_radius_m)

    # if the polarization parameters are not specified in __init__, the output has the same polarization as input
    def get_output_reflected(self, input_signal):
        if not isinstance(input_signal, OpticalSignal):
            raise TypeError('Input to optical surface must be an optical signal.')
        
        reflection_polarization_angle = self.reflection_polarization_angle if self.reflection_polarization_angle is not None else input_signal.polarization_angle
        reflection_polarization_ellipticity = self.reflection_polarization_ellipticity if self.reflection_polarization_ellipticity is not None else input_signal.polarization_ellipticity

        return OpticalSignal(input_signal.power_watts * self.reflection_coeff, input_signal.wavelength_m, 
                             reflection_polarization_angle, reflection_polarization_ellipticity, 
                             input_signal.waist_radius_m)


class UnpolarizedSplitter5050(OpticalSurface):
    def __init__(self, name):
        super().__init__(name, 
                         transmission_coeff=0.5, 
                         reflection_coeff=0.5)
        
class Polarized45Splitter5050(OpticalSurface):
    def __init__(self, name):
        super().__init__(name, 
                         transmission_polarization_angle=45,
                         reflection_polarization_angle=135,
                         transmission_coeff=0.5,
                         reflection_coeff=0.5)        

class Mirror(OpticalSurface):
    def __init__(self, name):
        super().__init__(name, 
                         transmission_coeff=1, 
                         reflection_coeff=0)

class ClearSurface(OpticalSurface):
    def __init__(self, name, transmission_coeff):
        super().__init__(name, 
                         transmission_coeff=transmission_coeff)
        
class LinearPolarizer(OpticalSurface):
    def __init__(self, name, angle, ellipticity):
        super().__init__(name, 
                         transmission_polarization_angle=angle,
                         transmission_polarization_ellipticity=ellipticity,
                         transmission_coeff=1,
                         reflection_coeff=0)

# do we have a relation for strength of magnetic field -> degree of polarization -> strength of polarization?
# 11/24/24 equations need updating as per Paul's Slack message
class HemozoinSolution(OpticalSurface):
    def __init__(self, name, hemozoin_concentration, depth):
        super().__init__(name, transmission_coeff=1) # temporarily define transmission coef...
        self.hemozoin_concentration = hemozoin_concentration
        self.depth = depth # distance light travels through solution

    def get_output_transmitted(self, input_signal):
        self.transmission_coeff = 1
        self.transmission_polarization_angle = None
        self.transmission_polarization_ellipticity = None
        return super().get_output_transmitted(input_signal)
    
    def get_output_reflected(self, input_signal):
        self.reflection_coeff = 0
        self.reflection_polarization_angle = None
        self.reflection_polarization_ellipticity = None
        return super().get_output_reflected(input_signal)
