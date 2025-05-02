#!/usr/bin/env python3

import os
import argparse
from configparser import ConfigParser

from mpi4py import MPI
import numpy as np

from py4radiation import simload, SED, ParameterFiles, IonTables, HeatingCoolingRates, SyntheticObservables, Diagnose

def main():
    parser = argparse.ArgumentParser(
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
            
        simpath = c['OBSERVABLES']['obs_simpath']
        simnum = c['OBSERVABLES']['obs_simnum']
        simfile = simpath + 'data.' + simnum + '.vtk'
        ions    = np.genfromtxt(c['OBSERVABLES']['obs_ionsfile'], dtype=None)
        units   = np.genfromtxt(c['OBSERVABLES']['obs_unitsfile'], dtype=None)[:, 1]

        if not os.path.isdir('./observables/'):
            os.mkdir('./observables/')

        fields, shape = simload(simfile)
        observables = SyntheticObservables(fields, shape, ions, units)
        observables.get_column_densities()
        print('Column Densities done')
        observables.get_mock_spectra()
        print('Mock absorption spectra done')

    elif mode == 3:
        print('CLOUD PROPERTIES mode')

        simpath = c['CLOUDS']['cl_simpath']
        simname = c['CLOUDS']['cl_simname']

        output_lines = ['n T v vx vy vz fmix x_CM y_CM z_CM x_sg y_sg z_sg vx_sg vy_sg vz_sg']

        if not os.path.isdir('./clouds/'):
            os.mkdir('./clouds/')

        sim_nums = ['{:04d}'.format(i) for i in range(81)]
        sim_files = [simpath + f'data.{sim}.vtk' for sim in sim_nums]

        fields_1, shape = simload(simpath + sim_files[0])
        diagnostics = Diagnose(fields_1, shape)
        
        for i in range(81):
            if i == 0:
                fields = fields_1
            else:
                fields, _ = simload(sim_files[i])
                
            avs, v_avs, fmix, j_cm, j_sg, v_sg = diagnostics.get_sim_diagnostics(fields)
            output_lines.append('{0:.14e} {1:.14e} {2:.14e} {3:.14e} {4:.14e} {5:.14e} {6:.14e} {7:.14e} {8:.14e} {9:.14e} {10:.14e} {11:.14e} {12:.14e} {13:.14e} {14:.14e} {15:.14e}'.format(avs[0], avs[1], avs[2], v_avs[0], v_avs[1], v_avs[2], fmix, j_cm[0], j_cm[1], j_cm[2], j_sg[0], j_sg[1], j_sg[2], v_sg[0], v_sg[1], v_sg[2]))
            print('Diagnostics done')
            
            diagnostics.get_cuts(fields, sim_nums[i])
            print('Cuts done')
            
            print(f'SIMULATION {i + 1} of 81 done')
            
        nfile = './clouds/' + simname + '_diagnostics.dat'
        with open(nfile, 'w') as f:
            f.write('\n'.join(output_lines))
            
        print('DIAGNOSTICS and CUTS done')

    else:
        print('FULL ANALYSIS mode')

        simpath = c['ANALYSIS']['simpath']
        simname = c['ANALYSIS']['simname']
        ions    = np.genfromtxt(c['ANALYSIS']['ionsfile'], dtype=None)
        units   = np.genfromtxt(c['ANALYSIS']['unitsfile'], dtype=None)[:, 1]

        if not os.path.isdir('./observables/'):
            os.mkdir('./observables/')

        if not os.path.isdir('./clouds/'):
            os.mkdir('./clouds/')

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
        
        sim_nums = ['{:04d}'.format(i) for i in range(81)]
        sim_files = [simpath + f'data.{sim}.vtk' for sim in sim_nums]

        fields_1, shape = simload(sim_files[0])
        diagnostics = Diagnose(fields_1, shape)
        print('FIRST SIMULATION LOADED')
        
        if rank == 0:
            output_lines = ['n T v vx vy vz fmix x_CM y_CM z_CM x_sg y_sg z_sg vx_sg vy_sg vz_sg']
            fields = fields_1
            observables = SyntheticObservables(sim_nums[0], fields, shape, ions, units)
            observables.get_column_densities()
            observables.get_mock_spectra()

            avs, v_avs, fmix, j_cm, j_sg, v_sg = diagnostics.get_sim_diagnostics(fields)
            line = ('{0:.14e} {1:.14e} {2:.14e} {3:.14e} {4:.14e} {5:.14e} {6:.14e} {7:.14e} {8:.14e} {9:.14e} {10:.14e} {11:.14e} {12:.14e} {13:.14e} {14:.14e} {15:.14e}'.format(avs[0], avs[1], avs[2], v_avs[0], v_avs[1], v_avs[2], fmix, j_cm[0], j_cm[1], j_cm[2], j_sg[0], j_sg[1], j_sg[2], v_sg[0], v_sg[1], v_sg[2]))
            output_lines.append(line)

            diagnostics.get_cuts(fields, sim_nums[0])
            print(f'SIMULATION 1 of 81 done')

        process = [j for j in range(1, 81) if (j - 1) % size == rank]
        local_data = []
        for k in process:
            fields, _ = simload(sim_files[k])
            observables = SyntheticObservables(sim_nums[k], fields, shape, ions, units)
            observables.get_column_densities()
            observables.get_mock_spectra()
            
            avs, v_avs, fmix, j_cm, j_sg, v_sg = diagnostics.get_sim_diagnostics(fields)
            line = ('{0:.14e} {1:.14e} {2:.14e} {3:.14e} {4:.14e} {5:.14e} {6:.14e} {7:.14e} {8:.14e} {9:.14e} {10:.14e} {11:.14e} {12:.14e} {13:.14e} {14:.14e} {15:.14e}'.format(avs[0], avs[1], avs[2], v_avs[0], v_avs[1], v_avs[2], fmix, j_cm[0], j_cm[1], j_cm[2], j_sg[0], j_sg[1], j_sg[2], v_sg[0], v_sg[1], v_sg[2]))
            local_data.append((k, line))
            
            diagnostics.get_cuts(fields, sim_nums[k])
            print(f'SIMULATION {k + 1} of 81 done')

        gathered = comm.gather(local_data, root=0)
        if rank == 0:
            all_data = [item for sublist in gathered for item in sublist]
            for k, line in sorted(all_data, key=lambda x: x[0]):
                output_lines.append(line)
                
            nfile = './clouds/' + simname + '_diagnostics.dat'
            with open(nfile, 'w') as f:
                f.write('\n'.join(output_lines))
            
        print('FULL ANALYSIS done')

if __name__ == '__main__':
    main()