import iris
import iris.analysis
import numpy as np
import os.path
import matplotlib.pyplot as plt
import iris.coord_categorisation

# LOAD DATA
# Define the two filenames to work with
filenames1 = ()
filenames2 = ()
for name in ['aojeb', 'antie', 'antie', 'antie', 'antie', 'antie', 'dkwyj']: filenames2 += ('/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+name+'.nc',)
for name in ['aojed', 'antng', 'dlkxi', 'anvti', 'dlhbk', 'anxal', 'dkytg']: filenames1 += ('/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+name+'.nc',) 
field_titles = ('ozone radiative feedback', 'radiative heating', 'ice microphysics', 'cirrus spreading rate', 'convection', 'ice optics', 'q vertical advection - interpolation')
variables = ['specific_humidity','air_temperature']
variable = raw_input(["Which variable to use?", variables, "(please type explicitly"])

tropic_lats = iris.Constraint(latitude = lambda l: -10<=l<=10) # constrains loaded data to the tropical latitudes -10deg to +10deg

# ANALYSIS
q_mean = [] # Location for saved data during looping for annual mean in each comparison
q_season = [] # Location for saved data during looping for seasonal cycle amplitude in each comparison
# Loop over all comparison runs
for i in range(len(filenames1)):  
    # Check files exist 
    if os.path.isfile(filenames1[i]) == False: print("Error: An experiment ID not found."); continue 
    if os.path.isfile(filenames2[i]) == False: print("Error: An experiment ID not found."); continue
    # Load cubes specifically for q in tropics
    cube1= iris.load(filenames1[i], variable & tropic_lats)
    cube2= iris.load(filenames2[i], variable & tropic_lats)
    q1= cube1[0]
    q2= cube2[0]
    # Selecting the overlapping time periods
    time_coord1 = q1.coord('t')
    time_coord2 = q2.coord('t')
    t_range2 = (time_coord2.points >= time_coord1.points[0]) & (time_coord2.points <= time_coord1.points[-1])
    t_range1 = (time_coord1.points >= time_coord2.points[0]) & (time_coord1.points <= time_coord2.points[-1])
    q01 = q1[t_range1,:,:,:]
    q02 = q2[t_range2,:,:,:]
    #print('New time co-ordinate range is for set 1: /n',q01.coord('t'))
    #print('New time co-ordinate range is for set 2: /n',q02.coord('t'))
    # Extracting region in time suitable for comparison
    ### Can modify so that script takes maximum number of 12-month periods from q_01.coord('t').points
    t_start = 1999
    t_end = 2008
    # Time origin is 01-SEP-1988:00:00:00
    yr0 = (q01.coord('t').points >= (t_start-1-1988)*360+120) & (q01.coord('t').points < (t_end-1988)*360+120)
    # Select the pressure level (100hPa for q, or T)
    q_p_01 = q01.extract(iris.Constraint(Pressure=100))
    q_p_02 = q02.extract(iris.Constraint(Pressure=100))
  
    ## Calculation of difference in annual mean in lat-long
    q_p_final = q_p_01 - q_p_02
    final_diff = q_p_final[yr0]
    diff_in_annual_mean = final_diff.collapsed('t', iris.analysis.MEAN)
    if variable == 'specific_humidity' : diff_in_annual_mean.data *= 1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv
    print "Calculated annual mean at each latitude-longitude point"

    ## Calculation of difference in annual mean, averaged in zonal and meridional
    diff_mean_mod = diff_in_annual_mean.collapsed('longitude', iris.analysis.MEAN) #zonal mean
    q_mean_averaged = diff_mean_mod.collapsed('latitude', iris.analysis.MEAN) # meridional mean
    print "Difference in annual mean is: ", q_mean_averaged
    q_mean.append(q_mean_averaged.data.item())  # converting from 0d array to scalar and saving result
   
    ## Calculation of difference in seasonal cycle amplitude in lat-long
    q_diff1 = q_p_01[yr0]
    q_diff2 = q_p_02[yr0]
    # Finding amplitude of seasonal cycle
    # Forming climatological months
    iris.coord_categorisation.add_month(q_diff1, 't', name='climatological months')
    iris.coord_categorisation.add_month(q_diff2, 't', name='climatological months')
    climatological_mean1 = q_diff1.aggregated_by(['climatological months'], iris.analysis.MEAN)
    climatological_mean2 = q_diff2.aggregated_by(['climatological months'], iris.analysis.MEAN)
    cycle1_max = climatological_mean1.collapsed('t', iris.analysis.MAX)
    cycle1_min = climatological_mean1.collapsed('t', iris.analysis.MIN)
    cycle2_max = climatological_mean2.collapsed('t', iris.analysis.MAX)
    cycle2_min = climatological_mean2.collapsed('t', iris.analysis.MIN)
    seasonal_cycle1 = cycle1_max - cycle1_min # This is the amplitude
    seasonal_cycle2 = cycle2_max - cycle2_min
    # Taking difference in seasonal cycle
    diff_in_seasonal_cycle = seasonal_cycle1-seasonal_cycle2
    if variable == 'specific_humidity': diff_in_seasonal_cycle *= 1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv)
    print "Calculated seasonal difference at each latitude-longitude point"

    ## Calculation of difference in seasonal cycle amplitude, averaged in zonal and meridional
    diff_season1_mod = q_diff1.collapsed('longitude', iris.analysis.MEAN)
    diff_season2_mod = q_diff2.collapsed('longitude', iris.analysis.MEAN)
    q_season1_averaged = diff_season1_mod.collapsed('latitude', iris.analysis.MEAN)
    q_season2_averaged = diff_season2_mod.collapsed('latitude', iris.analysis.MEAN)
    iris.coord_categorisation.add_month(q_season1_averaged, 't', name='climatological months - horizontally averaged')
    iris.coord_categorisation.add_month(q_season2_averaged, 't', name='climatological months - horizontally averaged')
    climatological_mean1 = q_season1_averaged.aggregated_by(['climatological months - horizontally averaged'], iris.analysis.MEAN)
    climatological_mean2 = q_season2_averaged.aggregated_by(['climatological months - horizontally averaged'], iris.analysis.MEAN)
    cycle1_max = climatological_mean1.collapsed('t', iris.analysis.MAX)
    cycle1_min = climatological_mean1.collapsed('t', iris.analysis.MIN)
    cycle2_max = climatological_mean2.collapsed('t', iris.analysis.MAX)
    cycle2_min = climatological_mean2.collapsed('t', iris.analysis.MIN)
    seasonal_cycle1 = cycle1_max - cycle1_min # This is the amplitude
    seasonal_cycle2 = cycle2_max - cycle2_min
    # Taking difference in seasonal cycle
    diff_in_seasonal_cycle_averaged = seasonal_cycle1-seasonal_cycle2
    if variable == 'specific_humidity': diff_in_seasonal_cycle_averaged *= 1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv)
    print "Calculated seasonal difference at each latitude-longitude point"
    q_season.append(diff_in_seasonal_cycle_averaged) 

    # PLOTTING
    import iris.quickplot as qplt
    plt.figure(i)
    ### For annual mean in lat-long
    plt.subplot(211)
    qplt.contourf(diff_in_annual_mean)
    plt.title(field_titles[i]+' effect on annual mean, with region average of'+'{:7.3f}'.format(q_mean_averaged.data.item()))
    ### For difference in seasonal cycle in lat-long
    plt.subplot(212)
    qplt.contourf(diff_in_seasonal_cycle)
    plt.title(field_titles[i]+' effect on seasonal cycle, with region average of'+'{:7.3f}'.format(float(diff_in_seasonal_cycle_averaged.data)))

### plt.axes labels and legends
plt.show()
# then compare the results to those in Met Office plots

