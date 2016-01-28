### Note, look for ### for comments on what work needs to be continued.

import iris
import iris.analysis
import iris.coords
import iris.coord_categorisation
import matplotlib.pyplot as plt
import numpy as np
import os.path

    # Function for collapsing data to average over selected regions
def collaps(cube, latlim, press, yr0):
    cube_zonal = cube.collapsed('longitude', iris.analysis.MEAN) # zonal mean
    cube_tropics_zonal = cube_zonal.extract(iris.Constraint(latitude = lambda l: -latlim<=l<=latlim)) # constrains data to the tropical latitudes -10deg to +10deg
    cube_trop_zonal = cube_tropics_zonal.collapsed('latitude', iris.analysis.MEAN) # meridional mean over the tropics
    cube_final = cube_trop_zonal.extract(iris.Constraint(Pressure=press)) # Select the pressure level
    cube_final_t = cube_final[yr0] # Select the time region
    return cube_final_t

def climatological_mean(cube):
    climatological_month_data=[]
    print "Climatological month calculation data"
    iris.coord_categorisation.add_month(cube, 't', name='climatological_months')
    #print "Added climatological month coord to cube:\n\n",cube
    #print cube.coord('climatological_months').points
    Janpoints = []
    Janslice = cube.extract(iris.Constraint(climatological_months='Jan')) 
    #for i in cube.coord('climatological_months').points[:] == 'Jan': Janpoints += [cube.coord('climatological_months').data]
    #print "Cube containing only January data is", Janslice
    #print "All months assigned to January have values of: \n", Janslice.data
    Marpoints = []
    Marslice = cube.extract(iris.Constraint(climatological_months='Mar'))
    #print "Cube containing only March data is", Marslice
    #print "All months assigned to March have values of: \n", Marslice.data
    climatological_mean = cube.aggregated_by(['climatological_months'], iris.analysis.MEAN)
    #print "Created cube based on climatological months:\n\n", climatological_mean
    #print climatological_mean.coord('climatological_months').points
    #print "This cube's type is ", type(climatological_mean)
    #print repr(climatological_mean)
    #climatological_mean.coord('climatological months')
    seasonal_cycle_amplitude = max(climatological_mean.data)- min(climatological_mean.data)
    #print seasonal_cycle_amplitude
    #print type(seasonal_cycle_amplitude[0])
    print "Finished climatological calculation"
    return climatological_mean, seasonal_cycle_amplitude

