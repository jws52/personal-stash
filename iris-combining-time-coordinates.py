# This Python script fills in a missing point in sequential data.
# (e.g. a series of monthly data fields with one month's data missing in the middle)
# Any questions, ask jws52 [at] cam.ac.uk

# Tread with caution- Some specific assumptions in the script may need to be changed:
# A single dimension has a missing point.
# The long_name of the coordinate with the missing point is 't' (for time)
# The value at the missing coordinate point is 6195
# The index at the missing dimension point is 206 
# Three fields are to be computed, at positions 1, 4 and 5 in the input cubelist
# Input filename is 'partial_cube_list.nc'

import iris
import iris.analysis
import iris.coords
import iris.coord_categorisation
import numpy as np
from iris.experimental.equalise_cubes import equalise_attributes

print "Loading the original file with a missing month in the sequence" #(with fields in temp, humidity and upward air velocity at index positions 1, 4 and 5).
cube1 = iris.load('partial_cube_list.nc')
print "create the missing month from interpolating linearly" # to create 't'=6195 and save result to samplew, samplet and sampleq
samplew = iris.analysis.interpolate.linear(cube1[1],[('t',6195)])
samplet = iris.analysis.interpolate.linear(cube1[4],[('t',6195)])
sampleq = iris.analysis.interpolate.linear(cube1[5],[('t',6195)])
# Consider checking the missing month for consistent attributes, aux_coords and dim_coords

print "Slicing original cube at missing month"
cubew1 = cube1[1][:206]
cubet1 = cube1[4][:206]
cubeq1 = cube1[5][:206]
cubew2 = cube1[1][206:]
cubet2 = cube1[4][206:]
cubeq2 = cube1[5][206:]
print "Subsetting cubes as a cubelist in time" (so that each cube has 't' as a scalar co-ordinate)
cubelistw1 = []
cubelistt1 = []
cubelistq1 = []
for i in range(len(cubew1.coord('t').points)): cubelistw1 += [cubew1[i,:,:,:]]
for i in range(len(cubet1.coord('t').points)): cubelistt1 += [cubet1[i,:,:,:]]
for i in range(len(cubeq1.coord('t').points)): cubelistq1 += [cubeq1[i,:,:,:]]
cubelistw1 += [samplew]
cubelistt1 += [samplet]
cubelistq1 += [sampleq]
new = len(cubelistw1)-1
for i in range(len(cubew2.coord('t').points)): cubelistw1 += [cubew2[i,:,:,:]]
for i in range(len(cubet2.coord('t').points)): cubelistt1 += [cubet2[i,:,:,:]]
for i in range(len(cubeq2.coord('t').points)): cubelistq1 += [cubeq2[i,:,:,:]]
cubelistw1 = iris.cube.CubeList(cubelistw1)
cubelistt1 = iris.cube.CubeList(cubelistt1)
cubelistq1 = iris.cube.CubeList(cubelistq1)

print"Checking attributes are the same (prints 'False' below if not)"
if cubelistw1[new].attributes == cubelistw1[new-1].attributes and cubelistt1[new].attributes == cubelistt1[new-1].attributes and cubelistq1[new].attributes == cubelistq1[new-1].attributes:
    print "True"
else: print "False"

print"Order and merge the related cubes"
mergew = cubelistw1.merge_cube()
merget = cubelistt1.merge_cube()
mergeq = cubelistq1.merge_cube()
mergedlist = iris.cube.CubeList([mergew,merget,mergeq])

# Saving the results to file
querysave = raw_input("Do you want to save the result as netCDF? (y/n)")
if querysave == "y":
  savename = raw_input("What do you want to save the resulting .nc file as?")
  iris.save(mergedlist, "savename"+".nc", netcdf_format="NETCDF3_CLASSIC")
  print "Finished and saved result to file"
else: print "Finished without saving to file, results should be available in memory to test and mainpulate."
