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
#print(time_coord1)
#print(time_coord2)
t_range2 = (time_coord2.points >= time_coord1.points[0]) & (time_coord2.points <= time_coord1.points[-1])
t_range1 = (time_coord1.points >= time_coord2.points[0]) & (time_coord1.points <= time_coord2.points[-1])
q01 = q1[t_range1,:,:,:]
q02 = q2[t_range2,:,:,:]
print('New time co-ordinate range is for set 1: /n',q01.coord('t'))
print('New time co-ordinate range is for set 2: /n',q02.coord('t'))

# Form the zonal mean
q_zonal1 = q01.collapsed('longitude', iris.analysis.MEAN)
q_zonal2 = q02.collapsed('longitude', iris.analysis.MEAN)

# Form the mean over the tropics
coord1 = q1.coord('latitude')
coord2 = q2.coord('latitude')
tropics1 = (coord1.points <=10) & (coord1.points >= -10)
tropics2 = (coord2.points <=10) & (coord2.points >= -10)
q_trop_zonal_01 = q_zonal1[:,:,tropics1]
q_trop_zonal_02 = q_zonal2[:,:,tropics2]
q_trop_zonal_01 = q_trop_zonal_01.collapsed('latitude', iris.analysis.MEAN)
q_trop_zonal_02 = q_trop_zonal_02.collapsed('latitude', iris.analysis.MEAN)

# Select the pressure level (70hPa for q, and 100hPa for T)
q_final1 = q_trop_zonal_01.extract(iris.Constraint(Pressure=70))
q_final2 = q_trop_zonal_02.extract(iris.Constraint(Pressure=70))
q_final = q_final1 - q_final2

# Plotting the difference as a function of time
import matplotlib.pyplot as plt
import iris.plot as iplt
import iris.quickplot as qplot
qplot.plot(q_final)
plt.show()
