# py4radiation (in dev)

## Quick notes

py4radiation is a python package to calculate ion fractions and heating/cooling rates from the SED of a source located at a certain distance from the object of interest (in our case gas clouds in the ISM/CGM).

These quick instructions refer only to the scripts in *Radiation*.

1. `prepare_sed.py`

For now it works for SEDs in Starburst99 format with the header previously removed. We use the normalisation factor at 1 Ryd.

You will obtain a .OUT file with the SED in the required format for CLOUDY/CIAOLoop.

2. `parfiles.py`

You need CLOUDY C13 to run this script. It generates the parameter files for CIAOLoop for the ion fractions and radiative heating/cooling routines.

3. Run CIAOLoop

Take into account that depending on the resolution, it may take quite a few computational resources.

4. Wrap the output files using `ion_tables.py` and `hc_rates.py`

If your run with CIAOLoop went well, you will see a single .RUN file in the output folder. You can get a nice h5 table with `ion_tables.py` (which can be directly used in Trident), or a file containing heating/cooling rates with the format

HDEN[cm^-3]  TEMPERATURE[K]  HEATING[erg cm^3 s^-1]  COOLING[erg cm^3 s^-1]
