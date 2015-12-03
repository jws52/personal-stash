import iris
import iris.analysis
import numpy as np
import os.path

# LOAD DATA
filenames1 = () # Define the two filenames to work with
filenames2 = ()
field_titles = ()
variables = ['specific_humidity','air_temperature']
variable = raw_input(["Which variable to use?", variables, "(please type explicitly"])
response = "yes"
while response != "no":
    filename2 = raw_input("Experiment ID for baseline run of comparison?")
    filename1 = raw_input("Experiment ID for modification run of comparison?")
    field_title = raw_input ("Title of comparison?")
    filenames1 += ('/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+filename1+'.nc',)
    filenames2 += ('/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+filename2+'.nc',)
    field_titles += (field_title,)
    response = raw_input("Another pair to compare? (yes/no)")
tropic_lats = iris.Constraint(latitude = lambda l: -10<=l<=10) # constrains loaded data to the tropical latitudes -10deg to +10deg

# ANALYSIS
q_mean = [] # Location for saved data during looping for annual mean in each comparison
q_season = [] # Location for saved data during looping for seasonal cycle amplitude in each comparison
for i in range(len(filenames1)): # Loop over all comparison runs
    # Load cubes specifically for q in tropics
    if os.path.isfile(filenames1[i]) == False: print("Error: An experiment ID not found."); continue # Check files exist
    if os.path.isfile(filenames2[i]) == False: print("Error: An experiment ID not found."); continue
    cube1= iris.load(filenames1[i], variable & tropic_lats)
    cube2= iris.load(filenames2[i], variable & tropic_lats)
    q1= cube1[0]
    q2= cube2[0]
    # Select the overlapping time periods
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
        # Extracting region in time suitable for comparison
    ## Can modify so that script takes maximum number of 12-month periods from q_01.coord('t').points
    t_start = 1999 #input("Starting year? Expect 1999.")
    t_end = 2008 #input("Endingyear? Expect 2008.")
    yr0 = (q_final1.coord('t').points >= (t_start-1-1988)*360+120) & (q_final1.coord('t').points < (t_end-1988)*360+120)
    #print yr0
    
    # Calculation of difference in annual mean
    q_final = q_final1 - q_final2
    final_diff = q_final[yr0]
    d_mean = final_diff.collapsed('t', iris.analysis.MEAN)
    if variable == 'water_vapour' : diff_mean = d_mean.data.item()*1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv, and converting from 0d array to scalar
    if variable == 'air_temperature' : diff_mean = d_mean.data.item() # converting from 0d array to scalar 
    print "Difference in annual mean is: ",diff_mean
    q_mean.append(diff_mean) 
    
    # Calculation of difference in seasonal cycle amplitude
    # Forming the climatological mean for t_start to t_end
    q_diff1 = q_final1[yr0]
    q_diff2 = q_final2[yr0]
    import iris
    import iris.coord_categorisation
    # Finding amplitude of seasonal cycle
    iris.coord_categorisation.add_month(q_diff1, 't', name='climatological months')
    iris.coord_categorisation.add_month(q_diff2, 't', name='climatological months')
    #print q_diff1
    #print q_diff2
    climatological_mean1 = q_diff1.aggregated_by(['climatological months'], iris.analysis.MEAN)
    climatological_mean2 = q_diff2.aggregated_by(['climatological months'], iris.analysis.MEAN)
    #print repr(climatological_mean1)
    #print repr(climatological_mean2)
    #climatological_mean1.coord('climatological months')
    #climatological_mean2.coord('climatological months')
    seasonal_cycle1 = max(climatological_mean1.data)- min(climatological_mean1.data)
    seasonal_cycle2 = max(climatological_mean2.data)- min(climatological_mean2.data)
    # Taking difference in seasonal cycle
    diff_in_seasonal_cycle = (seasonal_cycle1-seasonal_cycle2)
    if variable == 'specific_humidity': diff_in_seasonal_cycle *= 1.608e6        # 1.608e6 is the units conversion from kg.kg^-1 to ppmv)
    print "Difference in seasonal cycle is: ", diff_in_seasonal_cycle
    q_season.append(diff_in_seasonal_cycle) 
print q_mean
print q_season

# PLOTTING
import matplotlib.pyplot as plt
plt.plot(q_mean[0],q_season[0], 'bo', q_mean[1],q_season[1], 'yo', q_mean[2],q_season[2], 'mo', q_mean[3],q_season[3], 'go')
plt.legend(field_titles, loc=2)
plt.xlabel("q_mean")
plt.ylabel("q_season")
plt.show()

# then compare the results to those in Met Office plots
