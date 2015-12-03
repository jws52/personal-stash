import iris
import iris.analysis
import numpy as np
##
# Define the two filenames to work with
filename1 = raw_input("First experiment ID?")
filename2 = raw_input("Second experiment ID?")
filename1 = '/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+filename1+'.nc'
filename2 = '/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+filename2+'.nc'
tropic_lats = iris.Constraint(latitude = lambda l: -10<=l<=10) # constrains loaded data to the tropical latitudes -10deg to +10deg
cube1= iris.load(filename1, 'specific_humidity' & tropic_lats)
cube2= iris.load(filename2, 'specific_humidity' & tropic_lats)
q1= cube1[0]
q2= cube2[0]
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
q_zonal_01 = q01.collapsed('longitude', iris.analysis.MEAN)
q_zonal_02 = q02.collapsed('longitude', iris.analysis.MEAN)

# Form the mean over the tropics
q_trop_zonal_01 = q_zonal_01.collapsed('latitude', iris.analysis.MEAN)
q_trop_zonal_02 = q_zonal_02.collapsed('latitude', iris.analysis.MEAN)

# Select the pressure level (100hPa for q)
q_final1 = q_trop_zonal_01.extract(iris.Constraint(Pressure=100))
q_final2 = q_trop_zonal_02.extract(iris.Constraint(Pressure=100))

# Forming the climatological mean for 1999-2008
## This is a test, intending to put this in a for loop, or find a more efficient way to take the mean of the months
t_start = input("Starting year? Expect 1999.")
t_end = input("Endingyear? Expect 2008.")
yr0 = (q_final1.coord('t').points >= (t_start-1-1988)*360+120) & (q_final1.coord('t').points < (t_end-1988)*360+120)
q_diff1 = q_final1[yr0]
q_diff2 = q_final2[yr0]
import iris
import iris.coord_categorisation

# For q_diff1
iris.coord_categorisation.add_month(q_diff1, 't', name='climatological months')
#print q_diff1
climatological_mean1 = q_diff1.aggregated_by(['climatological months'], iris.analysis.MEAN)
#print repr(climatological_mean1)
#climatological_mean1.coord('climatological months')
seasonal_cycle1 = max(climatological_mean1.data)- min(climatological_mean1.data)

# Now repeat for q_diff2
iris.coord_categorisation.add_month(q_diff2, 't', name='climatological months')
#print q_diff2
climatological_mean2 = q_diff2.aggregated_by(['climatological months'], iris.analysis.MEAN)
#print repr(climatological_mean2)
#climatological_mean2.coord('climatological months')
seasonal_cycle2 = max(climatological_mean2.data)- min(climatological_mean2.data)

# then take (max value) - (min value)
diff_in_seasonal_cycle = (seasonal_cycle1-seasonal_cycle2)
diff_in_seasonal_cycle *= 1.608e6        # 1.608 is the units conversion from kg.kg^-1 to ppmv)
print ("Difference in seasonal cycle is: ", diff_in_seasonal_cycle, " ppmv\n")

# then compare the results to those in Met Office plots
