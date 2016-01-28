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
    run_monthly_means = raw_input("Do you want to output dataset for monthly mean values? (y/n)")

    q_mean = [] # Location for saved data during looping for annual mean in q each comparison
    q_season = [] # Location for saved data during looping for seasonal cycle amplitude in q in each comparison
    q_months = []
    q_climatological_months = []
    w_mean = [] # Location for saved for data during looping for annual mean in w in each comparison
    w_season = [] # Location for saved data during looping for seasonal cycle amplitude in w in each comparison
    w_months = []
    w_climatological_months = []
    
    if calc_type ==2:
        for i in range(len(filenames1)): # Loop over all comparison runs
            print "Calculating for ", field_titles[i]
            print "Loading cubes"
            cube1= iris.load_cube(filenames1[i], variable1)
            cube3= iris.load_cube(filenames1[i], variable2)

            print "Calculating region in time suitable for comparison"
            ## Can modify so that script takes maximum number of 12-month periods from q_01.coord('t').points
            t_start = 1999 #input("Starting year? Expect 1999.")
            t_end = 2008 #input("Endingyear? Expect 2008.")
            yr0 = (cube1.coord('t').points >= (t_start-1-1988)*360+120) & (cube1.coord('t').points < (t_end-1988)*360+120)
            #print yr0
            
            print "Collapsing data to average over selected regions"
            cube1_collapsed = collaps(cube1, latlim, press1, yr0)
            cube3_collapsed = collaps(cube3, latlim, press2, yr0)
            
            print "Calculating monthly means (###this needs modifying to agree with cube1 and cube 3 instead of q"
            if run_monthly_means == "y":
                if variable1 == 'specific_humidity' :
                    q_month_mean = q_final*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                    q_month_mean.rename('relative_humidity')
                if variable1 == 'air_temperature' : 
                    q_month_mean = q_final 
                    q_month_mean.rename('air_temperature')
                if variable1 == 'upward_air_velocity': 
                    q_month_mean = q_final
                    q_month_mean.rename('upward_air_velocity')

            print "Calculating differences in annual mean (###this needs modifying to agree with cube1 instead of q)"
            q_final_mean = q_final.collapsed('t', iris.analysis.MEAN)
            if variable1== 'specific_humidity' : q_diff_mean = q_final_mean.data.item()*1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv, and converting from 0d array to scalar
            if variable1 == 'air_temperature' : q_diff_mean = q_final_mean.data.item() # converting from 0d array to scalar 
            if variable1 == 'upward_air_velocity': q_diff_mean = q_final_mean.data.item()
            print "Difference in annual mean for", variable1, "is: ",q_diff_mean
            q_mean.append(q_diff_mean) 

            print "Calculation of difference in seasonal cycle amplitude (###need to fill in this bit)"
            
            print "End this loop OK


    if calc_type == 1:
        for i in range(len(filenames1)): # Loop over all comparison runs
            print "Calculating for ", field_titles[i]
            print "Loading cubes"
            if os.path.isfile(filenames1[i]) == False: print("Error: An experiment ID not found."); continue # Check files exist
            if os.path.isfile(filenames2[i]) == False: print("Error: An experiment ID not found."); continue
            q1= iris.load_cube(filenames1[i], variable1)
            q2= iris.load_cube(filenames2[i], variable1)
            w1= iris.load_cube(filenames1[i], variable2)
            w2= iris.load_cube(filenames2[i], variable2)
            #print "Cube1 is ", cube1
            #print q1.coord('Pressure').points      

            print "Selecting the overlapping time periods"
            time_coord1 = q1.coord('t')
            time_coord2 = q2.coord('t')
            t_range1 = (time_coord1.points >= time_coord2.points[0]) & (time_coord1.points <= time_coord2.points[-1])
            t_range2 = (time_coord2.points >= time_coord1.points[0]) & (time_coord2.points <= time_coord1.points[-1])
            q01 = q1[t_range1,:,:,:]
            q02 = q2[t_range2,:,:,:]
            w01 = w1[t_range1,:,:,:]
            w02 = w2[t_range2,:,:,:]
            print 'New time co-ordinate range is for set 1: /n',q01.coord('t')
            print 'New time co-ordinate range is for set 2: /n',q02.coord('t')
            
            print "Calculating region in time suitable for comparison"
            ## Can modify so that script takes maximum number of 12-month periods from q_01.coord('t').points
            t_start = 1999 #input("Starting year? Expect 1999.")
            t_end = 2008 #input("Endingyear? Expect 2008.")
            yr0 = (q01.coord('t').points >= (t_start-1-1988)*360+120) & (q01.coord('t').points < (t_end-1988)*360+120)
            #print yr0      

            ### Error-checking or Removing any dates that do not appear throughout the time series OR adding the missing months to the dataset
            for cube in [q01,q02,w01,w02]:    # upward_air_velocity can give a unit mismatch between the two input files. This crudely matches.
                if cube.units == "unknown": cube.units = 1
            ###
     
            print "Collapsing data to average over selected regions"
            q01_collapsed = collaps(q01, latlim, press1, yr0)
            q02_collapsed = collaps(q02, latlim, press1, yr0)
            w01_collapsed = collaps(w01, latlim, press2, yr0)
            w02_collapsed = collaps(w02, latlim, press2, yr0)
        
            print "Taking difference between data to be compared"
            q_final = q01_collapsed - q02_collapsed
            w_final = w01_collapsed - w02_collapsed
            
            print "Calculating monthly mean data"
            if run_monthly_means == "y":
                if variable1 == 'specific_humidity' :
                    q_month_mean = q_final*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                    q_month_mean.rename('relative_humidity')
                if variable1 == 'air_temperature' : 
                    q_month_mean = q_final 
                    q_month_mean.rename('air_temperature')
                if variable1 == 'upward_air_velocity': 
                    q_month_mean = q_final
                    q_month_mean.rename('upward_air_velocity')
                #print "Difference in monthly mean for", variable1, "is: ",q_month_mean
                q_months.append(q_month_mean) 
                if variable2 == 'specific_humidity' : 
                    w_month_mean = w_final*hum_ratio # hum_ratio is units conversion from kg.kg^-1 to ppmv
                    w_month_mean.rename('relative_humidity')
                if variable2 == 'air_temperature' : 
                    w_month_mean = w_final 
                    w_month_mean.rename('air_temperature')
                if variable2 == 'upward_air_velocity': 
                    w_month_mean = w_final
                    w_month_mean.rename('upward_air_velocity')
                #print "Difference in monthly mean for", variable2, "is: ",w_month_mean
                w_months.append(w_month_mean) 
        
            print "Calculating differences in annual mean"
            q_final_mean = q_final.collapsed('t', iris.analysis.MEAN)
            if variable1== 'specific_humidity' : q_diff_mean = q_final_mean.data.item()*1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv, and converting from 0d array to scalar
            if variable1 == 'air_temperature' : q_diff_mean = q_final_mean.data.item() # converting from 0d array to scalar 
            if variable1 == 'upward_air_velocity': q_diff_mean = q_final_mean.data.item()
            print "Difference in annual mean for", variable1, "is: ",q_diff_mean
            q_mean.append(q_diff_mean) 
            w_final_mean = w_final.collapsed('t', iris.analysis.MEAN)
            if variable2 == 'specific_humidity' : wiff_mean = w_final_mean.data.item()*1.608e6 # 1.608e6 is the units conversion from kg.kg^-1 to ppmv, and converting from 0d array to scalar
            if variable2 == 'air_temperature' : wiff_mean = w_final_mean.data.item() # converting from 0d array to scalar 
            if variable2 == 'upward_air_velocity': wiff_mean = w_final_mean.data.item()
            print "Difference in annual mean for",variable2, " is: ",wiff_mean
            w_mean.append(wiff_mean)        

            print "Calculation of difference in seasonal cycle amplitude"
            # Forming the climatological mean for t_start to t_end
            seasonal_cycle=[]
            climatological_month_data=[]
              
            w_diff_climatological_months = []  
            for cube in [q01_collapsed,q02_collapsed,w01_collapsed,w02_collapsed]:
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
            q_diff_in_seasonal_cycle = (seasonal_cycle[0]-seasonal_cycle[1])
            w_diff_in_seasonal_cycle = (seasonal_cycle[2]-seasonal_cycle[3])
            q_diff_climatological_months = climatological_month_data[0] - climatological_month_data[1]
            #print "differencing the climatological months int he first comparison gives: \n", q_diff_climatological_months
            w_diff_climatological_months = climatological_month_data[2] - climatological_month_data[3]  
            if variable1 == 'specific_humidity': q_diff_in_seasonal_cycle *= 1.608e6        # 1.608e6 i s the units conversion from kg.kg^-1 to ppmv)
            if variable2 == 'specific_humidity': w_diff_in_seasonal_cycle *= 1.608e6        # 1.608e6 is the units conversion from kg.kg^-1 to ppmv)
            print "Difference in seasonal cycle for ",variable1,"is: ", q_diff_in_seasonal_cycle
            q_season.append(q_diff_in_seasonal_cycle)
            q_climatological_months.append(q_diff_climatological_months)
            print "Difference in seasonal cycle for ",variable2,"is: ", w_diff_in_seasonal_cycle
            w_season.append(w_diff_in_seasonal_cycle) 
            w_climatological_months.append(w_diff_climatological_months)
            print "End this loop OK"    

        print "All loops finished OK. Results outputs are:"
        print "q_mean\n", q_mean
        print "q_season\n", q_season
        print "q_months\n", q_months
        print "q_climatological_months\n", q_climatological_months
        print "w_mean\n", w_mean
        print "w_season\n", w_season
        print "w_months\n", w_months
        print "w_climatological_months\n", w_climatological_months
