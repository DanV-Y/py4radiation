#!/usr/bin/env python3

import h5py
import numpy as np

class IonTables():
    """

    Generate ion fractions from CIAOLoop output files
    Modified from ion_balance_tables by Britton Smith
    github.com/brittonsmith/cloudy_cooling_tools

    
    :runfile: string

        Path to file ending with .run inside ./ib folder

    :outfile: string

        Name of hdf5 ion fractions file

    :elements: string

        Elements for ion fractions

    """

    def __init__(self, path, runfile, outfile, elements):
        self.path = path
        self.pathfile = path + runfile
        self.runfile = runfile
        self.outfile = outfile
        self.elements = elements


    def _getdata(self, element):
        """
        
        Cloudy/CIAOLoop ion fraction run files into hdf5

        """

        print(f"Converting {element} from {self.runfile} to {self.outfile}")

        if not self.runfile.endswith('.run'):
            raise ValueError('Error: run file needs to end in .run')
        
        prefix = self.runfile[:-4]

        with open(self.pathfile, 'r') as f:
            lines = [line.strip() for line in f]

        parameter_values = []
        parameter_names  = []

        get_parameter_values = False
        n_runs = 0

        for i, line in enumerate(lines):
            if get_parameter_values:
                if line == '#':
                    get_parameter_values = False
                else:
                    parameter, values = line.split(': ', 1)
                    parameter_values.append([float(value) for value in values.split()])
                    parameter_names.append(parameter[2:])
            elif line.startswith('# Loop commands and values'):
                get_parameter_values = True
            elif line.startswith('#run'):
                n_runs = len(lines) - i - 1
                break

        grid_shape = [len(vals) for vals in parameter_values]
        
        if n_runs != np.prod(grid_shape):
            raise ValueError(f'Error: total runs not equal to product of parameters')
        
        grid_data = []
        for j in range(n_runs):
            map_j = f"{self.path}{prefix}_run{j+1}_{element}.dat"
            idxs = np.unravel_index(j, grid_shape)
            self.loadmaps(map_j, grid_shape, idxs, grid_data)

        temperature = grid_data.pop(0)
        ion_data    = grid_data.pop(0)

        ion_data = np.rollaxis(ion_data, -1)

        with h5py.File(self.outfile, 'a') as output:
            ds = output.create_dataset(element, data=ion_data, dtype=np.float64)
            ds.attrs['Temperature'] = np.array(temperature, dtype=np.float64)

            for idx, values in enumerate(parameter_values, start=1):
                ds.attrs[f'Parameter{idx}'] = np.array(values, dtype=np.float64)

    def loadmaps(self, map, grid_shape, idx, grid_data):
        """

        Read individual Cloudy map and fill data arrays

        """

        try:
            data = np.loadtxt(map, comments='#')
        except Exception as e:
            raise RuntimeError(f'Error loading file {map}: {e}')
        
        T = data[:, 0]
        ion_fraction = data[:, 1:]

        if not grid_data:
            shape = list(grid_shape) + list(ion_fraction.shape)
            grid_data.append(T)
            grid_data.append(np.zeros(shape=shape))

        grid_data[1][tuple(idx)] = ion_fraction

    def get_ion_tables(self):
        """
        """

        for element in self.elements:
            self._getdata(element)