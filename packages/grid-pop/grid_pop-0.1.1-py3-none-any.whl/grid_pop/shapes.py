import numpy as np

from .datasets import (
    fetch_population_density, 
    fetch_population_count, 
    check_valid_input, 
    DENSITY_RESOLUTIONS, 
    DATA_FORMATS, 
    DATA_YEARS
)


class Points:
    '''

    Attributes
    ----------
    username: str, default=''
        Earthdata Login username, not needed if data has already been downloaded

    password: str, default=''
        Earthdata Login password, not needed if data has already been downloaded

    data_type: {'density', 'count', 'both'}
        Data set(s) to download and/or 

    resolution: {'2pt5-min', '30-sec', '15-min', '30-min', '1-deg'}
        Data set resolution, either native 30 arc-second, 2.5 arc-minute, 15 arc-minute, 
        30 arc-minute, or 1 degree.

    year: {2020, 2000, 2005, 2010, 2015}
        Estimate year
    
    format: {'asc', 'tif'}
        File format, either ASCII ('asc') or GeoTiff ('tif')

    adjusted: bool, default=True
        If True, uses estimates adjusted to match United Nations country totals

    Methods
    -------
    add_points(ll_points, clear_points=False) 


    '''
    def __init__(
            self, data_type: str = 'density', resolution: str = '2pt5-min', 
            year: int = 2020, format: str = 'asc', adjusted: bool = True,
            username: str = '', password: str = ''
        ):
        self.username = username
        self.password = password
        self.points = []
        self.pop_density = []
        self.pop_count = []

        self.resolution = check_valid_input(resolution, DENSITY_RESOLUTIONS)
        self.year = check_valid_input(year, DATA_YEARS)
        self.format = check_valid_input(format, DATA_FORMATS)
        self.adjusted = check_valid_input(adjusted, [True, False])

        self.data_type = data_type
        self.density_array = np.ndarray((0, 0))
        self.count_array = np.ndarray((0, 0))
        self._fetch_population_data()


    @staticmethod
    def _valid_lat_lon(point: tuple) -> None:
        '''Checks if a give (lat, lon) tuple is a valid point.

        Parameters
        ----------
        point
            Lat-lon tuple.

        Raises
        ------
        ValueError
            If the latitude & longitude values are not within their appropriate 
            ranges, or if there are more than 2 values in the tuple.
        '''
        lat = point[0]
        lon = point[1]

        if (abs(lat) > 90) or (abs(lon) > 180) or (len(point) != 2):
            raise ValueError(
                f'Invalid lat/lon point: \'{point}\' is not a correct coordinate.'
            )
        
    @staticmethod
    def _return_array_value(
            gpw_array: np.ndarray, ll_point: tuple
        ) -> float:
        '''
        Determines the cell in which a lat-lon point is located, and returns 
        the value of that cell from the givin array.

        Parameters
        ----------
        gpw_array
            The data array from which lat-lon values are to be returned.

        ll_point
            The lat-lon point of interest

        Returns
        -------
            The numerical value from the gpw_array.


        '''
        lat_cells, lon_cells = gpw_array.shape
        lat = ll_point[0]
        lon = ll_point[1]
        
        lat_cell = int((90 - lat) / 180 * (lat_cells - 1))
        lon_cell = int((180 + lon) / 360 * (lon_cells - 1))

        return gpw_array[lat_cell, lon_cell]
    

    def _fetch_population_data(self) -> None:
        '''
        Loads the appropriate data arrays given the \'data_type\' selected during initialization.

        Parameters
        ----------
            None


        Returns
        -------
            None

        '''
        if (self.data_type == 'density') | (self.data_type == 'both'):
            self.density_array = fetch_population_density(
                self.username, self.password, self.year, self.format, self.resolution, self.adjusted
            )
        
        if (self.data_type == 'count') | (self.data_type == 'both'):
            self.count_array = fetch_population_count(
                self.username, self.password, self.year, self.format, self.resolution, self.adjusted
            )


    def add_points(
            self, ll_points: list|tuple, clear_points: bool = False
        ) -> dict:
        '''
        Adds the given point or set of points to the \'points\' list, and 


        Parameters
        ----------
        ll_points: list|tuple
            A single lat-lon point, or a list of lat-lon points.

        clear_points: bool, default=False
            Removes the current set of stored lat-lon points before
            appending the new values from \'ll_points\'.

        Returns
        -------
        result: dict
            An updated dictionary with the current list of points, 
            population density values (if applicable), and 
            population count values (if applicable).


        '''
        if clear_points:
            self.points = []
            self.pop_density = []
            self.pop_count = []

        num_points_init = len(self.points)
        
        if isinstance(ll_points, tuple):
            Points._valid_lat_lon(ll_points)
            self.points.append(ll_points)

        if isinstance(ll_points, list):
            for point in ll_points:
                Points._valid_lat_lon(point)
            self.points.extend(ll_points)

        num_points_fin = len(self.points)

        for i in range(num_points_init, num_points_fin):
            if (self.data_type == 'density') | (self.data_type == 'both'):
                self.pop_density.append(Points._return_array_value(self.density_array, self.points[i]))
            
            if (self.data_type == 'count') | (self.data_type == 'both'):
                self.pop_count.append(Points._return_array_value(self.count_array, self.points[i]))

        result = {'points': self.points}

        if (self.data_type == 'density') | (self.data_type == 'both'):
            result['population_density'] = self.pop_density
            
        if (self.data_type == 'count') | (self.data_type == 'both'):
            result['population_count'] = self.pop_count            

        return result
