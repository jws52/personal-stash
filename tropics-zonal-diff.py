#Code to obtain zonal mean and meridional mean across 10degS-10degN and difference between two datasets

import iris
import iris.analysis
import numpy as np
##
# Define the two filenames to work with
filename1 = '/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-aojed.nc'
filename2 = '/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-aojeb.nc'
cubes1= iris.load(filename1)
cubes2= iris.load(filename2)
# Load specific humidity cube for each file
q1 = cubes1[4]
q2 = cubes2[4]
#Select the overlapping time periods
time_coord1 = q1.coord('t')
time_coord2 = q2.coord('t')
print(time_coord1)
print(time_coord2)
t_range2 = (time_coord2.points > time_coord1.points[0]) & (time_coord2.points < time_coord1.points[-1])
t_range1 = (time_coord1.points > time_coord2.points[0]) & (time_coord1.points < time_coord2.points[-1])
q01 = q1[t_range1,:,:,:]
q02 = q2[t_range2,:,:,:]
q01
q02
print(q02[:,1,1,1])
print(q01[:,1,1,1])
print(q2.coord('t'))
print(q1.coord('t'))
# Form the zonal mean
zonal_mean1 = q1.collapsed('longitude', iris.analysis.MEAN)
zonal_mean2 = q2.collapsed('longitude', iris.analysis.MEAN)
# Form the mean over the tropics
coord1 = q1.coord('latitude')
coord2 = q2.coord('latitude')
tropics1 = (coord1.points <=10) & (coord1.points >= -10)
tropics2 = (coord2.points <=10) & (coord2.points >= -10)







