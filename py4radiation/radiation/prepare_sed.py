#!/usr/bin/env python3

import os
import sys
import numpy as np
import pandas as pd

class SED():
    """

    Prepare SED to Cloudy/CIAOLoop readable files

    **Parameters**
    
    :sedfile: string 
        
        Path to SED file
        The first column must contain the wavelength in Angstroms
        The second (and other columns) must contain the luminosity 
        in erg s^-1 A^-1 for the radiation source at different ages

    :distance: float

        Distance of the cloud to the radiation source in kpc

    :z: string

        Redshift (use 0.0000e+00 as format)

    :age: int, sb99 format, optional

        Age of the starburst in Myr

    """

    def __init__(self, sedfile, distance, z, age=1):
        self.sed = pd.read_csv(sedfile, sep=r'\s+', header=None).to_numpy()
        
        self.distance = distance * 3.086e+21
        self.z        = float(z)
        self.zn       = z
        
        if 30 <= age <= 100:
            self.age = age/10 + 18
        elif 200 <= age <= 900:
            self.age = age/100 + 27
        else:
            self.age = age

    def getSED(self):
        """

        Calculate energy (in Ryd) and intensity 

        """

        wavelength = self.sed[:, 0].astype(float)
        frequency  = 3.e+8 / (wavelength * 1.e-10)
        energy = frequency * 4.135667696e-15 / 13.65

        luminosity = self.sed[:, self.age].astype(float)
        lum = 10**(luminosity) * wavelength**2 / 3.e+18
        j_nu = lum / (4 * np.pi * self.distance**2) 

        return [energy, j_nu]

    def getFile(self):
        """

        Get Cloudy C13/CIAOLoop readable SED file

        """

        en, jnu = self.getSED()

        stdout = sys.stdout
        nfile  = 'SED_z' + self.zn + '.out'

        with open(nfile, 'w') as f:
            sys.stdout = f
            print(f'# SED profile at {self.age} Myr')
            print(f'# z = {self.zn}')
            print('# E [Ryd] log10 (J_nu)')

            for i in range(len(en) - 1, 0, -1):
                if i == (len(en) - 1):
                    print('interpolate (' + '{:.10f}'.format(en[i]) + ' ' + '{:.10f}'.format(jnu[i]) + ')', sep='')
                else:
                    print('continue (' + '{:.10f}'.format(en[i]) + ' ' + '{:.10f}'.format(jnu[i]) + ')', sep='')

                if 0.99 <= en[i] <= 1.01:
                    nfactor = jnu[i]

            norm = np.log10(4 * np.pi * 10**nfactor)
            
            print('f(nu) = ' + '{:.14f}'.format(norm) + ' at 1.0000000000 Ryd', sep='')
            sys.stdout = stdout

