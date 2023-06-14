.. image:: _static/bmi_nwis_logo.png
    :align: center
    :scale: 10%
    :alt: bmi_nwis
    :target: https://bmi_nwis.readthedocs.io/


`bmi_nwis <https://github.com/gantian127/bmi_nwis>`_ package is an implementation of the Basic Model Interface
(`BMI <https://bmi-spec.readthedocs.io/en/latest/>`_) for the `USGS NWIS dataset <https://waterdata.usgs.gov/nwis>`_.
This package uses the `dataretrieval <https://github.com/USGS-python/dataretrieval>`_ package
to download the NWIS dataset and wraps the dataset with BMI for data control and query.

This package is not implemented for people to use but is the key element to convert the NWIS dataset
into a data component (`pymt_nwis <https://github.com/gantian127/pymt_nwis>`_) for
the `PyMT <https://pymt.readthedocs.io/en/latest/?badge=latest>`_ modeling framework developed by
Community Surface Dynamics Modeling System (`CSDMS <https://csdms.colorado.edu/wiki/Main_Page>`_).

Please note that the current bmi_nwis implementation only supports to download time series data
for instantaneous values and daily mean values ('iv' or 'dv' service option in the dataretrieval package).
If you have any suggestion to improve the current function, please create a github issue
`here <https://github.com/gantian127/bmi_nwis/issues>`_.


Installation
++++++++++++

**Stable Release**

The bmi_nwis package and its dependencies can be installed with pip.

.. code-block:: console

    $ pip install bmi_nwis

or with conda.

.. code-block:: console

    $ conda install -c conda-forge bmi_nwis

**From Source**

After downloading the `source code <https://github.com/gantian127/bmi_nwis>`_, run the following command from top-level
folder (the one that contains setup.py) to install bmi_nwis.

.. code-block:: console

    $ pip install -e .



Quick Start
+++++++++++++++++++++
Below shows how to use two methods to download the NWIS datasets.

You can learn more details from the
`tutorial notebook <https://github.com/gantian127/bmi_nwis/blob/master/notebooks/bmi_nwis.ipynb>`_
To run this notebook, please go to the `CSDMS EKT Lab <https://csdms.colorado.edu/wiki/Lab-0034>`_
and follow the instruction in the "Lab notes" section.

**Example 1**: Use the dataretrieval package to download data

.. code-block:: python

    import dataretrieval.nwis as nwis

    # get data from NWIS
    dataset = nwis.get_record(sites='03339000', service='iv', start='2022-01-01', end='2022-01-03')

    # plot data
    ax = dataset.plot(y=['00060','00065'], subplots=True, figsize=(10,8),
                      xlabel='Time', title = 'Time Series Data at USGS Gage 03339000')
    ax[0].set_ylabel('Stream flow (ft3/s)')
    ax[1].set_ylabel('Gage height (ft)')

|plot|

**Example 2**: Use BmiNwis class to download data (Demonstration of how to use BMI)

.. code-block:: python

    import numpy as np
    import cftime
    import pandas as pd

    from bmi_nwis import BmiNwis


    # initiate a data component
    data_comp = BmiNwis()
    data_comp.initialize('config_file.yaml')

    # get variable info
    for var_name in  data_comp.get_output_var_names():
        var_unit = data_comp.get_var_units(var_name)
        var_location = data_comp.get_var_location(var_name)
        var_type = data_comp.get_var_type(var_name)
        var_grid = data_comp.get_var_grid(var_name)
        var_itemsize = data_comp.get_var_itemsize(var_name)
        var_nbytes = data_comp.get_var_nbytes(var_name)
        print('variable_name: {} \nvar_unit: {} \nvar_location: {} \nvar_type: {} \nvar_grid: {} \nvar_itemsize: {}'
                '\nvar_nbytes: {} \n'. format(var_name, var_unit, var_location, var_type, var_grid, var_itemsize, var_nbytes))

    # get time info
    start_time = data_comp.get_start_time()
    end_time = data_comp.get_end_time()
    time_step = data_comp.get_time_step()
    time_unit = data_comp.get_time_units()
    time_steps = int((end_time - start_time)/time_step) + 1
    print('start_time:{} \nend_time:{} \ntime_step:{} \ntime_unit:{} \ntime_steps:{} \n'.format(start_time, end_time, time_step, time_unit, time_steps))

    # get variable grid info
    grid_type = data_comp.get_grid_type(var_grid)
    grid_rank = data_comp.get_grid_rank(var_grid)
    grid_node_count = data_comp.get_grid_node_count(var_grid)

    site_lon = np.empty(grid_node_count)
    data_comp.get_grid_x(var_grid, site_lon)

    site_lat = np.empty(grid_node_count)
    data_comp.get_grid_y(var_grid, site_lat)

    print('grid_type: {} \ngrid_rank: {} \ngrid_node_count: {} \nsite_lon: {} \nsite_lat: {} \n'.format(
        grid_type, grid_rank, grid_node_count, site_lon[0], site_lat[0]))

    # initiate dataframe to store data
    dataset = pd.DataFrame(columns = ['00060','00065','time'])

    for i in range(0, time_steps):
        # get stream flow data
        stream_flow = np.empty(1)
        data_comp.get_value('Stream flow', stream_flow)

        # get gage height data
        gage_height = np.empty(1)
        data_comp.get_value('Height', gage_height)

        # get time data
        cftime_value= data_comp.get_current_time()
        time = cftime.num2pydate(cftime_value, time_unit)

        # add new row to dataframe
        dataset.loc[len(dataset)]=[stream_flow[0], gage_height[0], time]

        # update to next time step
        data_comp.update()

    # convert time to local time
    dataset = dataset.set_index('time').tz_localize(tz='UTC').tz_convert(tz='US/Central')

    # plot data
    ax = dataset.plot(y=['00060','00065'], subplots=True, figsize=(10,8),
                      xlabel='Time', title = 'Time Series Data at USGS Gage 03339000')
    ax[0].set_ylabel('Stream flow (ft3/s)')
    ax[1].set_ylabel('Gage height (ft)')

    # finalize the data component
    data_comp.finalize()

Parameter settings
+++++++++++++++++++
To initiate a data component, a configuration file
(e.g., `config_file.yaml <https://github.com/gantian127/bmi_nwis/blob/master/notebooks/config_file.yaml>`_)
can be used to specify the parameters for downloading the data. The major parameters are listed below:

* **sites**: The site number for the USGS gage, which is a unique 8- to 15-digit identification number for each site.
  'sites' can be a string value for one site or a list of string values for multiple sites.

* **start**: The start date of the time series data (example string format as "YYYY-MM-DD").

* **end**: The end date of the time series data (example string format as "YYYY-MM-DD").

* **service**: The service option for data download.
  Options include 'dv'- daily mean value and 'iv'- instantaneous value.

* **parameterCd**: The parameter code defined by USGS for the variables (e.g., 00060 represents Stream flow).
  'parameterCd' can be a string value for one variable or a list of string values for multiple variables.

* **output**: The file path of the NetCDF file to store the data.



.. links:

.. |binder| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/gantian127/bmi_nwis/master?filepath=notebooks%2Fbmi_nwis.ipynb

.. |plot| image:: _static/plot.png

