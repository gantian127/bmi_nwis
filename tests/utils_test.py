import pytest
import os

from bmi_nwis import NwisData


# test user input for get_data() method

# test sites
def test_sites():
    with pytest.raises(ValueError):
        NwisData().get_data(sites='invalid_site', start='2022-01-01', end='2022-01-03', service='iv')

    with pytest.raises(ValueError):
        NwisData().get_data(sites='033390001', start='2022-01-01', end='2022-01-03', service='iv')


# test service
def test_service():
    with pytest.raises(ValueError):
        NwisData().get_data(sites='03339000', start='2022-01-01', end='2022-01-03', service='invalid_type')


# test output
def test_output_invalid_dir(tmpdir):
    with pytest.raises(ValueError):
        NwisData().get_data(sites='03339000', start='2022-01-01', end='2022-01-03', service='iv',
                        output=os.path.join(tmpdir, 'error'))


@pytest.mark.filterwarnings("ignore:numpy.ndarray size changed")
def test_output_valid_dir(tmpdir):
    NwisData().get_data(sites='03339000', start='2022-01-01', end='2022-01-03', service='iv',
                    output=os.path.join(tmpdir, 'test.nc'))

    assert len(os.listdir(tmpdir)) == 1





