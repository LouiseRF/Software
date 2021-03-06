#!python2
# -*- coding: utf-8 -*-
"""Solenoid Field Map
Ben Shepherd, April 2017
Given a named solenoid and current, provides a field map.
Combined solenoid and bucking coil maps are handled too."""

import numpy as np
from collections import namedtuple
import scipy.interpolate

# Solenoids that we know about.
# The ones prefixed 'gb-' are referenced in the Gulliford/Bazarov paper.
SOLENOID_LIST = ('gb-rf-gun', 'gb-dc-gun', 'Gun-10')

field_map_attr = namedtuple('field_map_attr', 'coeffs z_map bc_area bc_turns sol_area sol_turns')

def interpolate(x, y):
    "Return an interpolation object with some default parameters."
    if scipy.version.full_version >= '0.17.0':
        interp = scipy.interpolate.interp1d(x, y, fill_value='extrapolate', bounds_error=False)
    else:
        # numpy <0.17.0 doesn't allow extrapolation - so use the values at the start and end
        x = np.insert(x, 0, -1e99)
        y = np.insert(y, 0, y[0])
        x = np.append(x, 1e99)
        y = np.append(y, y[-1])
        interp = scipy.interpolate.interp1d(x, y, bounds_error=False)
    return interp


class Solenoid():
    """Create a reference to a known solenoid."""

    def __init__(self, name, quiet=True):
        """Initialise the class, setting parameters relevant to the named setup."""
        self.quiet = quiet
        if not name in SOLENOID_LIST:
            raise NotImplementedError('Unknown solenoid "{name}". Valid names are {SOLENOID_LIST}.'.format(**locals()))
        self.name = name
        self.calc_done = False
        if name == 'Gun-10':
            # magnetic field map built up from coefficients for x**n and y**n
            # where x = BC current density
            # and y = solenoid current density
            # and n <= 3
            # See BJAS' spreadsheet: coeffs-vs-z.xlsx
            # This takes care of interaction between the BC and solenoid
            self.b_field = field_map_attr(coeffs=np.loadtxt('gun10-coeffs-vs-z.csv', delimiter=','),
                                          z_map=np.arange(-12, 467, dtype='float64') * 1e-3,
                                          bc_area=856.0, bc_turns=720.0, sol_area=8281.0, sol_turns=144.0)
            self.z_map = self.b_field.z_map
            self.bc_current = 5.0  # reasonable default value
            self.sol_current = 300.0  # reasonable default value

        elif name[:3] == 'gb-':
            self.bc_current = 0.0
            self.sol_current = 300.0  # just a made-up number

            # Define this in a simpler way - then we can just multiply by sol_current to get B-field value
            z_list, B_list = np.loadtxt('gb-field-maps/{}_b-field.csv'.format(name), delimiter=',').T
            self.b_field = np.array([z_list, B_list / self.sol_current])

        self.bmax_index = np.argmax(self.getMagneticFieldMap())  # assume this won't change with sol/BC currents

    def setBuckingCoilCurrent(self, current):
        """Reset the bucking coil current to a new value."""
        if current != self.bc_current:
            self.bc_current = float(current)
            self.calc_done = False

    def setSolenoidCurrent(self, current):
        """Reset the solenoid current to a new value."""
        if current != self.sol_current:
            self.sol_current = float(current)
            self.calc_done = False

    def calcMagneticFieldMap(self):
        """Calculate the magnetic field map for given solenoid and BC currents."""
        if isinstance(self.b_field, tuple):
            # Coefficients describing how the B-field depends on the sol/BC currents
            X = self.bc_current * self.b_field.bc_turns / self.b_field.bc_area
            Y = self.sol_current * self.b_field.sol_turns / self.b_field.sol_area
            # Use a subset of coefficients
            A = np.array(
                [Y, Y ** 2, Y ** 3, X, X * Y, X * Y ** 2, X ** 2, X ** 2 * Y,
                 X ** 2 * Y ** 2, X ** 2 * Y ** 3, X ** 3, X ** 3 * Y]).T
            self.B_map = np.dot(self.b_field.coeffs, A)
            self.z_map = self.b_field.z_map
        else:
            # we've defined it as just an array, multiply by sol current to get field
            self.z_map, B_map = self.b_field
            self.B_map = B_map * self.sol_current
        self.B_interp = interpolate(self.z_map, self.B_map)
        self.calc_done = True

    def getZMap(self):
        """Return the longitudinal (z) coordinates used in the field map."""
        return self.z_map

    def getMagneticFieldMap(self):
        """Return the magnetic field map produced by the solenoid and bucking coil."""
        if not self.calc_done:
            self.calcMagneticFieldMap()
        return self.B_map

    def getMagneticField(self, z):
        """Return the magnetic field at a given z coordinate."""
        if not self.calc_done:
            self.calcMagneticFieldMap()
        return float(self.B_interp(z))

    def getPeakMagneticField(self):
        """Return the peak solenoid field in T."""
        if not self.calc_done:
            self.calcMagneticFieldMap()
        return float(self.B_map[self.bmax_index])

    def optimiseParam(self, opt_func, operation, x_name, x_units, target=None, target_units=None, tol=1e-6):
        """General function for optimising a parameter by varying another."""
        # operation should be of form "Set peak field" etc.
        x_init = getattr(self, x_name)
        if not self.quiet:
            target_text = '' if target == None else ', target {target:.3f} {target_units}'.format(**locals())
            print('{operation}{target_text}, by varying {x_name} starting at {x_init:.3f} {x_units}.'.format(**locals()))
        xopt = scipy.optimize.fmin(opt_func, x_init, xtol=1e-3, disp=not self.quiet)
        if not self.quiet:
            print('Optimised with {x_name} setting of {0:.3f} {x_units}'.format(float(xopt), **locals()))
        return float(xopt)

    def bcCurrentToCathodeField(self, bci):
        self.setBuckingCoilCurrent(bci)
        return self.getMagneticField(0.0)

    def setCathodeField(self, field=0.0):
        """Set the cathode field to a given level by changing the bucking coil 
        current, and return the value of this current."""
        delta_B_sq = lambda bci: (self.bcCurrentToCathodeField(bci) - field) ** 2
        return self.optimiseParam(delta_B_sq, 'Set field at cathode', 'bc_current', 'A', field, 'T')

    def solCurrentToPeakField(self, sol_current):
        self.setSolenoidCurrent(sol_current)
        return self.getPeakMagneticField()

    def setPeakMagneticField(self, field):
        """Set the peak magnetic field to a given level (in T) by changing the 
        solenoid current, and return the value of this current."""
        delta_B_sq = lambda soli: (self.solCurrentToPeakField(soli) - field) ** 2
        return self.optimiseParam(delta_B_sq, 'Set solenoid peak field', 'sol_current', 'A', field, 'T')

