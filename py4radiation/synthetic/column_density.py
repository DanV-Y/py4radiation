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

    def __init__(self, ds, shape, ions):
        self.ds = ds
        self.shape = shape
        elements = ions[:, 0]
        ionnums  = ions[:, 1].astype(int)

        species = []
        for i in range(len(elements)):
            species.append(elements[i] + '_p' + str(ionnums[i] - 1))

        self.ions = species

        self.obs = './observables/'

    def projYZ(self):
        """

        Get the YZ (transverse) column density map

        """
        for i in range(len(self.ions)):
            proj = self.ds.proj(self.ions[i] + '_number_density', 'x')
            arr  = np.array(proj[(self.ions[i] + '_number_density')])
            arr  = np.reshape(arr, (self.shape[1], self.shape[2]))

            fig_arr = '\n'.join(['\t'.join(map(str, row)) for row in arr])
            file_yz = self.obs + self.ions[i] + '_yz.dat'
            with open(file_yz, 'w') as file:
                file.write(fig_arr)

    def projXZ(self):
        """

        Get the XZ (down-the-barrel) column density map

        """
        for i in range(len(self.ions)):
            proj = self.ds.proj(self.ions[i] + '_number_density', 'y')
            arr  = np.array(proj[(self.ions[i] + '_number_density')])
            arr  = np.reshape(arr, (self.shape[0], self.shape[2]))

            fig_arr = '\n'.join(['\t'.join(map(str, row)) for row in arr])
            file_xz = self.obs + self.ions[i] + '_xz.dat'
            with open(file_xz, 'w') as file:
                file.write(fig_arr)
