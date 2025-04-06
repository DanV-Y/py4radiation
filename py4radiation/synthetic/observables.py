#/usr/bin/env python3

import os

import yt
import trident

import numpy as np
import pandas as pd

from .absorption_spectrum import MockSpectra
from .column_density import ColumnDensity

class SyntheticObservables():
    """

    Generate synthetic observables (column densities and mock spectra)
    from a single VTK simulation file

    :fields: numpy array

        Scalar/vector fields from a VTK simulation file

    :shape: tuple

        Shape of the computational box of the simulation

    :ions: numpy array

        Set of ions for analysis

    :units: numpy array

        Units array in the following order:
        [0] density
        [1] pressure
        [2] velocity
        [3] length

    """

    def __init__(self, fields, shape, ions, units):

        mm = 1.660e-24   # 1 amu
        mu = 6.724418e-1 
        kb = 1.380e-16   # Boltzmann constant in cgs

        rho = fields[0] * units[0]
        tr1 = fields[1]
        prs = fields[2] * units[1]
        vx1 = fields[3] * units[2]
        vx2 = fields[4] * units[2]
        vx3 = fields[5] * units[2]
        T   = prs * mu * mm / (rho * kb)

        metal = np.ones((shape[0], shape[1], shape[2]))
        bbox  = np.array([[-shape[0]/2, shape[0]/2], [0, shape[1]], [-shape[2]/2, shape[2]/2]], dtype=int)

        data = {
            ('gas', 'density'): (rho, 'g/cm**3'),
            ('gas', 'temperature'): (T, 'K'),
            ('gas', 'metallicity'): (metal, 'Zsun'),
            ('gas', 'velocity_x'): (vx1, 'cm/s'),
            ('gas', 'velocity_y'): (vx2, 'cm/s'),
            ('gas', 'velocity_z'): (vx3, 'cm/s')
        }

        length   = units[3] * 0.039
        mass     = units[0] * length**3
        velocity = units[2]

        ds = yt.load_uniform_grid(data, shape,
                                  length_unit = (length, 'cm'),
                                  mass_unit = (mass, 'g'),
                                  velocity_unit = (velocity, 'cm/s'),
                                  bbox = bbox,
                                  nprocs = 1)

        species = list(ions[:, 0] + [' ', ' '] + ions[:, 2])
        
        trident.add_ion_fields(ds, ions=species, ftype='gas')

        self.ds    = ds
        self.shape = shape
        self.ions  = ions

        obs_path = './observables/'

        if os.path.isdir(obs_path):
            None
        else:
            os.mkdir(obs_path)

    def get_column_densities(self):
        """

        Get down-the-barrel and transverse column density maps
        
        """
        cols = ColumnDensity(self.ds, self.shape, self.ions)
        cols.projXZ()
        cols.projYZ()

        print('Column density maps DONE')

    def get_mock_spectra(self):
        """

        Get absorption spectra for three default rays
        
        """
        spectra = MockSpectra(self.ds, self.shape, self.ions)

        rays = []
        rays.append(spectra.raymaker('r1', [0, 0, 0], [0, self.shape[1], 0]))
        rays.append(spectra.raymaker('r2', [8, 0, 0], [8, self.shape[1], 0]))
        rays.append(spectra.raymaker('r3', [16, 0, 0], [16, self.shape[1], 0]))

        for i in range(3):
            spectra.getSpectrum(rays[i], 'r' + str(i))
        
        print('Mock absorption spectra DONE')
