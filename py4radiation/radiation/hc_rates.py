#!/usr/bin/env python3

import numpy as np

class HeatingCoolingRates():
    """

    Get PLUTO-readable heating and cooling rates

    """

    def __init__(self, path, runfile, outfile):
        self.path = path
        self.pathfile = path + runfile
        self.runfile = runfile
        self.outfile = outfile

    def get_hc_rates(self):
        """

        Get a single file with radiative heating & cooling
        to use for PLUTO HD/MHD simulations

        """

        print(f'Adapting radiative heating & cooling from {self.runfile} to {self.outfile}')

        if not self.runfile.endswith('.run'):
            raise ValueError('Error: run file needs to end in .run')
        
        prefix = self.runfile[:-4]

        with open(self.pathfile) as f:
            lines = [line.strip() for line in f]

        run_index = next((i for i, line in enumerate(lines) if line.startswith('#run')), None)
        if run_index == None:
            raise ValueError('Error: missing run marker (#run) in run file')
        
        n_runs = len(lines) - run_index - 1

        hden = np.linspace(-9, 4, n_runs)

        output_lines = ['HDEN[cm^-3]  TEMPERATURE[K]  HEATING[erg_cm^3_s^-1]  COOLING[erg_cm^3_s^-1]']

        for j in range(n_runs):
            map_j = f"{self.path}{prefix}_run{j+1}.dat"
            nvals, Tvals, hvals, cvals = self.loadmaps(map_j, hden, j)
            for n, T, h, c in zip(nvals, Tvals, hvals, cvals):
                output_lines.append('{0:.7E}  {1:.7E}  {2:.7E}  {3:.7E}'.format(10**n, T, h, c))

        with open(self.outfile, 'w') as fw:
            fw.write('\n'.join(output_lines))


    def loadmaps(self, map, hden, n_run):
        """

        Load an individual heating & cooling map file

        """
        data = np.loadtxt(map, comments='#')
        T = data[:, 0]
        heating = data[:, 1]
        cooling = data[:, 2]

        hden_vals = np.full(len(T), hden[n_run])

        return hden_vals, T, heating, cooling