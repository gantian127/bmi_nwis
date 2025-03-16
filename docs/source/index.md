```{image} _static/bmi_nwis_logo.png
:align: center
:alt: bmi_nwis
:scale: 13%
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

The bmi_nwis package and its dependencies can be installed with pip.

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

After downloading the [source code][bmi_nwis-github], run the following command from top-level
folder to install bmi_nwis.

```console
pip install -e .
```

## Citation
Please include the following references when citing this software package:

Gan, T., Tucker, G.E., Hutton, E.W.H., Piper, M.D., Overeem, I., Kettner, A.J.,
Campforts, B., Moriarty, J.M., Undzis, B., Pierce, E., McCready, L., 2024:
CSDMS Data Components: data–model integration tools for Earth surface processes
modeling. Geosci. Model Dev., 17, 2165–2185. https://doi.org/10.5194/gmd-17-2165-2024

Gan, T. (2023). CSDMS NWIS Data Component. Zenodo. https://doi.org/10.5281/zenodo.10368748

## Download NWIS Data


**Example 1**: Use the dataretrieval package to download data

```python
import dataretrieval.nwis as nwis

# get data from NWIS
dataset = nwis.get_record(
    sites="03339000", service="iv", start="2022-01-01", end="2022-01-03"
)

# plot data
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
import numpy as np
import cftime
import pandas as pd

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
    print(f"{var_nbytes=}\n")

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

# get variable grid info
grid_type = data_comp.get_grid_type(var_grid)
grid_rank = data_comp.get_grid_rank(var_grid)
grid_node_count = data_comp.get_grid_node_count(var_grid)

site_lon = np.empty(grid_node_count)
data_comp.get_grid_x(var_grid, site_lon)

site_lat = np.empty(grid_node_count)
data_comp.get_grid_y(var_grid, site_lat)

print(f"{grid_type=}")
print(f"{grid_rank=}")
print(f"{grid_node_count=}")
print(f"{site_lon[0]=}")
print(f"{site_lat[0]=}")

# initiate dataframe to store data
dataset = pd.DataFrame(columns=["00060", "00065", "time"])

for i in range(0, time_steps):
    # get stream flow data
    stream_flow = np.empty(1)
    data_comp.get_value("Stream flow", stream_flow)

    # get gage height data
    gage_height = np.empty(1)
    data_comp.get_value("Height", gage_height)

    # get time data
    cftime_value = data_comp.get_current_time()
    time = cftime.num2pydate(cftime_value, time_unit)

    # add new row to dataframe
    dataset.loc[len(dataset)] = [stream_flow[0], gage_height[0], time]

    # update to next time step
    data_comp.update()

# convert time to local time
dataset = dataset.set_index("time").tz_localize(tz="UTC").tz_convert(tz="US/Central")

# plot data
ax = dataset.plot(
    y=["00060", "00065"],
    subplots=True,
    figsize=(10, 8),
    xlabel="Time",
    title="Time Series Data at USGS Gage 03339000",
)
ax[0].set_ylabel("Stream flow (ft3/s)")
ax[1].set_ylabel("Gage height (ft)")

# finalize the data component
data_comp.finalize()
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