def load_and_analyse():
    # Function to load in data and produce fields for monthly means, annual means, and seasonal cycle amplitude for each filename supplied
    filenames1 = () # Define the two sets of filenames to work with
    filenames2 = ()
    variables = ['specific_humidity','air_temperature', 'upward_air_velocity']
    variable1 = raw_input(["Which two variable to use?", variables, "(please type explicitly and press enter after each)"])
    variable2 = raw_input(["And the second variable is?"])
    calc_type = input(["Do you want to calculate 1) differences from baseline, or 2)absolute values? (type 1 or 2)"])    
    while calc_type not in [1,2]: calc_type = input(["Not recognised, try again. Do you want to calculate 1) differences from baseline, or 2)absolute values? (type 1 or 2)"])  
    press1 = input(["What pressure level (hPa) to select for "+variable1+"? (options are 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 20, 10)"])
    press2 = input(["What pressure level (hPa) to select for "+variable2+"? (options are the same)"])
    latlim = input(["what latitude limit do you want to take for the tropical meridional mean?  (symmetrical in degrees e.g Type 10 to get mean over 10N to 10S.)"])
    if latlim < 0: latlim = input(["Not recognised, try again, enter a number >= 0"])
    
    if calc_type == 1:
        for name in ['anmxa', 'antie', 'dkwyj', 'antie', 'antie', 'antie', 'antie', 'antie', 'aojeb']: filenames2 += ('/group_workspaces/jasmin2/ukca/vol1/jsmith52/tq-selections/tq-selection-'+name+'.nc',)
        for name in ['dkwyj', 'dlvpd', 'dkytg', 'antng', 'anxal', 'dlkxi', 'dlhbk', 'anvti', 'aojed']: filenames1 += ('/group_workspaces/jasmin2/ukca/vol1/jsmith52/tq-selections/tq-selection-'+name+'.nc',) 
        field_titles = ('theta vertical advection - interpolation', 'theta vertical advection - conservation', 'q vertical advection - interpolation', 'radiative heating', 'ice optics','ice microphysics', 'convection','cirrus spreading rate', 'ozone radiative feedback')
    elif calc_type == 2:
        for name in ['anmxa', 'aojeb', 'antie', 'dkwyj', 'dlvpd', 'dkytg', 'antng', 'anxal', 'dlkxi', 'dlhbk', 'anvti', 'aojed']: filenames1 += ('/group_workspaces/jasmin2/ukca/vol1/jsmith52/tq-selections/tq-selection-'+name+'.nc',) 
        filenames2 = filenames1  
        field_titles = ('baseline1 (for theta vert. advect. interp.)', 'baseline3 (for ozone radiatibve feedback)', 'baseline2 (for the rest)', 'theta vertical advection - interpolation', 'theta vertical advection - conservation', 'q vertical advection - interpolation', 'radiative heating', 'ice optics','ice microphysics', 'convection','cirrus spreading rate', 'ozone radiative feedback')
        
    # ANALYSIS
    hum_ratio = iris.coords.AuxCoord(1.608E6, long_name='Unit conversion from specific humidity to relative humidity by volume', units ='ppmv/kg.kg^-1')
    
    cube1_mean = [] # Locations for saving data during looping
    cube1_season = [] 
    cube1_months = []
    cube1_climatological_months = []
    cube3_mean = [] 
    cube3_season = []
    cube3_months = []
    cube3_climatological_months = []
    
    if calc_type == 1:
        for i in range(len(filenames1)): # Loop over all comparison runs
            print "Calculating for ", field_titles[i]
            print "Loading cubes"
            if os.path.isfile(filenames1[i]) == False: print("Error: An experiment ID not found."); continue # Check files exist
            if os.path.isfile(filenames2[i]) == False: print("Error: An experiment ID not found."); continue
            cube1= iris.load_cube(filenames1[i], variable1)
            cube2= iris.load_cube(filenames2[i], variable1)
            cube3= iris.load_cube(filenames1[i], variable2)
            cube4= iris.load_cube(filenames2[i], variable2)
            #print "Cube1 is ", cube1
            #print cube1.coord('Pressure').points      

            print "Selecting the overlapping time periods"
            time_coord1 = cube1.coord('t')
            time_coord2 = cube2.coord('t')
            t_range1 = (time_coord1.points >= time_coord2.points[0]) & (time_coord1.points <= time_coord2.points[-1])
            t_range2 = (time_coord2.points >= time_coord1.points[0]) & (time_coord2.points <= time_coord1.points[-1])
            cube01 = cube1[t_range1,:,:,:]
            cube02 = cube2[t_range2,:,:,:]
            cube03 = cube3[t_range1,:,:,:]
            cube04 = cube4[t_range2,:,:,:]
            #print 'New time co-ordinate range is for set 1: /n',cube01.coord('t')
            #print 'New time co-ordinate range is for set 2: /n',cube02.coord('t')
            
            print "Calculating region in time suitable for comparison"
            ## Can modify so that script takes maximum number of 12-month periods from cube_01.coord('t').points
            t_start = 1999 #input("Starting year? Expect 1999.")
            t_end = 2008 #input("Endingyear? Expect 2008.")
            yr0 = (cube01.coord('t').points >= (t_start-1-1988)*360+120) & (cube01.coord('t').points < (t_end-1988)*360+120)
            #print yr0      

            ### Error-checking or Removing any dates that do not appear throughout the time series OR adding the missing months to the dataset
            for cube in [cube01,cube02,cube03,cube04]:    # upward_air_velocity can give a unit mismatch between the two input files. This crudely matches.
                if cube.units == "unknown": cube.units = 1
            ###
     
            print "Collapsing data to average over selected regions"
            cube01_collapsed = collaps(cube01, latlim, press1, yr0)
            cube02_collapsed = collaps(cube02, latlim, press1, yr0)
            cube3_collapsed = collaps(cube03, latlim, press2, yr0)
            cube4_collapsed = collaps(cube04, latlim, press2, yr0)
            if variable1 == 'specific_humidity' :
                cube01_collapsed = cube01_collapsed*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                cube01_collapsed.rename('relative_humidity')
                cube02_collapsed = cube02_collapsed*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                cube02_collapsed.rename('relative_humidity')
            if variable2 == 'specific_humidity' :
                cube3_collapsed = cube3_collapsed*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                cube3_collapsed.rename('relative_humidity')
                cube4_collapsed = cube4_collapsed*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                cube4_collapsed.rename('relative_humidity')
            
            print "Taking difference between data to be compared"
            cube1_final = cube01_collapsed - cube02_collapsed
            cube3_final = cube3_collapsed - cube4_collapsed
            
            print "Calculating monthly mean data"
            cube1_month_mean = cube1_final 
            #print "Difference in monthly mean for", variable1, "is: ",cube1_month_mean
            cube1_months.append(cube1_month_mean) 
            cube3_month_mean = cube3_final 
            #print "Difference in monthly mean for", variable2, "is: ",cube3_month_mean
            cube3_months.append(cube3_month_mean) 
        
            print "Calculating annual mean data"
            cube1_final_mean = cube1_final.collapsed('t', iris.analysis.MEAN)
            cube1_diff_mean = cube1_final_mean.data.item()
            print "Difference in annual mean for", variable1, "is: ",cube1_diff_mean
            cube1_mean.append(cube1_diff_mean) 
            cube3_final_mean = cube3_final.collapsed('t', iris.analysis.MEAN)
            wiff_mean = cube3_final_mean.data.item()
            print "Difference in annual mean for",variable2, " is: ",wiff_mean
            cube3_mean.append(wiff_mean)        

            print "Calculating seasonal cycle amplitudes and climatological months"
            # Forming the climatological mean for t_start to t_end
            seasonal_cycle=[]
            climatological_month_data=[]
            for cube in [cube01_collapsed,cube02_collapsed,cube3_collapsed,cube4_collapsed]:
                (cmd, sca) = climatological_mean(cube)
                climatological_month_data.append(cmd)
                #print sca
                #print type(sca)
                seasonal_cycle.append(sca)
                #print "Seasonal cycle is", seasonal_cycle
                #print "After calling the function, the climatological month cube is \n\n", cmd 
                #print "and its type is ", type(cmd )
                #print "The list of climatological month cubes is \n\n", climatological_month_data
                #print "and its type is ", type(climatological_month_data)
            # Taking difference in seasonal cycle
            #print "sca is ", seasonal_cycle 
            #print "cmd is ", climatological_month_data
            cube1_diff_in_seasonal_cycle = (seasonal_cycle[0]-seasonal_cycle[1])
            cube3_diff_in_seasonal_cycle = (seasonal_cycle[2]-seasonal_cycle[3])
            cube1_diff_climatological_months = climatological_month_data[0] - climatological_month_data[1]
            #print "differencing the climatological months int he first comparison gives: \n", cube1_diff_climatological_months
            cube3_diff_climatological_months = climatological_month_data[2] - climatological_month_data[3]  
            print "Difference in seasonal cycle for ",variable1,"is: ", cube1_diff_in_seasonal_cycle
            cube1_season.append(cube1_diff_in_seasonal_cycle)
            cube1_climatological_months.append(cube1_diff_climatological_months)
            print "Difference in seasonal cycle for ",variable2,"is: ", cube3_diff_in_seasonal_cycle
            cube3_season.append(cube3_diff_in_seasonal_cycle) 
            cube3_climatological_months.append(cube3_diff_climatological_months)
            print "End this loop OK"    

    elif calc_type ==2:
        for i in range(len(filenames1)): # Loop over all comparison runs
            print "Calculating for ", field_titles[i]
            print "Loading cubes"
            cube1= iris.load_cube(filenames1[i], variable1)
            cube3= iris.load_cube(filenames1[i], variable2)

            print "Calculating region in time suitable for comparison"
            ## Can modify so that script takes maximum number of 12-month periods from cube1_01.coord('t').points
            t_start = 1999 #input("Starting year? Expect 1999.")
            t_end = 2008 #input("Endingyear? Expect 2008.")
            yr0 = (cube1.coord('t').points >= (t_start-1-1988)*360+120) & (cube1.coord('t').points < (t_end-1988)*360+120)
            #print yr0
            
            print "Collapsing data to average over selected regions"
            cube1_collapsed = collaps(cube1, latlim, press1, yr0)
            cube3_collapsed = collaps(cube3, latlim, press2, yr0)
            if variable1 == 'specific_humidity' : # Converting mixing ratio from 'per unit mass' to 'per unit volume'
                cube1_collapsed = cube1_collapsed*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                cube1_collapsed.rename('relative_humidity')
            if variable2 == 'specific_humidity' : 
                cube3_collapsed = cube3_collapsed*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                cube3_collapsed.rename('relative_humidity')
            
            print "Calculating monthly means"
            cube1_month_mean = cube1_collapsed 
            cube1_months.append(cube1_month_mean) 
            cube3_month_mean = cube3_collapsed 
            cube3_months.append(cube3_month_mean) 

            print "Calculating annual means"
            cube1_annual = cube1_collapsed.collapsed('t', iris.analysis.MEAN)
            cube1_diff_mean = cube1_annual.data.item()
            print "Annual mean for", variable1, "is: ",cube1_diff_mean
            cube1_mean.append(cube1_diff_mean) 
            cube3_annual = cube3_collapsed.collapsed('t', iris.analysis.MEAN)
            cube3_diff_mean = cube3_annual.data.item()
            print "Annual mean for",variable2, " is: ", cube3_diff_mean
            cube3_mean.append(cube3_diff_mean)

            print "Calculation of seasonal cycle amplitude"
            # Forming the climatological mean for t_start to t_end
            seasonal_cycle=[]
            climatological_month_data=[]
            for cube in [cube1_collapsed,cube3_collapsed]:
                (cmd, sca) = climatological_mean(cube)
                climatological_month_data.append(cmd)
                #print sca
                #print type(sca)
                seasonal_cycle.append(sca)
                #print "Seasonal cycle is", seasonal_cycle
                #print "After calling the function, the climatological month cube is \n\n", cmd 
                #print "and its type is ", type(cmd )
                #print "The list of climatological month cubes is \n\n", climatological_month_data
                #print "and its type is ", type(climatological_month_data)
            # Taking difference in seasonal cycle
            #print "sca is ", seasonal_cycle 
            #print "cmd is ", climatological_month_data
            print "Seasonal cycle for ",variable1,"is: ", seasonal_cycle[0]
            cube1_season.append(seasonal_cycle[0])
            cube1_climatological_months.append(climatological_month_data[0])
            print "Seasonal cycle for ",variable2,"is: ", seasonal_cycle[1]
            cube3_season.append(seasonal_cycle[1]) 
            cube3_climatological_months.append(climatological_month_data[1])
            
            print "End this loop OK"

    print "All loops finished OK. Results outputs are:"
    print "cube1_mean\n", cube1_mean
    print "cube1_season\n", cube1_season
    print "cube1_months\n", cube1_months
    print "cube1_climatological_months\n", cube1_climatological_months
    print "cube3_mean\n", cube3_mean
    print "cube3_season\n", cube3_season
    print "cube3_months\n", cube3_months
    print "cube3_climatological_months\n", cube3_climatological_months
    return(variable1, variable2, cube1_mean, cube1_season, cube1_months, cube3_mean, cube3_season, cube3_months, cube1_climatological_months, cube3_climatological_months, field_titles, press1, press2)

