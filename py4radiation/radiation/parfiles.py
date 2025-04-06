#!/usr/bin/env python3

import os
import sys

class ParameterFiles():
    """

    Parameter files for CIAOLoop using Cloudy C13.0
    Ion fractions for photoionisation and radiative heating & cooling


    **Parameters**

    :cloudypath: string

        Path to Cloudy C13.0 executable

    :run_name: string

        Name for the current CIAOLoop run

    :elements: string

        Elements for calculation of ion fractions

    :z: string

        Redshift

    :resolution: string, LOW or HIGH

        LOW: 81 log T points, 27 log hden points
        HIGH: 321 log T points, 105 log hden points

    """

    def __init__(self, cloudypath, run_name, elements, z, resolution='LOW'):

        self.cloudypath = cloudypath
        self.run_name   = run_name
        self.elements   = elements
        self.z          = z

        if resolution != 'LOW' and resolution != 'HIGH':
            raise Exception('Set resolution to either LOW or HIGH')

        if resolution == 'LOW':
            T_res    = 81
            hden_res = 0.5
        else:
            T_res    = 321
            hden_res = 0.125

        self.resolution = [T_res, hden_res]
        self.path = os.getcwd()

    def getIonFractions(self):
        """

        Get CIAOLoop parameter file for ion fractions

        """
        file = self.run_name + '_ib.par'

        stdout = sys.stdout
        with open(file, 'w') as f:
            sys.stdout = f
            print('#####################################################')
            print('########## ION FRACTION MAP PARAMETER FILE ##########')
            print('#####################################################')
            print()
            print('#####################################################')
            print('################## RUN  PARAMETERS ##################')
            print()
            print('# path to CLOUDY executable')
            print('cloudyExe               = ' + self.cloudypath)
            print()
            print('# save raw output from CLOUDY')
            print('saveCloidyOutputFiles   = 0')
            print()
            print('# exit if CLOUDY crashes')
            print('exitOnCrash             = 1')
            print()
            print('# run name')
            print('outputFilePrefix        = ' + self.run_name)
            print()
            print('# output path')
            print('outputDir               = ' + self.path + '/ib')
            print()
            print('# index of first run')
            print('runStartIndex           = 1')
            print()
            print('# TEST')
            print('test                    = 0')
            print()
            print('# run mode')
            print('cloudyRunMode           = 3')
            print()
            print('#####################################################')
            print('############ ION FRACTION MAP PARAMETERS ############')
            print()
            print('# min T')
            print('coolingMapTmin = 1e1')
            print()
            print('# max T')
            print('coolingMapTmax = 1e9')
            print()
            print('# T resolution (log points)')
            print('coolingMapTpoints = ' + str(self.resolution[0]))
            print()
            print('# elements')
            print('ionFractionElements = ' + self.elements)
            print()
            print('#####################################################')
            print('####################### LOOPS #######################')
            print()
            print('command stop zone 1')
            print()
            print('command iterate to convergence')
            print()
            print('loop [hden] (-9;4;' + str(self.resolution[1]) + ')')
            print()
            print('loop [init "' + self.path + '/' + self.run_name + 'z*.out"] ' + self.z)

            sys.stdout = stdout

    def getHeatingCooling(self):
        """

        Get CIAOLoop parameter file for radiative heating & cooling

        """

        file = self.run_name + '_hc.par'

        stdout = sys.stdout
        with open(file, 'w') as f:
            sys.stdout = f
            print('#####################################################')
            print('######## HEATING & COOLING MAP PARAMETER FILE #######')
            print('#####################################################')
            print()
            print('#####################################################')
            print('################## RUN  PARAMETERS ##################')
            print()
            print('# path to CLOUDY executable')
            print('cloudyExe               = ' + self.cloudypath)
            print()
            print('# save raw output from CLOUDY')
            print('saveCloidyOutputFiles   = 0')
            print()
            print('# exit if CLOUDY crashes')
            print('exitOnCrash             = 1')
            print()
            print('# run name')
            print('outputFilePrefix        = ' + self.run_name)
            print()
            print('# output path')
            print('outputDir               = ' + self.path + '/hc')
            print()
            print('# index of first run')
            print('runStartIndex           = 1')
            print()
            print('# TEST')
            print('test                    = 0')
            print()
            print('# run mode')
            print('cloudyRunMode           = 1')
            print()
            print('#####################################################')
            print('########## HEATING & COOLING MAP PARAMETERS #########')
            print()
            print('# min T')
            print('coolingMapTmin = 1e1')
            print()
            print('# max T')
            print('coolingMapTmax = 1e9')
            print()
            print('# T resolution (log points)')
            print('coolingMapTpoints = ' + str(self.resolution[0]))
            print()
            print('# scale factor')
            print('# 1 - n_H^2')
            print('# 2 - n_H * n_e')
            print('coolingScaleFactor = 1')
            print()
            print('#####################################################')
            print('####################### LOOPS #######################')
            print()
            print('command stop zone 1')
            print()
            print('command iterate to convergence')
            print()
            print('loop [hden] (-9;4;' + str(self.resolution[1]) + ')')
            print()
            print('loop [init "' + self.path + '/' + self.run_name + 'z*.out"] ' + self.z + ' 0.0001e+00')
            
            sys.stdout = stdout
