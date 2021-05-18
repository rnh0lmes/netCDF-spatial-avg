# Purpose: Given a set of netCDF files in a directory, converts the netCDF files to rasters and
# uses the Zonal Statistics with a supplied zone layer. The created tables are then merged together
# into a single dBASE table, then converted to an .xls spreadsheet in the chose output directory.
#
# Requires: 
# + Spatial Analyst extension for ArcMap, pre-created input and output directories, and a supplied zone layer.
# + Python 2
#
# MultiProcess: Each cdf file is processed in parallel under separate cores.
#
# Original Author: Gerrit VanderWaal (763-647-0338, gerrit.vwaal@gmail.com)
# Adapted for monthly climate data: Robyn Holmes
# Adpated for multiprocess: Luis Garnica (lagarnicachavira@utep.edu)

import os
import datetime
import arcpy
import re
import multiprocessing
import time
import gc
class LicenseError(Exception):
    pass

def process_cdf(cfd_file):
    print ("Sub-Processing CDF: " + cfd_file)

    try:
        # Checks that the Spatial Analyst extension is installed, calls the LicenseError exception if it is not.
        # print "Checking Spatial Analyst license..."
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            # print "License retrieved.\n"
        else:
            raise LicenseError

        # Enables data overwriting.
        arcpy.env.overwriteOutput = True

        # paths
        inputSpace = "C:\\Users\\lagarnicachavira\\Documents\\Repos\\netcdf-processor\\inputs"
        outputSpace = "C:\\Users\\lagarnicachavira\\Documents\\Repos\\netcdf-processor\\outputs"
        # zones = "C:\\Users\\lagarnicachavira\\Documents\\Repos\\netcdf-processor\\shapes\\Sub_Basins.shp"
        zones = "C:\\Users\\lagarnicachavira\\Documents\\Repos\\netcdf-processor\\shapes\\Sub_Basins"

        # level dimension??? no effect??
        level = 0

        # arcpy environment workspace
        arcpy.env.workspace = inputSpace

        # DAILY new vars
        dimension = "time"
        valueSelectionMethod = "BY_VALUE"
        theFormatTime = '%m/%d/%Y %H:%M:%S %p'
        theFormat = '%m/%d/%Y'

        # declare local result table
        result_table = None

        if cfd_file.startswith("Extraction_"):
            ###DAILY new STEPS
            # inputs is hardcoded here, need to check use of shares variables
            # print("input path: "  + inputSpace + "\\" + cfd_file + "\n")
            nc_FP = arcpy.NetCDFFileProperties(inputSpace + "\\" + cfd_file)
            nc_Dim = nc_FP.getDimensions()

            # extracts the variable name from the file name
            fluxvar = cfd_file[11:-3] 

            # for level dimension
            dimension2 = "projection"   ##THE SECOND DIMENSION##
            top2 = nc_FP.getDimensionSize(dimension2)   ##THE SECOND DIMENSION##

            # create local summary table for this netcdf file
            result_table = create_summary_table(outputSpace, "summary_" + fluxvar)

            for dimension in nc_Dim:
                if dimension == "time":
                    top = nc_FP.getDimensionSize(dimension)
                    for i in range(0, top):
                        dimension_values = nc_FP.getDimensionValue(dimension, i)
                        thedate = str(dimension_values)
                        try:
                            dt = datetime.datetime.strptime(thedate, theFormatTime)
                        except:
                            dt = datetime.datetime.strptime(thedate, theFormat)
                        justdate = str(dt.month) + "/" + str(dt.day) + "/" + str(dt.year)
                        dv1 = ["time", dimension_values]
                        # dimension_values = [dv1]
                        dv2 = ["projection", level]
                        dimension_values = [dv1,dv2]

                        # Creates a raster from the netCDF file stored in "CDFs" using the "Baseflow" variable, "lon" as the x-dimension, "lat" as the y-dimension, and default variables for
                        # the rest.
                        # print "Creating " + fluxvar + " raster for " + justdate + " " + cfd_file + "..."####
                        rasterFluxvar = arcpy.MakeNetCDFRasterLayer_md (cfd_file, fluxvar, "longitude", "latitude", os.path.join(outputSpace, fluxvar), "", dimension_values, valueSelectionMethod, "CENTER")
                        
                        # Creates a Zonal Statistics table using the specified zone layer as the zones, the watershed names as the distinguishing fields, the previously created raster as
                        # the input raster, and default variables for the rest.
                        # print "Creating " + fluxvar + " table for " + justdate + " " + cfd_file + "...\n"####
                        iotype = 'in_memory\\'  
                        outputTable = iotype + '\\' + fluxvar + "_" + str(dt.month) + "_" + str(dt.day) + "_" + str(dt.year)
                        arcpy.CreateTable_management(iotype, fluxvar + "_" + str(dt.month) + "_" + str(dt.day) + "_" + str(dt.year), "", "")   
                        
                        # print "Calculating statistics \n"
                        # uses parallel processing by default
                        arcpy.sa.ZonalStatisticsAsTable (zones, "NAME", rasterFluxvar, outputTable, "", "")

                        # Adds month, year, and type fields to newly created table.
                        # print "adding fields to stats table"
                        arcpy.AddField_management(outputTable, "thedate", "TEXT", "", "", 10, "", "", "", "")
                        arcpy.AddField_management(outputTable, "YEAR", "TEXT", "", "", 4, "", "", "", "")
                        arcpy.AddField_management(outputTable, "MONTH", "TEXT", "", "", 2, "", "", "", "")
                        arcpy.AddField_management(outputTable, "DAY", "TEXT", "", "", 2, "", "", "", "")
                        arcpy.AddField_management(outputTable, "LEVEL", "TEXT", "", "", 3, "", "", "", "")
                        arcpy.AddField_management(outputTable, "TYPE", "TEXT", "", "", 20, "", "", "", "")                   
                        
                        # Populate month, year, and type fields in new table.
                        # print "adding values to fields"
                        with arcpy.da.UpdateCursor(outputTable, ["thedate", "YEAR", "MONTH","DAY", "TYPE", "LEVEL"], "", "", "", (None, None)) as cursor:
                            for row in cursor:
                                row[0] = justdate####
                                row[1] = dt.year####
                                row[2] = dt.month####
                                row[3] = dt.day####
                                row[4] = fluxvar####
                                row[5] = level####
                                cursor.updateRow(row)
                        
                        # Appends newly created table to local result table.
                        # print "append to list of tables"
                        arcpy.Append_management(outputTable, result_table, "NO_TEST", "", "")
                        
                        # clean up memory use
                        del outputTable
                        del rasterFluxvar
                        gc.collect()
                        # break #uncomment just to get a small sample first year
                        # End range for
                    # End time if
                 # End dimension for   
            #End check if it is a netcdf file for extraction  
        # No need to return anything, tables will be on folder.   
        return         
        # End process_cdf

    except Exception as e:
        # If an error occurred, print line number and error message
        import traceback, sys
        tb = sys.exc_info()[2]
        print "An error occured on line %i" % tb.tb_lineno
        print str(e)
        return None