def plotting(variable1, variable2, cube1_mean, cube1_season, cube1_months, cube3_mean, cube3_season, cube3_months, cube1_climatological_months, cube3_climatological_months, field_titles, press1, press2):
    print "PLOTTING"

    # Plot options from (1-4), switch the comments so that the preferred one is active
    response = input("What do you want to plot for "+variable1+" and "+variable2+"?\n 1) annual mean vs. annual mean\n 2) annual mean vs. amplitude of seasonal cycle\n 3) amplitude of seasonal cycle vs. annual mean\n 4) amplitude of seasonal cycle vs. amplitude of seasonal cycle\n 5) Monthly data vs. monthly data \n 6) Climatological months vs. climatological months\n Please type 1, 2, 3, 4, 5, or 6.")
    if response == 1:
        x = cube1_mean
        y = cube3_mean
        xname = "annual mean"
        yname = "annual mean"
    elif response == 2:
        x = cube1_mean
        y = cube3_season
        xname = "annual mean"
        yname = "amplitude of seasonal cycle"
    elif response == 3:
        x = cube1_season
        y = cube1_mean
        xname = "amplitude of seasonal cycle"
        yname = "annual mean"
    elif response == 4:
        x = cube1_season
        y = cube3_season
        xname = "amplitude of seasonal cycle"
        yname = "amplitude of seasonal cycle"
    elif response == 5:
        lag_steps = input("How many months (timesteps) of lag do you want? Please type 0, 1, 2 or 3 etc.")
        x = cube1_months
        y = cube3_months
        xname = "monthly mean"
        if lag_steps is not 0: yname = "monthly mean (lagged)"
        else: yname = "monthly mean"
    elif response == 6:
        lag_steps = input("How many months (timesteps) of lag do you want? Please type 0, 1, 2 or 3 etc.")
        x = cube1_climatological_months
        y = cube3_climatological_months
        xname = "climatological months"
        if lag_steps is not 0: yname = "climatological months(lagged)"
        else: yname = "climatological months"
    else: print "Cannot plot"
    
    plt.gca().set_color_cycle(['limegreen', 'green','deepskyblue', 'yellow', 'magenta', 'darkviolet','darkorange','darkgrey','blue'])
 
    if response in (1, 2, 3, 4):
        # Plot
        plt.plot(x[0], y[0], 'o', x[1], y[1], 'o',x[2], y[2], 'o', x[3], y[3], 'o', x[4], y[4], 'o', x[5], y[5], 'o', x[6], y[6], 'o', x[7], y[7], 'o', x[8], y[8], 'o', markersize=16)
        plt.plot(0, 0, 'k+', ms=50)
        # Regression line
        m, b = np.polyfit(x, y, 1)
        pearR = np.corrcoef(x, y)[1,0]
        plt.plot(x, [(m*x1 + b) for x1 in x], '-')
        plt.figtext(0.6, 0.25, "Correlation R = "+'{:4.2f}'.format(pearR))
        plt.title(variable1+"("+str(press1)+"hPa) against "+variable2+" ("+str(press2)+"hPa)")

    elif response is 5:
        # Plot
        if lag_steps == 0: 
            for j in range(len(x)): plt.plot(x[j].data[:],y[j].data[:], 'o', markersize=6)
        else: 
            for j in range(len(x)): 
                plt.plot(x[j].data[:-1*lag_steps],y[j].data[lag_steps:], 'o', markersize=6)
        # Regression lines
        m =[0]*len(x)
        b = [0]*len(x)
        pearR = [0]*len(x)
        plot_levels = []
        plot_levels += [i*0.029 for i in range(1+len(x))]
        plt.figtext(0.45, 0.88-plot_levels[0],"Correlation R =    and slope of fitted line m =")
        for j in range(len(x)):
            if lag_steps == 0:
                 m[j], b[j] = np.polyfit(x[j].data,y[j].data, 1)
                 pearR[j] = np.corrcoef(x[j].data,y[j].data)[1,0]           
            else:
                 m[j], b[j] = np.polyfit(x[j].data[:-1*lag_steps],y[j].data[lag_steps:], 1)
                 pearR[j] = np.corrcoef(x[j].data[:-1*lag_steps],y[j].data[lag_steps:])[1,0]         
            plt.plot(x[j].data, [(m[j]*x1 + b[j]) for x1 in x[j].data], '-', linewidth=2)
            plt.figtext(0.45, 0.88-plot_levels[j+1],"R = "+'{:4.2f}'.format(pearR[j])+"             m = "+'{:.1E}'.format(m[j]))
        plt.title(variable1+"("+str(press1)+"hPa) against "+variable2+" ("+str(press2)+"hPa)"+"with time lag of "+str(lag_steps)+"months")    
    elif response is 6:
        # Plot
        if lag_steps == 0: 
            for j in range(len(x)): plt.plot(x[j].data[:],y[j].data[:], 'o', markersize=6)
        else: 
            #jmoded = range(len(x))
            #jmoded = jmod[lag_steps:] + jmod[:lag_steps]
            ymod = [0]*len(x)
            for j in range(len(x)):
               #y[j] = y[j].data[lag_steps:] + y[j].data[:lag_steps]
               ymod[j] = []
               ymod[j].extend(y[j][lag_steps:].data)
               ymod[j].extend(y[j][:lag_steps].data)
               print "ymod is\n", ymod
               print "y is \n", y[j][:].data
               plt.plot(x[j].data[:],ymod[j][:], 'o', markersize=6)
        # Regression lines
        # Defining variables
        m =[0]*len(x)
        b = [0]*len(x)
        pearR = [0]*len(x)
        plot_levels = []
        plot_levels += [i*0.029 for i in range(1+len(x))] #for spacing of figtext
        plt.figtext(0.45, 0.88-plot_levels[0],"Correlation R =    and slope of fitted line m =")
        for j in range(len(x)):
            if lag_steps == 0:
                 m[j], b[j] = np.polyfit(x[j].data,y[j].data, 1)
                 pearR[j] = np.corrcoef(x[j].data,y[j].data)[1,0]           
            else:
                 m[j], b[j] = np.polyfit(x[j].data,ymod[j], 1)
                 pearR[j] = np.corrcoef(x[j].data,ymod[j])[1,0]         
            plt.plot(x[j].data, [(m[j]*x1 + b[j]) for x1 in x[j].data], '-', linewidth=2)
            plt.figtext(0.45, 0.88-plot_levels[j+1],"R = "+'{:4.2f}'.format(pearR[j])+"             m = "+'{:.1E}'.format(m[j]))
        plt.title(variable1+"("+str(press1)+"hPa) against "+variable2+" ("+str(press2)+"hPa)"+"with time lag of "+str(lag_steps)+"months")    
    if m >= -0.1:  plt.legend(field_titles, loc=2)
    else: plt.legend(field_titles, loc=3)
    if calc_type == 1:
        comment = "Difference to "
    elif calc_type == 2:
        comment = ""
    if variable1 == 'air_temperature': plt.xlabel(comment, "T"+xname+" (C)")
    if variable1 == 'specific_humidity': plt.xlabel(comment, "cube1 "+xname+"(ppmv)")
    if variable1 == 'upward_air_velocity': plt.xlabel(comment, " w"+xname+" (units unknown)")
    if variable2 == 'specific_humidity': plt.ylabel(comment, " cube1 "+yname+" (ppmv)")
    if variable2 == 'air_temperature': plt.ylabel(comment, " T "+yname+" (C)")
    if variable2 == 'upward_air_velocity': plt.ylabel(comment, " w "+yname+" (units unknown)")

    plt.show()
    return()
    # then compare the results to those in Met Office plots
