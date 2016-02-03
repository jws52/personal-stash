import iris
import iris.analysis
import numpy as np
import os.path
import matplotlib.pyplot as plt
import iris.coord_categorisation
plt.gca().set_color_cycle(['limegreen', 'green','deepskyblue', 'yellow', 'magenta', 'darkviolet','darkorange','darkgrey','blue'])

# LOAD DATA
# Define the two filenames to work with
filenames1 = ()
filenames2 = ()
for name in ['anmxa', 'antie', 'dkwyj', 'antie', 'antie', 'antie', 'antie', 'antie', 'aojeb']: filenames2 += ('/group_workspaces/jasmin2/ukca/vol1/jsmith52/tq-selections/tq-selection-'+name+'.nc',)
for name in ['dkwyj', 'dlvpd', 'dkytg', 'antng', 'anxal', 'dlkxi', 'dlhbk', 'anvti', 'aojed']: filenames1 += ('/group_workspaces/jasmin2/ukca/vol1/jsmith52/tq-selections/tq-selection-'+name+'.nc',)
field_titles = ('theta vertical advection - interpolation', 'theta vertical advection - conservation', 'q vertical advection - interpolation', 'radiative heating', 'ice optics','ice microphysics', 'convection','cirrus spreading rate', 'ozone radiative feedback')
variables = ['specific_humidity','air_temperature']
variable = raw_input(["Which variable to use?", variables, "(please type explicitly"])
latlim = input("what latitude limit do you want to take for the tropical meridional mean?  (symmetrical in degrees e.g Type 10 to get mean over 10N to 10S.)")
if latlim < 0: latlim = input(["Not recognised, try again, enter a number >= 0"])
tropic_lats = iris.Constraint(latitude = lambda l: -latlim<=l<=latlim) # constrains loaded data to the tropical latitudes

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
    ### Can modify so that script takes maximum number of 12-month periods from q_01.coord('t').pointsi instead of suitable time region
    t_start = 1999
    t_end = 2008
    # Time origin is 01-SEP-1988:00:00:00
    yr0 = (q01.coord('t').points >= (t_start-1-1988)*360+120) & (q01.coord('t').points < (t_end-1988)*360+120)
    ### Constrain the pressure level to region of interest (near the tropopause)
    
    ## Error-checking the files
    for cube in [q01, q02]:
        if cube.coord('longitude').circular== False: 
            print "Correcting longitude coordinate description to be circular (remnant of interpolation and merge method)"
            cube.coord('longitude').circular=True
    ##
    
    ## Calculation of difference in annual mean, averaged in zonal and meridional
    q_p_final = q01 - q02
    final_diff = q_p_final[yr0]
    diff_in_annual_mean = final_diff.collapsed('t', iris.analysis.MEAN)
    if variable == 'specific_humidity' : diff_in_annual_mean.data *= 1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv
    diff_mean_mod = diff_in_annual_mean.collapsed('longitude', iris.analysis.MEAN) #zonal mean
    q_mean_averaged = diff_mean_mod.collapsed('latitude', iris.analysis.MEAN) # meridional mean
    print "Calculated difference in annual mean for", field_titles[i]

    ## Calculation of difference in seasonal cycle amplitude, averaged in zonal and meridional
    q_diff1 = q01[yr0]
    q_diff2 = q02[yr0]
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
    diff_season_mod = diff_in_seasonal_cycle.collapsed('longitude', iris.analysis.MEAN)
    q_season_averaged = diff_season_mod.collapsed('latitude', iris.analysis.MEAN)
    print "Calculated difference in seasonal cycle for", field_titles[i]

    # PLOTTING
    ### For annual mean bias profile in vertical
    #plt.subplot(211)
    plt.plot(q_mean_averaged.data, q_mean_averaged.coord('Pressure').points) 
    if variable == 'specific_humidity': plt.legend(field_titles, loc=2)   ### For difference in seasonal cycle profile in vertical
    elif variable == 'air_temperature': plt.legend(field_titles, loc=3)   ### For difference in seasonal cycle profile in vertical
    #plt.subplot(212)
    #plt.gca().set_color_cycle(['limegreen', 'green','deepskyblue', 'yellow', 'magenta', 'darkviolet','darkorange','darkgrey','blue'])
    #plt.plot(q_season_averaged.data, q_season_averaged.coord('Pressure').points) 
    #plt.legend(field_titles, loc=2)

### plt.axes labels and legends
#plt.subplot(211)
plt.plot([0 for x in q_season_averaged.coord('Pressure').points],q_season_averaged.coord('Pressure').points, 'k--')
plt.title('Vertical profile of annual mean bias for'+variable+'within '+str(latlim)+'degN/S')
plt.yscale('log')
plt.ylim(50, 250)
plt.yticks([250, 200, 100, 80, 60, 50], ['250', '200', '100', '80', '60', '50'])
if variable == 'specific_humidity': plt.xlim(-5,5)
if variable == 'air_temperature': plt.xlim(-2.6, 2.6)
plt.ylabel('pressure (hPa)')
if variable == 'specific_humidity': plt.xlabel('difference (ppmv)')
if variable == 'air_temperature': plt.xlabel('difference (C)')
plt.gca().invert_yaxis()
#plt.subplot(212)
#plt.plot([0 for x in q_season_averaged.coord('Pressure').points],q_season_averaged.coord('Pressure').points, 'k--')
#plt.title('Vertical profile of difference in seasonal cycle for'+variable)
#plt.yscale('log')
#plt.ylim(50, 500)
#if variable == 'specific_humidity': plt.xlim(-200, 200)
#if variable == 'air_temperature': plt.xlim(-2.6, 2.6)
#plt.ylabel('pressure (hPa)')
#if variable == 'specific_humidity': plt.xlabel('difference (ppmv)')
#if variable == 'air_temperature': plt.xlabel('difference (C)')
#plt.gca().invert_yaxis()
#plt.tight_layout()
plt.show()
# then compare the results to those in Met Office plots

