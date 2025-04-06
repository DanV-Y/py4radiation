#/usr/bin/env python3

import os
import trident

import numpy as np

class MockSpectra():
    """

    Generate mock absorption spectra using rays across the cloud
    for a specific set of ions

    :ds: yt data grid
    
        Fields from the simulation file using the yt package

    :shape: tuple

        Dimensions of the computational box of the simulation

    :ions: numpy array

        Ions chosen for analysis
        They must be consistent with the ion fractions file for Trident

    """

    def __init__(self, ds, shape, ions):
        self.ds = ds
        self.shape = shape
        self.ds = ds
        self.shape = shape
        self.ions = list(ions[:, 0] + [' ', ' '] + ions[:, 2])
        self.obs  = './observables/'

    def raymaker(self, ray_name, start, end):
        """

        Generate rays across the cloud

        :ray_name: string

            Name assigned to the ray

        :start: list

            Rectangular coordinates of the starting point of the ray

        :end: list

            Rectangular coordinates of the ending point of the ray
        
        """

        ray = trident.make_simple_ray(self.ds,
                                start_position = start,
                                end_position = end,
                                data_filename = self.obs + 'ray_' + ray_name + '.h5',
                                lines = self.ions,
                                ftype = 'gas',
                                redshift = 0)
        
        print(f'Ray {ray_name} created')
        return ray
        
    def getSpectrum(self, ray, ray_name):
        """

        Generate mock absorption spectra for all the given ions
        using a ray across the cloud

        :ray: string

            Filename of ray, including path

        :ray_name:

            Name assigned to the ray
            Necessary to differentiate among rays

        """

        for i in self.ions:
            spec = trident.SpectrumGenerator(lambda_min=-500, lambda_max=0, dlambda=1, bin_space='velocity')
            spec.make_spectrum(ray, lines=[i])
            spec.save_spectrum(self.obs + i + '_ray_' + ray_name + '.dat')
            print(f'Ion {i} DONE')
