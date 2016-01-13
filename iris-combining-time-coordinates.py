import iris
import iris.analysis
import iris.coords
import iris.coord_categorisation
import numpy as np

# Load the 
cubew1 = iris.load('anmxa-partial-1w.nc')
cubet1 = iris.load('anmxa-partial-1t.nc')
cubeq1 = iris.load('anmxa-partial-1q.nc')
cubew2 = iris.load('anmxa-partial-2w.nc')
cubet2 = iris.load('anmxa-partial-2t.nc')
cubeq2 = iris.load('anmxa-partial-2q.nc')


## For cubes above interpolate linearly between to create 't'= and save result to monthw, montht, monthq
## And check that the field names in the resulting cubes are the same as the original (except for the time value)

# Subsetting cubes cubelist in time (so that each cube has 't' as a scalar co-ordinate)
cubelistw1 = []
cubelistt1 = []
cubelistq1 = []
cubelistw2 = []
cubelistt2 = []
cubelistq2 = []
for i in range(len(cubew1)): cubelistw1 += cubew1[1][i,:,:,:]
for i in range(len(cubet1)): cubelistt1 += cubet1[1][i,:,:,:]
for i in range(len(cubeq1)): cubelistq1 += cubeq1[1][i,:,:,:]
for i in range(len(cubew2)): cubelistw2 += cubew2[1][i+206,:,:,:]
for i in range(len(cubet2)): cubelistt2 += cubet2[1][i+206,:,:,:]
for i in range(len(cubeq2)): cubelistq2 += cubeq2[1][i+206,:,:,:]
cubelistw1 = iris.CubeList(cubelistw1)
cubelistt1 = iris.CubeList(cubelistt1)
cubelistq1 = iris.CubeList(cubelistq1)
cubelistw2 = iris.CubeList(cubelistw2)
cubelistt2 = iris.CubeList(cubelistt2)
cubelistq2 = iris.CubeList(cubelistq2)

#Order and merge the related cubes
cubelistw = [cubelistw1, monthw, cubelistw2]
cubelistt = [cubelistt1, montht, cubelistt2]
cubelistq = [cubelistq1, monthq, cubelistq2]
cubelistw = iris.CubeList(cubelistw)
cubelistt = iris.CubeList(cubelistt)
cubelistq = iris.CubeList(cubelistq)
mergew = cubelistw.merge_cube()
merget = cubelistt.merge_cube()
mergeq = cubelistq.merge_cube()

# Save files
