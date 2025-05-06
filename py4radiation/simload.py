#!/usr/bin/env python3

import vtk
import numpy as np

def simload(filename):
    """

    Load a VTK simulation file and obtain FIELDS and SHAPE (dimension)

    **Parameters**

    :file: string, path to simulation file

    :return: scalar/vector fields, dimensions

    """

    reader = vtk.vtkDataSetReader()
    reader.SetFileName(filename)
    reader.ReadAllScalarsOn()
    reader.ReadAllVectorsOn()
    reader.Update()

    data  = reader.GetOutput()
    dims  = data.GetDimensions()
    shape = tuple(d - 1 for d in dims)

    cell_data = data.GetCellData()
    var_names = ['rho', 'tr1', 'prs', 'vx1', 'vx2', 'vx3']
    fields    = [np.array(cell_data.GetArray(name)).reshape(shape, order='F') for name in var_names]

    return fields, shape
