import iris
import iris.analysis
import iris.coords
import iris.coord_categorisation
import numpy as np
from iris.experimental.equalise_cubes import equalise_attributes

# Load the 
cubew1 = iris.load_cube('anmxa-partial-1w.nc')
cubet1 = iris.load_cube('anmxa-partial-1t.nc')
cubeq1 = iris.load_cube('anmxa-partial-1q.nc')
cubew2 = iris.load_cube('anmxa-partial-2w.nc')
cubet2 = iris.load_cube('anmxa-partial-2t.nc')
cubeq2 = iris.load_cube('anmxa-partial-2q.nc')
month = iris.load('anmxa-missingmonth.nc')

montht = month[0]
monthq = month[1]
monthw = month[2]

## For cubes above interpolate linearly between to create 't'= and save result to monthw, montht, monthq
## And check that the field names in the resulting cubes are the same as the original (except for the time value)

# Subsetting cubes cubelist in time (so that each cube has 't' as a scalar co-ordinate)
cubelistw1 = []
cubelistt1 = []
cubelistq1 = []
#cubelistw2 = []
#cubelistt2 = []
#cubelistq2 = []
for i in range(len(cubew1.coord('t').points)): cubelistw1 += [cubew1[i,:,:,:]]
for i in range(len(cubet1.coord('t').points)): cubelistt1 += [cubet1[i,:,:,:]]
for i in range(len(cubeq1.coord('t').points)): cubelistq1 += [cubeq1[i,:,:,:]]
cubelistw1 += [monthw]
cubelistt1 += [montht]
cubelistq1 += [monthq]
new = len(cubelistw1)-1
for i in range(len(cubew2.coord('t').points)): cubelistw1 += [cubew2[i,:,:,:]]
for i in range(len(cubet2.coord('t').points)): cubelistt1 += [cubet2[i,:,:,:]]
for i in range(len(cubeq2.coord('t').points)): cubelistq1 += [cubeq2[i,:,:,:]]
cubelistw1 = iris.cube.CubeList(cubelistw1)
cubelistt1 = iris.cube.CubeList(cubelistt1)
cubelistq1 = iris.cube.CubeList(cubelistq1)
#cubelistw2 = iris.cube.CubeList(cubelistw2)
#cubelistt2 = iris.cube.CubeList(cubelistt2)
#cubelistq2 = iris.cube.CubeList(cubelistq2)

#Set attributes are the same
cubelistw1[new].attributes = cubelistw1[new-1].attributes
cubelistt1[new].attributes = cubelistt1[new-1].attributes
cubelistq1[new].attributes = cubelistq1[new-1].attributes




#Order and merge the related cubes
#cubelistw = []
#cubelistt = []
#cubelistq = []
#cubelistw = [cubelistw1, monthw, cubelistw2]
#cubelistt = [cubelistt1, montht, cubelistt2]
#cubelistq = [cubelistq1, monthq, cubelistq2]
#cubelistw = iris.cube.CubeList(cubelistw)
#cubelistt = iris.cube.CubeList(cubelistt)
#cubelistq = iris.cube.CubeList(cubelistq)
mergew = cubelistw1.merge_cube()
#### Get an error here: "failed to merge into a single cube.
  #Coordinates in cube.aux_coords (scalar) differ: t.
  #Coordinates in cube.dim_coords differ: longitude."
  #Try to fix with new_aux_coord = iris.coords.AuxCoord(6195, units='days since 1988-09-01 00:00:00', long_name='t', var_name ='t')
  #cubelistw1[new].add_aux_coord(new_aux_coord)

merget = cubelistt1.merge_cube()
mergeq = cubelistq1.merge_cube()

# Save files
