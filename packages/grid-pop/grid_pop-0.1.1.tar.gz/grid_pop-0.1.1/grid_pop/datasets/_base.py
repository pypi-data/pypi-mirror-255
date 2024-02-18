import shutil
from os import environ, makedirs
from os.path import expanduser, join


BASE_URL = "https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/"

DENSITY_RESOLUTIONS = ['30-sec', '2pt5-min', '15-min', '30-min', '1-deg']

DATA_FORMATS = ['asc', 'tif']

DATA_YEARS = [2000, 2005, 2010, 2015, 2020]

DATA_SETS = [
    'gpw-v4-population-count-rev11',
    'gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals-rev11',
    'gpw-v4-population-density-rev11'
    'gpw-v4-population-density-adjusted-to-2015-unwpp-country-totals-rev11',
    ]


def get_data_home(data_home=None) -> str:
    '''Return the path of the data directory.

    This folder is used by the dataset loaders to avoid downloading the
    data several times.

    By default the data directory is set to a folder named 'sedac_data' in the
    user home folder.

    Alternatively, it can be set by the 'SEDAC_DATA' environment
    variable or programmatically by giving an explicit folder path. The '~'
    symbol is expanded to the user home folder.

    If the folder does not already exist, it is automatically created.

    Parameters
    ----------
    data_home : str or path-like, default=None
        The path to SEDAC data directory. If `None`, the default path
        is `~/sedac_data`.

    Returns
    -------
    data_home: str
        The path to SEDAC data directory.
    '''
    if data_home is None:
        data_home = environ.get("SEDAC_DATA", join("~", "sedac_data"))
    data_home = expanduser(data_home)
    makedirs(data_home, exist_ok=True)
    return data_home


def clear_data_home(data_home=None) -> None:
    """Delete all the content of the data home cache.

    Parameters
    ----------
    data_home : str or path-like, default=None
        The path to SEDAC data directory. If `None`, the default path
        is `~/sedac_data`.

    Examples
    --------
    >>> from grid_pop.datasets import clear_data_home
    >>> clear_data_home()  # doctest: +SKIP
    """
    data_home = get_data_home(data_home)
    shutil.rmtree(data_home)


def check_valid_input(
        value, valid_values: set|list, func_name: str = 'func', param_name: str = 'param'
    ) -> None:
    '''Checks if a given value is a member of the expected set of responses, raises a
    ValueError if not a correct value.

    Parameters
    ----------
    value

    valid_values: set|list
    
    func_name: str, Default='func'
    
    param_name: str, Default='param'

    Returns
    -------
    value

    '''
    if isinstance(valid_values, list):
        valid_values = set(valid_values)

    if value not in valid_values:
        raise ValueError(f"{func_name}: {param_name} must be one of {valid_values}.")
    
    return value