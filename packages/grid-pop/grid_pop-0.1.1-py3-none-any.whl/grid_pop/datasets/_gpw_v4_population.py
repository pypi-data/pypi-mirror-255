
import requests
import numpy as np

from os import makedirs
from os.path import exists
from zipfile import ZipFile

from . import (
    get_data_home, 
    check_valid_input, 
    BASE_URL, 
    DATA_YEARS, 
    DATA_FORMATS, 
    DENSITY_RESOLUTIONS
)


class session_with_header_redirection(requests.Session):

    AUTH_HOST = 'urs.earthdata.nasa.gov'

    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

   # Overrides from the library to keep headers when redirected to or from
   # the NASA auth host.

    def rebuild_auth(self, prepared_request, response) -> None:

        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname and 
                redirect_parsed.hostname != self.AUTH_HOST and 
                original_parsed.hostname != self.AUTH_HOST):

                del headers['Authorization']

        return None


def _download_data(
        username: str, password: str, data_set: str, file_save_path: str, file_url_path: str
    ) -> None:
    '''Downloads the SEDAC zip file to the data directory.

    Parameters
    ----------
    username: str, Default=''

    password: str, Default=''

    data_set: str

    file_save_path: str

    file_url_path: str
    '''
    if (username=='') | (password==''):
        raise ValueError(
            'Data set needs to be downloaded, please enter username and password.'
        )

    print('Downloading data... ', end='')
    session = session_with_header_redirection(username, password)
    
    url = BASE_URL + '/'.join([data_set, file_url_path])

    try:
        # submit the request using the session
        response = session.get(url, stream=True)

        # raise an exception in case of http errors
        response.raise_for_status()

        with open(file_save_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024*1024):
                fd.write(chunk)

        print('Done.')

    except requests.exceptions.HTTPError as e:
        # handle any errors here
        print(e)


def _load_file_part(
        zip_archive: str, data_file: str
    ) -> np.ndarray:
    '''
    '''
    with zip_archive.open(data_file) as data_file:
        data = np.loadtxt(
            data_file, skiprows=6, dtype=np.float32
        )

    return data


def _load_zip(
        file_save_path: str, format: str, resolution: str
    ) -> np.ndarray:
    '''Extracts and returns the data file from the given zip file.

    Parameters
    ----------
    file_save_path: str
        The zip file that contains the data of interest.

    format: str
        The data format of the file of interest. Used for searching for the 
        correct file within the zip file.

    Returns
    -------
    data: ndarray
    '''
    zip_contents = np.load(file_save_path)

    if resolution != '30-sec':
        data_file = next(x for x in zip_contents.keys() if x[-3:] == format)

        with ZipFile(file_save_path) as zip_archive:
            data = _load_file_part(zip_archive, data_file)

    else:
        file_list = [x for x in zip_contents.keys() if x[-3:] == format]
        file_list.sort()

        with ZipFile(file_save_path) as zip_archive:
            data = np.append(
                        np.append(
                            np.append(
                                np.append(_load_file_part(zip_archive, file_list[0]), _load_file_part(zip_archive, file_list[4]), axis = 0), 
                                np.append(_load_file_part(zip_archive, file_list[1]), _load_file_part(zip_archive, file_list[5]), axis = 0), axis=1), 
                            np.append(_load_file_part(zip_archive, file_list[2]), _load_file_part(zip_archive, file_list[6]), axis = 0), axis=1), 
                        np.append(_load_file_part(zip_archive, file_list[3]), _load_file_part(zip_archive, file_list[7]), axis = 0), axis=1
                    )

    return data


def fetch_population_density(
        username: str = '', password: str = '', year: int = 2020, format: str = 'asc', 
        resolution: str = '2pt5-min', adjusted: bool = True
    ) -> np.ndarray:
    '''Return a numpy array containing the population density data.

    Parameters
    ----------
    username: str, Default=''

    password: str, Default=''

    year: int, Default=2020

    format: str, Default='asc'

    resolution: str, Default='2pt5-min'

    adjusted: bool, Default=True

    Returns
    -------
    data: ndarray
    '''
    check_valid_input(year, DATA_YEARS, 'fetch_population_density', 'year')
    check_valid_input(format, DATA_FORMATS, 'fetch_population_density', 'format')
    check_valid_input(resolution, DENSITY_RESOLUTIONS, 'fetch_population_density', 'resolution')

    data_home = get_data_home()
    if not exists(data_home):
        makedirs(data_home)
    
    data_set = 'gpw-v4-population-density-rev11'
    if adjusted:
        data_set = 'gpw-v4-population-density-adjusted-to-2015-unwpp-country-totals-rev11'
    
    file_url_path = data_set + f'_{year}_{resolution.replace('-', '_')}_{format}.zip'
    file_save_path = data_home + '/' + file_url_path

    if not exists(file_save_path):
        _download_data(username, password, data_set, file_save_path, file_url_path)
    
    data = _load_zip(file_save_path, format, resolution)

    data[data == -9999] = np.nan
    
    return data


def fetch_population_count(
        username: str = '', password: str = '', year: int = 2020, format: str = 'asc', 
        resolution: str = '2pt5-min', adjusted: bool = True
    ) -> np.ndarray:
    '''Return a numpy array containing the population count data.

    Parameters
    ----------
    username: str, Default=''

    password: str, Default=''

    year: int, Default=2020

    format: str, Default='asc'

    resolution: str, Default='2pt5-min'

    adjusted: bool, Default=True

    Returns
    -------
    data: ndarray

    Examples
    --------
    >>> 
    '''
    data_home = get_data_home()
    if not exists(data_home):
        makedirs(data_home)
    
    data_set = 'gpw-v4-population-count-rev11'
    if adjusted:
        data_set = 'gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals-rev11'
    
    file_url_path = data_set + f'_{year}_{resolution.replace('-', '_')}_{format}.zip'
    file_save_path = data_home + '/' + file_url_path

    if not exists(file_save_path):
        _download_data(username, password, data_set, file_save_path, file_url_path)
    
    data = _load_zip(file_save_path, format, resolution)

    data[data == -9999] = np.nan
    
    return data