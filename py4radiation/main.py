#!/usr/bin/env python3

import os
import sys
import argparse
from configparser import ConfigParser

import numpy as np
import pandas as pd

from .simload import simload
from radiation.prepare_sed import SED
from radiation.parfiles import ParameterFiles
from synthetic.observables import SyntheticObservables
from clouds.diagnose import Diagnose

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

        cloudypath = conf['RADIATION']['cloudypath']
        elements   = conf['RADIATION']['elements']
        resolution = conf['RADIATION']['resolution']

        parfiles = ParameterFiles(cloudypath, run_name, elements, redshift, resolution)
        parfiles.getIonFractions()
        parfiles.getHeatingCooling()

    elif mode == 1:
        print('SYNTHETIC OBSERVABLES mode')

        if os.path.isdir('./observables/'):
            None
        else:
            os.mkdir('./observables/')

        simpath = conf['SYNTHETIC']['simpath']
        simfile = simpath + conf['SYNTHETIC']['simfile']
        ions    = pd.read_csv(conf['SYNTHETIC']['ionsfile'], sep=r'\s+', header=None).to_numpy()
        units   = pd.read_csv(conf['SYNTHETIC']['unitsfile'], sep=r'\s+', header=None).to_numpy()[1]

        fields, shape = simload(simfile)
        observables = SyntheticObservables(fields, shape, ions, units)
        observables.get_column_densities()
        observables.get_mock_spectra()

    elif mode == 2:
        print('CLOUDS mode')

        if os.path.isdir('./clouds/'):
            None
        else:
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

        n_list = []
        T_list = []
        fmix_l = []
        ycm_ls = []
        xsg_ls = []
        ysg_ls = []
        zsg_ls = []
        vxsgls = []
        vysgls = []
        vzsgls = []

        for k in range(81):
            fields, _ = simload(simfiles[k])
            n_av, T_av, fmix, y_cm, j_sg, v_sg = diagnostics.get_sim_diagnostics(fields)
            n_list.append(n_av)
            T_list.append(T_av)
            fmix_l.append(fmix)
            ycm_ls.append(y_cm)
            xsg_ls.append(j_sg[0])
            ysg_ls.append(j_sg[1])
            zsg_ls.append(j_sg[2])
            vxsgls.append(v_sg[0])
            vysgls.append(v_sg[1])
            vzsgls.append(v_sg[2])

            diagnostics.get_cuts(fields, sinnums[k])

            print(f'Simulation {k + 1} out of 81 done')

        nfile = './clouds/' + sim_name + '_diagnostics.dat'
        stdout = sys.stdout
        with open(nfile, 'w') as f:
            sys.stdout = f
            for m in range(81):
                print('{0:.7E}'.format(n_list[m]) + '  ' + '{0:.7E}'.format(T_list[m]) + '  ' + '{0:.7E}'.format(fmix_l[m]) + '  ' + '{0:.7E}'.format(ycm_ls[m]) + '  ' + '{0:.7E}'.format(xsg_ls[m]) + '  ' + '{0:.7E}'.format(ysg_ls[m]) + '  ' + '{0:.7E}'.format(zsg_ls[m]) + '  ' + '{0:.7E}'.format(vxsgls[m]) + '  ' + '{0:.7E}'.format(vysgls[m]) + '  ' + '{0:.7E}'.format(vzsgls[m]))
            
            sys.stdout = stdout
        print('DIAGNOSE and CUTS done')

    else:
        raise Exception('MODES: (1) radiation (2) synthetic (3) clouds')
    
if __name__ == '__main__':
    main()
