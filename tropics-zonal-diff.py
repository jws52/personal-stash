import iris
import iris.analysis
import numpy as np
##
# Define the two filenames to work with
filenames1 = ()
filenames2 = ()
response = "yes"
while response != "no":
    filename2 = raw_input("Experiment ID for baseline run of comparison?")
    filename1 = raw_input("Experiment ID for modification run of comparison?")
    filenames1 += ('/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+filename1+'.nc',)
    filenames2 += ('/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+filename2+'.nc',)
    response = raw_input("Another pair to compare? (yes/no)")

##filename1 = raw_input("First experiment ID?")
##filename2 = raw_input("Second experiment ID?")
#filename1 = '/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+filename1+'.nc'
#filename2 = '/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+filename2+'.nc'
tropic_lats = iris.Constraint(latitude = lambda l: -10<=l<=10) # constrains loaded data to the tropical latitudes -10deg to +10deg

#Loop over all comparison runs
q_mean= [] #Location for saved data during looping
for i in range(len(filenames1)):
    cube1= iris.load(filenames1[i], 'specific_humidity' & tropic_lats)
    cube2= iris.load(filenames2[i], 'specific_humidity' & tropic_lats)
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
    #print('New time co-ordinate range is for set 1: /n',q01.coord('t'))
    #print('New time co-ordinate range is for set 2: /n',q02.coord('t'))
    
    # Form the zonal mean
    q_zonal_01 = q01.collapsed('longitude', iris.analysis.MEAN)
    q_zonal_02 = q02.collapsed('longitude', iris.analysis.MEAN)
    
    # Form the mean over the tropics
    q_trop_zonal_01 = q_zonal_01.collapsed('latitude', iris.analysis.MEAN)
    q_trop_zonal_02 = q_zonal_02.collapsed('latitude', iris.analysis.MEAN)
    
    # Select the pressure level (100hPa for q)
    q_final1 = q_trop_zonal_01.extract(iris.Constraint(Pressure=100))
    q_final2 = q_trop_zonal_02.extract(iris.Constraint(Pressure=100))
    q_final = q_final1 - q_final2
    
    # Forming the annual-mean for 1999-2008
    ## This is a test, intending to put this in a for loop, or find a more efficient way to take the mean of the months
    t_start = 1999 #input("Starting year? Expect 1999.")
    t_end = 2008 #input("Endingyear? Expect 2008.")
    yr0 = (q_final.coord('t').points >= (t_start-1-1988)*360+120) & (q_final.coord('t').points < (t_end-1988)*360+120)
    #print yr0
    q_diff = q_final[yr0]
    q_diff_mean = q_diff.collapsed('t', iris.analysis.MEAN)
    print("Difference in annual mean is: ",q_diff_mean.data *1.608e6, "ppmv")
    q_mean.append(q_diff_mean.data*1.608e6)

print q_mean
# Plotting the difference as a function of time
#import matplotlib.pyplot as plt
#import iris.plot as iplt
#import iris.quickplot as qplot
#qplot.plot(q_final)
#plt.show()
