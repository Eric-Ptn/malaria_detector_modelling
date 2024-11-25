import constants
import components as cp


system = [
    [cp.Laser('LASER', laser_watts=2.5e-3, wavelength_m=650e-9, waist_radius_m=50e-6), 'FIRST'],
    [cp.LinearPolarizer('LINEAR POLARIZER', angle=90, ellipticity=5), 'TRANSMITTED'],
    [cp.UnpolarizedSplitter5050('UNPOLARIZED 5050 SPLITTER 1'), 'REFLECTED'],
    [cp.ClearSurface('CUVETTE GLASS IN', transmission_coeff=0.81), 'TRANSMITTED'],
    [cp.HemozoinSolution('HEMOZOIN', hemozoin_concentration=0, depth=0), 'TRANSMITTED'],
    [cp.ClearSurface('CUVETTE GLASS OUT', transmission_coeff=0.81), 'TRANSMITTED'],
    [cp.UnpolarizedSplitter5050('UNPOLARIZED 5050 SPLITTER 2'), 'TRANSMITTED'],
    [cp.Polarized45Splitter5050('POLARIZED 5050 SPLITTER'), 'REFLECTED']
]

signal_outputs = []

for element in system:
    component = element[0]
    descriptor = element[1]

    if descriptor == 'FIRST':
        this_output = component.get_output()        
    elif descriptor == 'TRANSMITTED':
        this_output = component.get_output_transmitted(signal_outputs[-1])
    elif descriptor == 'REFLECTED':
        this_output = component.get_output_reflected(signal_outputs[-1])

    print(f'{component.name}\n\t{repr(this_output)}\n')
    signal_outputs.append(this_output)
