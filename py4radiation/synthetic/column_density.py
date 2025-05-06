#/usr/bin/env python3

import os
import numpy as np

class ColumnDensity():
    """
    
    Generate column density maps for wind-cloud simulations
    in down-the-barrel and transverse views

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
        ionnums  = ions[:, 1].astype(int)

        species = []
        for i in range(len(elements)):
            species.append(elements[i] + '_p' + str(ionnums[i] - 1))

        self.ions = species
        self.ionlabels = [f'{row[0]}{row[2]}' for row in ions]

        obs = './observables/'

        if not os.path.isdir(obs):
            os.mkdir(obs)

        elements_paths = []
        for element in elements:
            path = obs + element + '/'
            if not os.path.isdir(path):
                os.mkdir(path)

            elements_paths.append(path)

        self.obs_path = elements_paths


    def projYZ(self):
        """

        Get the YZ (transverse) column density map

        """
        for i, ion in enumerate(self.ions):
            proj = self.ds.proj(ion + '_number_density', 'x')
            arr  = np.array(proj[(ion + '_number_density')])
            arr  = np.reshape(arr, (self.shape[1], self.shape[2]))

            fig_arr = '\n'.join(['\t'.join(map(str, row)) for row in arr])
            file_yz = self.obs_path[i] + self.simnum + '_' + self.ionlabels[i] + '_coldens_yz.dat'
            with open(file_yz, 'w') as file:
                file.write(fig_arr)

    def projXZ(self):
        """

        Get the XZ (down-the-barrel) column density map

        """
        for i, ion in enumerate(self.ions):
            proj = self.ds.proj(ion + '_number_density', 'y')
            arr  = np.array(proj[(ion + '_number_density')])
            arr  = np.reshape(arr, (self.shape[0], self.shape[2]))

            fig_arr = '\n'.join(['\t'.join(map(str, row)) for row in arr])
            file_xz = self.obs_path[i] + self.simnum + '_' + self.ionlabels[i] + '_coldens_xz.dat'
            with open(file_xz, 'w') as file:
                file.write(fig_arr)
