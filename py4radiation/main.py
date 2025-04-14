#!/usr/bin/env python3

import os
import argparse
from configparser import ConfigParser

import numpy as np

from py4radiation import simload, SED, ParameterFiles, IonTables, HeatingCoolingRates, SyntheticObservables, Diagnose

def main():
    parser = argparse.ArgumentPaser(
        prog = 'py4radiation',
        description = 'UV radiation effects (photoionisation and radiative heating/cooling) into wind-cloud simulations'
    )

    parser.add_argument('-f', type=str, required=True, help='CONFIG file')

    file = parser.parse_args()
    c = ConfigParser()
    c.read(file.f)

    mode = int(c['MODE']['mode'])

    if not mode in [1, 2, 3, 4]:
        raise ValueError('Error: wrong mode.')

    if mode == 1:
        print('PHOTOIONISATION + RADIATIVE HEATING & COOLING mode')

        run_name = c['RADIATION']['run_name']
        redshift = c['RADIATION']['redshift']

        if c['RADIATION']['sedfile'] != None:
            sedfile = c['RADIATION']['sedfile']
            distance = c['RADIATION']['distance']
            age = c['RADIATION']['age']

            sed = SED(run_name, sedfile, distance, redshift, age)
            sed.getFile()
            print('SED file created.')

        elif c['RADIATION']['cloudypath'] != None:
            cloudypath = c['RADIATION']['cloudypath']
            elements = c['RADIATION']['elements']
            resolution = c['RADIATION']['resolution']

            parfiles = ParameterFiles(cloudypath, run_name, elements, redshift, resolution)
            parfiles.getIonFractions()
            parfiles.getHeatingCooling()
            print('IB/CH parameter files created.')

        elif c['RADIATION']['ibpath'] != None:
            ibpath = c['RADIATION']['ibpath']
            runfile = c['RADIATION']['runfile']
            outfile = c['RADIATION']['outfile']
            elements = c['RADIATION']['elements']

            ionbalance = IonTables(ibpath, runfile, outfile, elements)
            ionbalance.get_ion_tables()

        elif c['RADIATION']['hcpath'] != None:
            hcpath = c['RADIATION']['hcpath']
            runfile = c['RADIATION']['runfile']
            outfile = c['RADIATION']['outfile']

            hcrates = HeatingCoolingRates(hcpath, runfile, outfile)
            hcrates.get_hc_rates()

        else:
            raise ValueError('Error: wrong configuration.')

    elif mode == 2:
        print('SYNTHETIC OBSERVABLES mode')

        if not os.path.isdir('./observables/'):
            os.mkdir('./observables/')
            
        simpath = c['OBSERVABLES']['obs_simpath']
        simnum = c['OBSERVABLES']['obs_simnum']
        simfile = simpath + 'data.' + simnum + '.vtk'
        ions    = np.gendromtxt(c['OBSERVABLES']['obs_ionsfile'], dtype=None)
        units   = np.gendromtxt(c['OBSERVABLES']['obs_unitsfile'], dtype=None)[:, 1]

        fields, shape = simload(simfile)
        observables = SyntheticObservables(fields, shape, ions, units)
        observables.get_column_densities()
        print('Column Densities done')
        observables.get_mock_spectra()
        print('Mock absorption spectra done')

    elif mode == 3:
        print('CLOUD PROPERTIES mode')

        if not os.path.isdir('./clouds/'):
            os.mkdir('./clouds/')

        simpath = c['CLOUDS']['cl_simpath']
        simname = c['CLOUDS']['cl_simname']

        output_lines = ['n T v vx vy vz fmix x_CM y_CM z_CM x_sg y_sg z_sg vx_sg vy_sg vz_sg']

        sim_nums = []
        for i in range(81):
            if i < 10:
                sim_nums.append('000' + str(i))
            else:
                sim_nums.append('00' + str(i))
        
        sim_files = []
        for j in sim_nums:
            sim_files.append(simpath + 'data.' + j + '.vtk')

        fields_1, shape = simload(simpath + sim_files[0])
        diagnostics = Diagnose(fields_1, shape)
        
        for k in range(81):
            if i == 0:
                fields = fields_1
            else:
                fields, _ = simload(sim_files[k])
                
            avs, v_avs, fmix, j_cm, j_sg, v_sg = diagnostics.get_sim_diagnostics(fields)
            output_lines.append('{0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e}'.format(avs[0], avs[1], avs[2], v_avs[0], v_avs[1], v_avs[2], fmix, j_cm[0], j_cm[1], j_cm[2], j_sg[0], j_sg[1], j_sg[2], v_sg[0], v_sg[1], v_sg[2]))
            print('Diagnostics done')
            
            diagnostics.get_cuts(fields, sin_nums[k])
            print('Cuts done')
            
            print(f'SIMULATION {k + 1} of 81 done')
            
        nfile = './clouds/' + simname + '_diagnostics.dat'
        with open(nfile, 'w') as f:
            f.write('\n'.join(output_lines))
            
        print('DIAGNOSTICS and CUTS done')

    else:
        print('FULL ANALYSIS mode')

        if not os.path.isdir('./observables/'):
            os.mkdir('./observables/')

        if not os.path.isdir('./clouds/'):
            os.mkdir('./clouds/')

        simpath = c['ANALYSIS']['simpath']
        simname = c['ANALYSIS']['simname']
        ions    = np.gendromtxt(c['ANALYSIS']['ionsfile'], dtype=None)
        units   = np.gendromtxt(c['ANALYSIS']['unitsfile'], dtype=None)[:, 1]

        output_lines = ['n T v vx vy vz fmix x_CM y_CM z_CM x_sg y_sg z_sg vx_sg vy_sg vz_sg']
        
        sim_nums = []
        for i in range(81):
            if i < 10:
                sim_nums.append('000' + str(i))
            else:
                sim_nums.append('00' + str(i))
        
        sim_files = []
        for j in sim_nums:
            sim_files.append(simpath + 'data.' + j + '.vtk')

        fields_1, shape = simload(simpath + sim_files[0])
        diagnostics = Diagnose(fields_1, shape)
        
        for k in range(81):
            if i == 0:
                fields = fields_1
            else:
                fields, _ = simload(sim_files[k])
            
            observables = SyntheticObservables(fields, shape, ions, units)
            observables.get_column_densities()
            observables.get_mock_spectra()

            print('Observables done')
                
            avs, v_avs, fmix, j_cm, j_sg, v_sg = diagnostics.get_sim_diagnostics(fields)
            output_lines.append('{0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e} {0:.14e}'.format(avs[0], avs[1], avs[2], v_avs[0], v_avs[1], v_avs[2], fmix, j_cm[0], j_cm[1], j_cm[2], j_sg[0], j_sg[1], j_sg[2], v_sg[0], v_sg[1], v_sg[2]))
            print('Diagnostics done')
            
            diagnostics.get_cuts(fields, sim_nums[k])
            print('Cuts done')
            
            print(f'SIMULATION {k + 1} of 81 done')
            
        nfile = './clouds/' + simname + '_diagnostics.dat'
        with open(nfile, 'w') as f:
            f.write('\n'.join(output_lines))
            
        print('FULL ANALYSIS done')

if __name__ == '__main__':
    main()