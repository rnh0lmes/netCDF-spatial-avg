# Downscaled CMIP3 and CMIP5 Climate and Hydrology Projections Pre-processing
Conversion of targeted netcdf files into spreadsheet tables with the use of the arcpy library for python 2 (arcmap) and 3 (arcgis pro).

## Execution Environment
+ For Arcmap desktop 10 or above use python 2.7 which can be setup with anaconda for multiple environments or native 2.7.  
+ For ArcGID PRO use python 3.6 or above which can be native environment or via anaconda.  
+ Anaconda needs to be the 32 bit version if using python 2 as arcgis desktop is 32 bits.  

To setup anaconda environment with arcmap look at the instructions on:

https://sites.temple.edu/geodev/setting-up-a-python-development-environment-with-anaconda-and-arcpy/

Notes: 
+ Download Anaconda 32 bit if using arcmap.  
+ The environment created can be used on visual studio code using the python interpreter addon and linking it
  to the python.exe that is inside the anaconda environment.

To run the python scripts from anaconda:
1. Open de Anaconda prompt.
2. Activate the environment
    > activate arcpy10-7
5. run the script with:
    > python <script_name>.py

## Input Harvesting
Refer to the docs folder for instructions on downloading netcdf data.
TODO: Robyn explain which datasets you downloaded for your inputs.

## Run Instructions

1. Copy the Netcdf files from a single projection into an inputs folder.
2. Create an outputs folder.
3. Copy the sub basin shapefile into the shapes folder, make sure to include all files linked to the shapefile.
4. Modify the path strings that are hardcoded in the python scripts... below all #paths comments. There is one on the main function and one on the cdf processing function.
5. Modify the level variable to the dimension required.

## Change Log

+ Separation of summary table field creation into its own function.
+ Each netcdf file is processed in different cores and independent from each other.
+ Each process created its own local summary table.
+ OutputTable is now managed directly in memory with no storage i/o operations.
+ The main process waits for the other to finish.
+ The main process looks up the tables on the output folder, creates the final summary table and appends the process tables.
+ Final runtime displayed add the end in seconds.

## References

+ Downscaled CIMP3 and CMPIP5 Climate and Hydrology Projections, https://gdo-dcp.ucllnl.org/downscaled_cmip_projections/#Projections:%20Subset%20Request
+ Parallel processing on python, https://www.pythonpool.com/python-map-function/

## Questions:

**Set environment setting to match pixel size of the raster?**
Setting the environment setting to match the pixel size of the raster being analyzed, makes the tool perform as expected, and as it should be as default, obviously, and therefore matches the output results i get when using zonal histogram on the same exact layers.

**What coordinate system is associated with the downscaled projections?**
The downscaled projections are on the NLDAS 1/8th degree grid (datum WGS84).

**What coordinate system does the raster use?**
WGS_1984_UTM_Zone_13N
Geographic Coordinate System:	GCS_WGS_1984
Datum: 	D_WGS_1984

## Attributions

Base Code:    
 + Gerrit VanderWaal (gerrit.vwaal@gmail.com)   
Project Adaptations:   
 + Robyn Holmes
 + Luis Garnica
 + Nolan Townsend

## License

GNU General Public License




