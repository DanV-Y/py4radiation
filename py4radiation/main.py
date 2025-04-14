#!/usr/bin/env python3

import os
import sys
import argparse
from configparser import ConfigParser

import numpy as np

from .simload import simload
from .radiation.prepare_sed import SED
from .radiation.parfiles import ParameterFiles
from .synthetic.observables import SyntheticObservables
from .clouds.diagnose import Diagnose

def main():
    parser = argparse.ArgumentParser(
        prog = 'py4radiation',
        description = 'UV radiation effects into HD/MHD wind-cloud simulations'
    )

    parser.add_argument('-f', type='str', required=True, help='CONFIG file')

    file = parser.parse_args()
    conf = ConfigParser()
    conf.read(file.f)

    mode = int(conf['MODE']['mode'])

    if mode == 0:
        print('PHOTOIONISATION + RADIATIVE HEATING & COOLING mode')

        run_name = conf['RADIATION']['run_name']
        redshift = conf['RADIATION']['redshift']

        if conf['RADIATION']['sedfile'] != None:
            sedfile = conf['RADIATION']['sedfile']
            distance = conf['RADIATION']['distance']
            age      = conf['RADIATION']['age']

            sed = SED(run_name, sedfile, distance, redshift, age)
            sed.getFile()

        elif conf['RADIATION']['cloudypath'] != None:
            cloudypath = conf['RADIATION']['cloudypath']
            elements   = conf['RADIATION']['elements']
            resolution = conf['RADIATION']['resolution']
            
            parfiles = ParameterFiles(cloudypath, run_name, elements, redshift, resolution)
            parfiles.getIonFractions()
            parfiles.getHeatingCooling()

        else:
            raise ValueError('Error: wrong configuration')

    elif mode == 1:
        print('SYNTHETIC OBSERVABLES mode')

        if not os.path.isdir('./observables/'):
            os.mkdir('./observables/')

        simpath = conf['SYNTHETIC']['simpath']
        simfile = simpath + conf['SYNTHETIC']['simfile']
        ions    = np.loadtxt(conf['SYNTHETIC']['ionsfile'])
        units   = np.loadtxt(conf['SYNTHETIC']['unitsfile'])[:, 1]

        fields, shape = simload(simfile)
        observables = SyntheticObservables(fields, shape, ions, units)
        observables.get_column_densities()
        observables.get_mock_spectra()

    elif mode == 2:
        print('CLOUDS mode')

        if not os.path.isdir('./clouds/'):
            os.mkdir('./clouds/')

        simpath  = conf['CLOUDS']['simpath']
        sim_name = conf['CLOUDS']['simname']
        box_x   = np.array(conf['CLOUDS']['box_x'].split()).astype(int)
        box_y   = np.array(conf['CLOUDS']['box_y'].split()).astype(int)
        box_z   = np.array(conf['CLOUDS']['box_z'].split()).astype(int)

        box = [box_x, box_y, box_z]

        fields_sim1, shape = simload(simpath + 'data.0000.vtk')
        diagnostics = Diagnose(fields_sim1, shape, box)
        
        sinnums = []
        for i in range(81):
            if i < 10:
                sinnums.append('000' + str(i))
            else:
                sinnums.append('00' + str(i))

        simfiles = []
        for j in sinnums:
            simfiles.append(simpath + 'data.' + j + '.dat')

        output_lines = ['n T v vx vy vz fmix x_CM y_CM z_CM x_sg y_sg z_sg vx_sg vy_sg vz_sg']

        for k in range(81):
            if i == 0:
                fields = fields_sim1
            else:
                fields, _ = simload(simfiles[k])

            avs, v_avs, fmix, j_cm, j_sg, v_sg = diagnostics.get_sim_diagnostics(fields)

            output_lines.append('{0:.14e} {0:.14e} {0:.14f} {0:.14e} {0:.14f} {0:.14e} {0:.14f} {0:.14e} {0:.14f} {0:.14e} {0:.14f} {0:.14f} {0:.14f} {0:.14f} {0:.14f} {0:.14f}'.format(avs[0], avs[1], avs[2], v_avs[0], v_avs[1], v_avs[2], fmix, j_cm[0], j_cm[1], j_cm[2], j_sg[0], j_sg[1], j_sg[2], v_sg[0], v_sg[1], v_sg[2]))

            diagnostics.get_cuts(fields, sinnums[k])

            print(f'Simulation {k + 1} out of 81 done')

        nfile = './clouds/' + sim_name + '_diagnostics.dat'
        with open(nfile, 'w') as f:
            f.write('\n'.join(output_lines))


        print('DIAGNOSE and CUTS done')

    else:
        raise Exception('MODES: (1) radiation (2) synthetic (3) clouds')
    
if __name__ == '__main__':
    main()