def create_summary_table(outputSpace, summaryFile):
    # print("Creating summary table")
    summary = arcpy.CreateTable_management(outputSpace, summaryFile + ".dbf", "", "")

    # Add fields to the table
    arcpy.AddField_management(summary, "NAME", "TEXT", "", "", 24, "", "", "", "")
    arcpy.AddField_management(summary, "thedate", "TEXT", "", "", 10, "", "", "", "")
    arcpy.AddField_management(summary, "YEAR", "TEXT", "", "", 4, "", "", "", "")
    arcpy.AddField_management(summary, "MONTH", "TEXT", "", "", 2, "", "", "", "")
    arcpy.AddField_management(summary, "DAY", "TEXT", "", "", 2, "", "", "", "")
    arcpy.AddField_management(summary, "TYPE", "TEXT", "", "", 20, "", "", "", "")   
    arcpy.AddField_management(summary, "LEVEL", "LONG", "", "", "", "", "", "", "") 
    arcpy.AddField_management(summary, "ZONE_CODE", "LONG", "", "", "", "", "", "", "")
    arcpy.AddField_management(summary, "COUNT", "LONG", "", "", "", "", "", "", "")
    arcpy.AddField_management(summary, "AREA", "DOUBLE", "", "", "", "", "", "", "")
    arcpy.AddField_management(summary, "MIN", "DOUBLE", "", "", "", "", "", "", "")
    arcpy.AddField_management(summary, "MAX", "DOUBLE", "", "", "", "", "", "", "")
    arcpy.AddField_management(summary, "RANGE", "DOUBLE", "", "", "", "", "", "", "")
    arcpy.AddField_management(summary, "MEAN", "DOUBLE", "", "", "", "", "", "", "")
    arcpy.AddField_management(summary, "STD", "DOUBLE", "", "", "", "", "", "", "")
    arcpy.AddField_management(summary, "SUM", "DOUBLE", "", "", "", "", "", "", "")

    return summary

