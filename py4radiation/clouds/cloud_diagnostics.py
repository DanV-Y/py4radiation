#/usr/bin/env python3

import numpy as np

class CloudDiagnostics():
    """

    Get diagnostics for gas in a VTK simulation file

    :j3D: numpy array

        3D reshaped axes for x, y, z

    :dV: numpy array

        Volume element of the computational box

    :M0: float

        Initial mass of the cloud

    """

    def __init__(self, j3D, dV, M0):
        self.j3D = j3D
        self.dV  = dV
        self.M0  = M0
        
        self.mu = 0.6724418
        self.mm = 1.660e-24
        self.kb = 1.380e-16

    def diagnose(self, fields):
        """

        Diagnose a single VTK file

        :fields: numpy array

            Scalar/vector fields from a VTK simulation file
            
        """

        rho, tr1, prs, vx, vy, vz = fields

        n = rho * tr1 / (self.mm * self.mu)
        T = prs * tr1 * self.mu * self.mm / (rho * self.kb)
        v = np.sqrt(vx**2 + vy**2 + vz**2) * tr1

        M = np.sum(rho * tr1) * self.dV
        
        def mwav(var):
            return np.sum(rho * var * tr1) * self.dV / M

        n_av = mwav(n)
        T_av = mwav(T)
        v_av = mwav(v)
        avs = [n_av, T_av, v_av]

        vx_av = mwav(vx)
        vy_av = mwav(vy)
        vz_av = mwav(vz)
        v_avs = [vx_av, vy_av, vz_av]

        mask = np.where((tr1 >= 0.01) & (tr1 <= 0.99), tr1, 0)
        fmix = np.sum(rho * mask) * self.dV / self.M0

        x_cm = mwav(self.j3D[0])
        y_cm = mwav(self.j3D[1])
        z_cm = mwav(self.j3D[2])
        j_cm = [x_cm, y_cm, z_cm]

        def sigma(var):
            s  = mwav(var)
            s2 = mwav(var**2)

            if np.isnan(s):
                sg = np.sqrt(s2)
            else:
                sg = np.sqrt(s2 - s**2)
            
            return sg

        x_sg = sigma(self.j3D[0]) * np.sqrt(5)
        y_sg = sigma(self.j3D[1]) * np.sqrt(5)
        z_sg = sigma(self.j3D[2]) * np.sqrt(5)
        j_sg = [x_sg, y_sg, z_sg]

        vx_sg = sigma(vx)
        vy_sg = sigma(vy)
        vz_sg = sigma(vz)
        v_sg = [vx_sg, vy_sg, vz_sg]

        return avs, v_avs, fmix, j_cm, j_sg, v_sg