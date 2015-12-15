import iris
import iris.analysis
import iris.coord_categorisation
import matplotlib.pyplot as plt
import numpy as np
import os.path

# LOAD DATA
filenames1 = () # Define the two filenames to work with
filenames2 = ()
variables = ['specific_humidity','air_temperature']
variable = raw_input(["Which variable to use?", variables, "(please type explicitly"])
for name in ['aojeb', 'antie', 'antie', 'antie', 'antie', 'antie', 'dkwyj', 'antie']: filenames2 += ('/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+name+'.nc',)
for name in ['aojed', 'antng', 'dlkxi', 'anvti', 'dlhbk', 'anxal', 'dkytg','dlvpd']: filenames1 += ('/group_workspaces/jasmin2/ukca/jsmith52/tq-selections/tq-selection-'+name+'.nc',) 
field_titles = ('ozone radiative feedback', 'radiative heating', 'ice microphysics', 'cirrus spreading rate', 'convection', 'ice optics', 'q vertical advection - interpolation','theta vertical advection conservation')
tropic_lats = iris.Constraint(latitude = lambda l: -10<=l<=10) # constrains loaded data to the tropical latitudes -10deg to +10deg

# ANALYSIS
    # Collapsing data to average over selected regions
def collaps(cube, yr0):
    cube_zonal = cube.collapsed('longitude', iris.analysis.MEAN) # zonal mean
    cube_trop_zonal = cube_zonal.collapsed('latitude', iris.analysis.MEAN) # mean over the tropics
    cube_final = cube_trop_zonal.extract(iris.Constraint(Pressure=100)) # Select the pressure level (100hPa for q)
    cube_final_t = cube_final[yr0] # Selecting time region
    return cube_final_t

q_mean = [] # Location for saved data during looping for annual mean in q each comparison
q_season = [] # Location for saved data during looping for seasonal cycle amplitude in q in each comparison
w_mean = [] # Location for saved for data during looping for annual mean in w in each comparison
w_season = [] # Location for saved data during looping for seasonal cycle amplitude in w in each comparison
for i in range(len(filenames1)): # Loop over all comparison runs
    # Load cubes specifically for q in tropics
    if os.path.isfile(filenames1[i]) == False: print("Error: An experiment ID not found."); continue # Check files exist
    if os.path.isfile(filenames2[i]) == False: print("Error: An experiment ID not found."); continue
    cube1= iris.load(filenames1[i], variable & tropic_lats)
    cube2= iris.load(filenames2[i], variable & tropic_lats)
    cube3= iris.load(filenames1[i], 'upward_air_velocity' & tropic_lats)
    cube4= iris.load(filenames2[i], 'upward_air_velocity' & tropic_lats)
    q1= cube1[0]
    q2= cube2[0]
    w1= cube3[0]
    w2= cube4[0]

    # Select the overlapping time periods
    time_coord1 = q1.coord('t')
    time_coord2 = q2.coord('t')
    t_range1 = (time_coord1.points >= time_coord2.points[0]) & (time_coord1.points <= time_coord2.points[-1])
    t_range2 = (time_coord2.points >= time_coord1.points[0]) & (time_coord2.points <= time_coord1.points[-1])
    q01 = q1[t_range1,:,:,:]
    q02 = q2[t_range2,:,:,:]
    w01 = w1[t_range1,:,:,:]
    w02 = w2[t_range2,:,:,:]
    #print('New time co-ordinate range is for set 1: /n',q01.coord('t'))
    #print('New time co-ordinate range is for set 2: /n',q02.coord('t'))
    ### Removing any dates that do not appear throughout the time series
    
    ###
   
    # Extracting region in time suitable for comparison
    ## Can modify so that script takes maximum number of 12-month periods from q_01.coord('t').points
    t_start = 1999 #input("Starting year? Expect 1999.")
    t_end = 2008 #input("Endingyear? Expect 2008.")
    yr0 = (q01.coord('t').points >= (t_start-1-1988)*360+120) & (q01.coord('t').points < (t_end-1988)*360+120)
    #print yr0
 
    # Collapsing data to average over selected regions
    q01_collapsed = collaps(q01, yr0)
    q02_collapsed = collaps(q02, yr0)
    w01_collapsed = collaps(w01, yr0)
    w02_collapsed = collaps(w02, yr0)

    # Calculating difference in annual mean for q or T
    q_final = q01_collapsed - q02_collapsed
    q_final_mean = q_final.collapsed('t', iris.analysis.MEAN)
    if variable == 'specific_humidity' : diff_mean = q_final_mean.data.item()*1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv, and converting from 0d array to scalar
    if variable == 'air_temperature' : diff_mean = q_final_mean.data.item() # converting from 0d array to scalar 
    print "Difference in annual mean is: ",diff_mean
    q_mean.append(diff_mean) 
   
    # Calculating difference in annual mean for w
    w_final = w01_collapsed - w02_collapsed
    w_final_mean = w_final.collapsed('t', iris.analysis.MEAN)
    wiff_mean = w_final_mean.data.item()
    print "Difference in annual mean for w is: ",wiff_mean
    w_mean.append(wiff_mean) 

    # Calculation of difference in seasonal cycle amplitude
    # Forming the climatological mean for t_start to t_end
    seasonal_cycle=[]
    for cube in [q01_collapsed,q02_collapsed,w01_collapsed,w02_collapsed]:
        # Finding amplitude of seasonal cycle
        iris.coord_categorisation.add_month(cube, 't', name='climatological months')
        #print cube_diff
        climatological_mean = cube.aggregated_by(['climatological months'], iris.analysis.MEAN)
        #print repr(climatological_mean)
        #climatological_mean.coord('climatological months')
        seasonal_cycle.append(max(climatological_mean.data)- min(climatological_mean.data))
    # Taking difference in seasonal cycle
    q_diff_in_seasonal_cycle = (seasonal_cycle[0]-seasonal_cycle[1])
    w_diff_in_seasonal_cycle = (seasonal_cycle[2]-seasonal_cycle[3])
    if variable == 'specific_humidity': q_diff_in_seasonal_cycle *= 1.608e6        # 1.608e6 is the units conversion from kg.kg^-1 to ppmv)
    print "Difference in seasonal cycle for q is: ", q_diff_in_seasonal_cycle
    q_season.append(q_diff_in_seasonal_cycle) 
    print "Difference in seasonal cycle for w is: ", w_diff_in_seasonal_cycle
    w_season.append(w_diff_in_seasonal_cycle) 

print q_mean
print q_season
print w_mean
print w_season

# PLOTTING

# Plot options from (1-4)
# 1) Plotting of q_mean against q_season
# plt.plot(q_mean[0],q_season[0], 'ro',q_mean[1],q_season[1], 'bo',q_mean[2],q_season[2], 'go',q_mean[3],q_season[3], 'co',q_mean[4],q_season[4], 'mo',q_mean[5],q_season[5], 'yo',q_mean[6],q_season[6], 'ko' )
# 2) Plotting of q_mean against w_mean
# plt.plot(q_mean[0],w_mean[0], 'ro',q_mean[1],w_mean[1], 'bo',q_mean[2],w_mean[2], 'go',q_mean[3],w_mean[3], 'co',q_mean[4],w_mean[4], 'mo',q_mean[5],w_mean[5], 'yo',q_mean[6],w_mean[6], 'ko' )
# 3) Plotting of q_season against w_season
#plt.plot(q_season[0],w_season[0], 'ro',q_season[1],w_season[1], 'bo',q_season[2],w_season[2], 'go',q_season[3],w_season[3], 'co',q_season[4],w_season[4], 'mo',q_season[5],w_season[5], 'yo',q_season[6],w_season[6], 'ko' )
# 4) Plotting of q_mean against w_season
plt.plot(q_mean[0],w_season[0], 'ro',q_mean[1],w_season[1], 'bo',q_mean[2],w_season[2], 'go',q_mean[3],w_season[3], 'co',q_mean[4],w_season[4], 'mo',q_mean[5],w_season[5], 'yo',q_mean[6],w_season[6], 'ko' )
#if variable == 'specific_humidity': plt.legend(field_titles, loc=2) #1) #2)
if variable == 'specific_humidity': plt.legend(field_titles, loc=3) #3) #4)
if variable == 'air_temperature': plt.legend(field_titles, loc=3)
#m, b = np.polyfit(q_mean, q_season, 1)  #1)
#pearR = np.corrcoef(q_mean, q_season)[1,0] #1)
#m, b = np.polyfit(q_mean, w_mean, 1) #2)
#pearR = np.corrcoef(q_mean, w_mean)[1,0] #2)
#m, b = np.polyfit(q_season, w_season, 1) #3)
#pearR = np.corrcoef(q_season, w_season)[1,0] #3)
m, b = np.polyfit(q_mean, w_season, 1) #4)
pearR = np.corrcoef(q_mean, w_season)[1,0] #4)
plt.plot(q_mean, [(m*x + b) for x in q_mean], '-')
plt.figtext(0.6, 0.2,"Correlation R = "+'{:4.2f}'.format(pearR))
if variable == 'air_temperature':
    plt.title('air_temperature')
    plt.xlabel("difference to T_annual_mean (C)") #1) #2) #4)
#    plt.xlabel("difference to T_season (C)") #3)
#    plt.ylabel("difference to T_season (C)") #1)
#    plt.ylabel("difference to w_annual_mean (units?)") #2)
    plt.ylabel("difference to w_season (units?)") #3) #4)
if variable == 'specific_humidity':
    plt.title('water vapour concentration')
    plt.xlabel("difference to q_annual_mean (ppmv)") #1) #2) #4)
#    plt.xlabel("difference to q_season (ppmv)") #3)
#    plt.ylabel("difference to q_season (ppmv") #1)
#    plt.ylabel("difference to w_annual_mean (units?)") #2)
    plt.ylabel("difference to w_season (units?)") #3) #4)
plt.show()

# then compare the results to those in Met Office plots

