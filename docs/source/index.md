```{image} _static/bmi_nwis_logo.png
:align: center
:alt: bmi_nwis
:scale: 30%
:target: https://nwis.readthedocs.io/
```

[bmi_nwis][bmi_nwis-github] package is an implementation of the
[Basic Model Interface (BMI)][bmi-docs] for the [USGS NWIS dataset][nwis-link].
This package uses the [dataretrieval][dataretrieval] package
to download the NWIS dataset and wraps the dataset with BMI for data control and query.

This package is not implemented for people to use but is the key element to convert the NWIS dataset
into a data component ([pymt_nwis][pymt_nwis]) for
the [PyMT][pymt-docs] modeling framework developed by
[Community Surface Dynamics Modeling System (CSDMS)][csdms].

Please note that the current bmi_nwis implementation only supports to download time series data
for instantaneous values and daily mean values ('iv' or 'dv' service option in the dataretrieval package).

# Getting Started

## Installation

**Stable Release**

The nwis package and its dependencies can be installed with pip.

````{tab} pip
```console
pip install bmi_nwis
```
````

````{tab} conda
```console
conda install -c conda-forge bmi_nwis
```
````

**From Source**

After downloading the [source code][nwis-github], run the following command from top-level
folder (the one that contains setup.py) to install nwis.

```console
pip install -e .
```

## Download NWIS Data


**Example 1**: Use the dataretrieval package to download data

```python
import dataretrieval.nwis as nwis

# get data from NWIS
dataset = nwis.get_record(
    sites="03339000", service="iv", start="2022-01-01", end="2022-01-03"
)

# plot discharge data
ax = dataset.plot(
    y=["00060", "00065"],
    subplots=True,
    figsize=(10, 8),
    xlabel="Time",
    title="Time Series Data at USGS Gage 03339000",
)
ax[0].set_ylabel("Stream flow (ft3/s)")
ax[1].set_ylabel("Gage height (ft)")
```

```{image} _static/plot.png
```

**Example 2**: use BmiNwis class to download data (Demonstration of how to use BMI).

```python
import matplotlib.pyplot as plt
import numpy as np
import cftime

from bmi_nwis import BmiNwis


# initiate a data component
data_comp = BmiNwis()
data_comp.initialize("config_file.yaml")

# get variable info
for var_name in data_comp.get_output_var_names():
    var_unit = data_comp.get_var_units(var_name)
    var_location = data_comp.get_var_location(var_name)
    var_type = data_comp.get_var_type(var_name)
    var_grid = data_comp.get_var_grid(var_name)
    var_itemsize = data_comp.get_var_itemsize(var_name)
    var_nbytes = data_comp.get_var_nbytes(var_name)

    print(f"{var_name=}")
    print(f"{var_unit=}")
    print(f"{var_location=}")
    print(f"{var_type=}")
    print(f"{var_grid=}")
    print(f"{var_itemsize=}")
    print(f"{var_nbytes=}")

# get time info
start_time = data_comp.get_start_time()
end_time = data_comp.get_end_time()
time_step = data_comp.get_time_step()
time_unit = data_comp.get_time_units()
time_steps = int((end_time - start_time) / time_step) + 1

print(f"{start_time=}")
print(f"{end_time=}")
print(f"{time_step=}")
print(f"{time_unit=}")
print(f"{time_steps=}")

# initiate numpy arrays to store discharge data
discharge_value = np.empty(1)
discharge_array = np.empty(time_steps)
cftime_array = np.empty(time_steps)

for i in range(0, time_steps):
    data_comp.get_value("discharge", discharge_value)
    discharge_array[i] = discharge_value[0]
    cftime_array[i] = data_comp.get_current_time()
    data_comp.update()

time_array = cftime.num2date(
    cftime_array,
    time_unit,
    only_use_cftime_datetimes=False,
    only_use_python_datetimes=True,
)

# plot discharge data
plt.figure(figsize=(9, 5))
plt.plot(time_array, discharge_array)
plt.ylabel("discharge (cubic feet per second)")
plt.title("Discharge Observation at USGS Gage 03339000")
```

## Parameter settings

To initiate a data component, a configuration file (e.g., [config_file.yaml][config] )
can be used to specify the parameters for downloading the data. The major parameters are
listed below:

- **sites**: The site number for the USGS gage, which is a unique 8- to 15-digit identification number for each site.
  'sites' can be a string value for one site or a list of string values for multiple sites.
- **start**: The start date of the time series data (example string format as "YYYY-MM-DD").
- **end**: The end date of the time series data (example string format as "YYYY-MM-DD").
- **service**: The service option for data download.
  Options include 'dv'- daily mean value and 'iv'- instantaneous value.
- **parameterCd**: The parameter code defined by USGS for the variables (e.g., 00060 represents Stream flow).
  'parameterCd' can be a string value for one variable or a list of string values for multiple variables.
- **output**: The file path of the NetCDF file to store the data.


<!-- links -->
[bmi-docs]: https://bmi.readthedocs.io
[bmi_nwis-github]: https://github.com/gantian127/bmi_nwis
[csdms]: https://csdms.colorado.edu
[dataretrieval]: https://github.com/USGS-python/dataretrieval
[nwis-link]: https://waterdata.usgs.gov/nwis?
[pymt_nwis]: https://pymt-nwis.readthedocs.io
[pymt-docs]: https://pymt.readthedocs.io
[config]: https://github.com/gantian127/bmi_nwis/blob/master/notebooks/config_file.yaml
