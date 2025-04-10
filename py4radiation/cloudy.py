#!/usr/bin/env python3

import os
import glob
import subprocess

class CloudyRoutines():
    """
    Cloudy C13 routines for ion fractions and radiative heating/cooling
    Adaptation of CIAOLoop by Britton Smith from PERL to PYTHON
    (https://github.com/brittonsmith/cloudy_cooling_tools/blob/main/CIAOLoop)
    """

    def __init__(self, parameter_file): 
        self.parameter_file = parameter_file

    # General functions

    def read_parameter_file(self):
        with open(self.parameter_file, 'r') as f:
            lines = [line.split() for line in f]

        param_flag = ['cloudyExe',
                      'saveCloudyOutputFiles',
                      'exitOnCrash',
                      'outputFilePrefix',
                      'outputDir',
                      'runStartIndex',
                      'test',
                      'cloudyRunMode',
                      'coolingMapTmin',
                      'coolingMapTmax',
                      'coolingMapTpoints',
                      'loop [hden]',
                      'loop [init']
        
        parameters = []
        param_index = 0

        for line in lines:
            if line.startswith(param_flag[param_index]):
                parameters.append(line[2])
                param_index += 1
                if param_index == 11:
                    if '1' in parameters[7]:
                        param_flag.insert(11, 'ionFractionElements')
                    elif '2' in parameters[7]:
                        param_flag.insert(11, 'coolingScaleFactor')
                    else:
                        raise ValueError('Error: wrong running mode')
                    
        return parameters