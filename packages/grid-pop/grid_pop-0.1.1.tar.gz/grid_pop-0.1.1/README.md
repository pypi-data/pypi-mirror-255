# Grid Pop: Accessing SEDAC's Gridded Population of the World Data

Downloads various data sets from the Socioeconomic Data and Applications Center (SEDAC)

## GPWv4 Introduction

From their [introduction](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4):

> The Gridded Population of the World (GPW) collection, now in its fourth version (GPWv4), models the distribution of human population (counts and densities) on a continuous global raster surface.
> Since the release of the first version of this global population surface in 1995, the essential inputs to GPW have been population census tables and corresponding geographic boundaries.
> The purpose of GPW is to provide a spatially disaggregated population layer that is compatible with data sets from social, economic, and Earth science disciplines, and remote sensing.
> It provides globally consistent and spatially explicit data for use in research, policy-making, and communications.

[General Methodology](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count-rev11):
>The Gridded Population of the World, Version 4 (GPWv4): Population Count, Revision 11 consists of estimates of human population (number of persons per pixel), consistent with national censuses and population registers ... 
> A proportional allocation gridding algorithm, utilizing approximately 13.5 million national and sub-national administrative units, was used to assign population counts to 30 arc-second grid cells. 
> The data files were produced as global rasters at 30 arc-second (~1 km at the equator) resolution. 
> To enable faster global processing, and in support of research communities, the 30 arc-second data were aggregated to 2.5 arc-minute, 15 arc-minute, 30 arc-minute and 1 degree resolutions.

Data sets currently included in this package:
- GPWv4 Population Density
- GPWv4 Population Count

These data sets are avaialble for the years 2000, 2005, 2010, 2015, & 2020. They are availiable unadjusted (i.e., 'consistent with national censuses and population registers') or adjusted 'to match the 2015 Revision of the United Nation's World Population Prospects (UN WPP) country totals'.

Available Resolutions:
- 30 Second (approx. 1km)
- 2.5 Minute (approx. 5km)
- 15 Minute (approx. 30 km)
- 30 Minute (approx. 55 km)
- 1 Degree (approx. 110 km)
\
    *Note:* The 30 Second file is very large, ~180 MB compressed and ~6 GB when extracted.  

## Getting Started
1. Register for an Earthdata Login account at https://urs.earthdata.nasa.gov/users/new
2. Install using 
\
    ```pip install grid-pop```
3. The first time that `Points` is initialized, a folder will be created at `~/sedac_data` to store the downloaded zip files. A username and password must be used each time you download a new data set - if the data set is already available in the `sedac_data` folder, you do not need to include your credentials.

## Example Usage
**First usage**
```
>>> from grid_pop import Points
>>> data = Points(data_type='density', username='USERNAME', password='PASSWORD')
Downloading data... Done.
>>> poi_latlon = [(40.7481, -73.9858), (31.2231, 121.4760), (44.6624, -103.8513), (0.0, 0.0)]
>>> data.add_points(poi_latlon)
{'points': [(40.7481, -73.9858), (31.2231, 121.476), (44.6624, -103.8513), (0.0, 0.0)], 'population_density': [23610.43, 40475.68, 123.3144, nan]}
```
**Subsequent usage of same data set**
```
>>> data2 = Points(data_type='density')
>>> data2.add_points(poi_latlon)
{'points': [(40.7481, -73.9858), (31.2231, 121.476), (44.6624, -103.8513), (0.0, 0.0)], 'population_density': [23610.43, 40475.68, 123.3144, nan]}
```
**Appending additional points**
```
>>> data.add_points((34.0431, -118.2436))
{'points': [(40.7481, -73.9858), (31.2231, 121.476), (44.6624, -103.8513), (0.0, 0.0), (34.0431, -118.2436)], 'population_density': [23610.43, 40475.68, 123.3144, nan, 10941.37]}
>>> data.add_points((34.0431, -118.2436), clear_points=True)
{'points': [(34.0431, -118.2436)], 'population_density': [10941.37]}
```
**Accessing full data array:**
```
>>> data.density_array
array([[nan, nan, nan, ..., nan, nan, nan],
       [nan, nan, nan, ..., nan, nan, nan],
       [nan, nan, nan, ..., nan, nan, nan],
       ...,
       [nan, nan, nan, ..., nan, nan, nan],
       [nan, nan, nan, ..., nan, nan, nan],
       [nan, nan, nan, ..., nan, nan, nan]])
```
*Note:* In the raw files, NO DATA values (e.g., oceans) are coded as `-9999`. After loading the file, they are re-coded as as numpy `np.nan`'s.