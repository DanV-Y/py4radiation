#!/usr/bin/env python3

import os
import numpy as np

from .cloud_cuts import CloudCuts
from .cloud_diagnostics import CloudDiagnostics

class Diagnose():
    """

    Get a diagnosis of cloud gas in a VTK simulation file

    :fields_sim1: numpy array

        Scalar/vector fields of the first simulation file
        for initial conditions

    :shape: tuple

        Dimensions of the simulation box in computational units

    :box: list

        x, y, z physical limits of the computational box

    """

    def __init__(self, fields_sim1, shape, box):
        self.shape = shape
        box_x, box_y, box_z = box

        x = np.linspace(box_x[0], box_x[1], shape[0])
        y = np.linspace(box_y[0], box_y[1], shape[1])
        z = np.linspace(box_z[0], box_z[1], shape[2])

        self.j = [x, y, z]

        self.j3D = [x.reshape(-1, 1, 1), y.reshape(1, -1, 1), z.reshape(1, 1, -1)]

        dx = np.max(x) - np.min(x) / shape[0]
        dV = dx**3
        self.dV = dV

        rho, tr1, _, _, _, _ = fields_sim1

        self.M0 = np.sum(rho * tr1) * dV

    def get_sim_diagnostics(self, fields):
        """

        Get diagnostics of cloud gas in from a VTK simulation file

        :fields: numpy array

            Scalar/vector fields of a VTK simulation file

        :return: numpy arrays

            n_av, T_av, fmix, y_cm, j_sg, v_sg
            average density, average temperature, mixing fraction,
            y-position of the centre of mass, cloud gas dispersion,
            velocity dispersion
        
        """
        diagnostics = CloudDiagnostics(self.j3D, self.dV, self.M0)
        return diagnostics.diagnose(fields)

    def get_cuts(self, fields, sinnum):
        """

        Get cuts for number density and velocity

        :fields: numpy array

            Scalar/vector fields of a VTK simulation file

        :sinnum: string

            Number of the simulation to label output files

        """
        cuts = CloudCuts(fields, self.shape, sinnum)
        cuts.get_ncuts()
        cuts.get_vcuts()