return(variable1, variable2, q_mean, q_season, q_months, w_mean, w_season, w_months, q_climatological_months, w_climatological_months, field_titles, press1, press2)

def plotting(variable1, variable2, q_mean, q_season, q_months, w_mean, w_season, w_months, q_climatological_months, w_climatological_months, field_titles, press1, press2):
    print "PLOTTING ###yet to be converted to absolute values"

    # Plot options from (1-4), switch the comments so that the preferred one is active
    response = input("What do you want to plot for "+variable1+" and "+variable2+"?\n 1) annual mean vs. annual mean\n 2) annual mean vs. amplitude of seasonal cycle\n 3) amplitude of seasonal cycle vs. annual mean\n 4) amplitude of seasonal cycle vs. amplitude of seasonal cycle\n 5) Monthly data vs. monthly data \n 6) Climatological months vs. climatological months\n Please type 1, 2, 3, 4, 5, or 6.")
    if response == 1:
        x = q_mean
        y = w_mean
        xname = "annual mean"
        yname = "annual mean"
    elif response == 2:
        x = q_mean
        y = w_season
        xname = "annual mean"
        yname = "amplitude of seasonal cycle"
    elif response == 3:
        x = q_season
        y = q_mean
        xname = "amplitude of seasonal cycle"
        yname = "annual mean"
    elif response == 4:
        x = q_season
        y = w_season
        xname = "amplitude of seasonal cycle"
        yname = "amplitude of seasonal cycle"
    elif response == 5:
        lag_steps = input("How many months (timesteps) of lag do you want? Please type 0, 1, 2 or 3 etc.")
        x = q_months
        y = w_months
        xname = "monthly mean"
        if lag_steps is not 0: yname = "monthly mean (lagged)"
        else: yname = "monthly mean"
    elif response == 6:
        lag_steps = input("How many months (timesteps) of lag do you want? Please type 0, 1, 2 or 3 etc.")
        x = q_climatological_months
        y = w_climatological_months
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
    if variable1 == 'air_temperature': plt.xlabel("difference to T"+xname+" (C)")
    if variable1 == 'specific_humidity': plt.xlabel("difference to q "+xname+"(ppmv)")
    if variable1 == 'upward_air_velocity': plt.xlabel("difference to w"+xname+" (units unknown)")
    if variable2 == 'specific_humidity': plt.ylabel("difference to q "+yname+" (ppmv)")
    if variable2 == 'air_temperature': plt.ylabel("difference to T "+yname+" (C)")
    if variable2 == 'upward_air_velocity': plt.ylabel("difference to w "+yname+" (units unknown)")

    plt.show()
    return()
    # then compare the results to those in Met Office plots