def main():
    start_time = time.time()
    print("Starting Main...")
    
    # Checks that the Spatial Analyst extension is installed, calls the LicenseError exception if it is not.
    print "Checking Spatial Analyst license..."
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
        print "License retrieved.\n"
    else:
        raise LicenseError

    try:
        # reset environments
        arcpy.ResetEnvironments()

        environments = arcpy.ListEnvironments()

        # Sort the environment names
        environments.sort()

        # print environment and setting
        for environment in environments:
            # Format and print each environment and its current setting.
            # (The environments are accessed by key from arcpy.env.)
            print("{0:<30}: {1}".format(environment, arcpy.env[environment]))

        # Enables data overwriting.
        arcpy.env.overwriteOutput = True

        # paths
        inputSpace = "C:\\Users\\lagarnicachavira\\Documents\\Repos\\netcdf-processor\\inputs"
        outputSpace = "C:\\Users\\lagarnicachavira\\Documents\\Repos\\netcdf-processor\\outputs"

        # arcpy environment workspace
        arcpy.env.workspace = inputSpace
        
        # Stores netCDF files in variable fileList
        fileList = os.listdir(inputSpace)

        # define how many threads to use? 
        # the more threads used more ram memory used at once to allocate memory for each one...

        # Sends netCDF files processing to separate cores
        print("Multi-Processing netCDF Files...")
        pool = multiprocessing.Pool()
        pool.map(process_cdf, fileList)

        # close the process pool, will no be used again
        pool.close()

        # sync with processing jobs (wait for jobs to finish)
        pool.join()

        # change the arcpy workspace to the output folder
        arcpy.env.workspace = outputSpace

        # open generated tables from netcdf files
        tables = arcpy.ListTables()

        # Creates new table that rest of tables will be appended to, with the year as the title
        summaryFile = "Summary_Extraction"
        yearTable = create_summary_table(outputSpace, summaryFile)

        # append the generated tables to the final table
        for table in tables:
            print("Found: " + table + "\n")
            arcpy.Append_management(table, yearTable, "NO_TEST", "", "")
        
        # Returns Spatial Analyst license for use by others.
        arcpy.CheckInExtension("Spatial")

        # Converts summary dBASE table to an Excel 2003 table.
        arcpy.TableToExcel_conversion (yearTable, os.path.join(outputSpace, summaryFile + ".xls"), "", "")

        # Deletes dBASE files generated in constructing Excel file.
        outputFiles = os.listdir(outputSpace)
        os.chdir(outputSpace)
        for toDelete in outputFiles:
            if toDelete.endswith(".xls"):
                pass
            elif toDelete.endswith(".lock"):
                pass
            else:
                os.remove(toDelete)
            
        print "Check " + outputSpace + " for the created summary file, " + summaryFile + "."
        
        # print total run time
        print("Total Runtime:  %s seconds\n" % (time.time() - start_time))

        # clean arcpy instance    
        # del arcpy 

        # force garbage collector
        # gc.collect()
        
        # Closes console.
        raw_input("Script completed. Press Enter to quit.\n")
        # End main

    # Error handling.
    except LicenseError:
        print "Spatial Analyst license unavailable."
        
    except Exception as e:
        # If an error occurred, print line number and error message
        import traceback, sys
        tb = sys.exc_info()[2]
        print "An error occured on line %i" % tb.tb_lineno
        print str(e)

if __name__ == '__main__':
    main()