import iris
import iris.analysis
import numpy as np
##
# Define the two filenames to work with
filename1 = '/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-aojed.nc'
filename2 = '/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-aojeb.nc'
tropic_lats = iris.Constraint(latitude = lambda l: -10<=l<=10) # constrains loaded data to the tropical latitudes -10deg to +10deg
q1= iris.load(filename1, 'specific_humidity' & tropic_lats)
q2= iris.load(filename2, 'specific_humidity' & tropic_lats)

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

## Form the zonal mean
q_zonal01 = q01.collapsed('longitude', iris.analysis.MEAN)
q_zonal02 = q02.collapsed('longitude', iris.analysis.MEAN)

# Form the mean over the tropics
q_trop_zonal_01 = q_zonal_01.collapsed('latitude', iris.analysis.MEAN)
q_trop_zonal_02 = q_zonal_02.collapsed('latitude', iris.analysis.MEAN)

# Select the pressure level (100hPa for q, and 100hPa for T)
q_final1 = q_trop_zonal_01.extract(iris.Constraint(Pressure=100))
q_final2 = q_trop_zonal_02.extract(iris.Constraint(Pressure=100))
q_final = q_final1 - q_final2

# Forming the annual-mean for 1999-2008
## This is a test, intending to put this in a for loop, or find a more efficient way to take the mean of the months
t_start = input("Starting year? Expect 1999.")
t_end = input("Endingyear? Expect 2008.")
yr0 = (q_final.coord('t').points >= (t_start-1-1988)*360+120) & (q_final.coord('t').points < (t_end-1988)*360+120)
#print yr0
q_diff = q_final[yr0]
q_diff_mean = q_diff.collapsed('t', iris.analysis.MEAN)
print q_diff_mean

# Plotting the difference as a function of time
#import matplotlib.pyplot as plt
#import iris.plot as iplt
#import iris.quickplot as qplot
#qplot.plot(q_final)
#plt.show()
