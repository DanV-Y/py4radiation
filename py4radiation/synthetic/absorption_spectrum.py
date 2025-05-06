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

    def __init__(self, simnum, ds, shape, ions):
        self.simnum = simnum
        self.ds = ds
        self.shape = shape
        elements = ions[:, 0]
        self.ions = [f'{row[0]} {row[2]}' for row in ions]
        self.ionlabels = [f'{row[0]}{row[2]}' for row in ions]
        
        obs = './observables/'
        if not os.path.isdir(obs):
            os.mkdir(obs)
        self.obs = obs

        elements_paths = []
        for element in elements:
            path = obs + element + '/'
            if not os.path.isdir(path):
                os.mkdir(path)

            elements_paths.append(path)

        self.obs_path = elements_paths

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

        for i, ion in enumerate(self.ions):
            fname = f"{self.obs_path[i]}{self.simnum}_{self.ionlabels[i]}_ray{ray_name}.dat"
            spec = trident.SpectrumGenerator(lambda_min=-500, lambda_max=0, dlambda=1, bin_space='velocity')
            spec.make_spectrum(ray, lines=[ion])
            spec.save_spectrum(fname)
            print(f'{ion} DONE for ray {ray_name}')
