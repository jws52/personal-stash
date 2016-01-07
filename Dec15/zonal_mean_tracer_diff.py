#/usr/bin/python
#************************************************************
# zonal mean of variable
# INPUT: Full 3D field
#************************************************************
import os
import datetime
localtime = datetime.datetime.now().strftime("%Y_%m_%d")

import netCDF4 as ncdf
import numpy as np

import pylab
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as clrs


import custom_colors as ccol

#************************************************************
# Set up
#************************************************************
disk     = '/scratch/ih280/netscratch/um/eval_paper/' # folder where the experiment data is
outdir   = '/home/ih280/Analysis/eval_paper/' # output folder for the plot
modnames = ['xgywu','xhtrj'] # experiment names
print       modnames[0]+'\n'
varnames = ['ch4+oh'] # your chosen variable name
field    = ['field34341'] # the name the variable has in the netcdf file
unit     = r'mol.cm-3.s-1'

# plot parameters
plotname = modnames[0]+'-'+modnames[1]+'_'+varnames[0]+'_contour.png'
xlab     = 'Latitude'
ylab     = 'Altitude / km'
clab     = u'\u0394 '+varnames[0]+r' / %'
llim     = -30    # shading limits
ulim     = 30
by       = 5
lclim    = -10    # contour limits
uclim    = 10
cby      = 1
lid      = 20   # y axis limit / km
yby      = 5
cdp      = 0
ylabs    = ["%.0f" % z for z in np.arange(0,lid+yby,yby)]
levs     = np.arange(llim,ulim+by,by)
clevs    = np.arange(lclim,uclim+by,cby)
cols1    = ccol.custom_colors('default')
cols     = ccol.shiftedColorMap(cols1, midpoint=0.5, name='shifted')
#********************************************************************************************************
# Fetch job attributes and files
nrun=len(modnames)
nvar=len(varnames)

# find netcdf files
# in format: [[mod1var1,mod1var2,...],[mod2var1,mod2var2,...],...]
ncmods = []
for i in range(nrun):
    ncmods.append([])
    for j in range(nvar):
      ncpath    = disk+modnames[i]+'_evaluation_output.nc'
      ncmod     = ncdf.Dataset(ncpath,'r')
      ncmods[i].append(ncmod)

#********************************************************************************************************
# VAR_PROC calculates zonal mean (as input), climatological annual mean and variance
def var_proc(ncmod):
   # extract dimensions
   global lat, hgt, tim
   lat     = ncmod[0].variables['latitude'][:]
   hgt     = ncmod[0].variables['hybrid_ht'][:]
   tim     = ncmod[0].variables['t'][:]
   # annual mean and variance 
   tvars   = []
   vvars   = []
   for j in range(nvar):
# np.where((lat>=-30) & (lat <=30)) returns the indices where the function returns true
      # get variable
      var  = np.mean(np.array(ncmod[j].variables[field[j]], dtype=np.float64)[:,:,:,:],axis=3)
      # time mean
      tvar = np.mean(var, axis=0, dtype=np.float64)
      tvars.append(tvar)
#      # yearly mean
#      yvar = np.empty((nyrs,len(hgt),len(lat)))
#      for i in range(0,nyrs):
#         jan = 12*i
#         yvar[i,:,:] = np.mean(var[jan:jan+12,:,:], axis=0, dtype=np.float64)
      # variance 
#      vvar = np.var(yvar, axis=0, dtype=np.float64)
#      vvars.append(vvar)
   # sum up (no effect if only one variable)
   tvar    = sum(tvars)
#   vvar    = sum(vvars)
   return(tvar)#,vvar)

#************************************************************
# TROP_HGT calculates zonal mean tropopause height
def trop_hgt(ncmod):
   # get tropopause height
   trophgt    = np.array(ncmod[0].variables['ht_1'], dtype=np.float64)[:,0,:,:]*1E-3  # km
   zttrophgt  = trophgt.mean(axis=2, dtype=np.float64).mean(axis=0, dtype=np.float64)
   return(zttrophgt)

#************************************************************
base  = var_proc(ncmods[0]) # first experiment
mod1  = var_proc(ncmods[1]) # second experiment

# Means
#mbase = base[0]
#mmod1 = mod1[0]

# Variances
#vbase = base[1]
#vmod1 = mod1[1]

# Difference
diff = mod1 - base
pdiff = diff / base * 100

# Tropopause height of base run
trophgt  = trop_hgt(ncmods[0])

#************************************************************
# PLOT Data
plt.figure	   (figsize=(7,8), dpi=100)#figsize=(11.69,8.27), dpi=100) #A4 figure(figsize=(8.27, 11.69), dpi=100)
plt.subplots_adjust(left=0.17, bottom=0.1,\
                    right=0.92, top=0.95,\
                    wspace=0.215, hspace=0.23)
plt.subplot	   (1,1,1, axisbg=	'#CCCCCC')
CS  = plt.contourf (lat[:], np.array(hgt[:])*1E-3, pdiff[:], levs, cmap=cols, inline=1, fontsize=18, extend='both')
CS2 = plt.contour  (lat[:], np.array(hgt[:])*1E-3, diff[:], clevs,colors='black', hold='on', linewidths=0.5)
plt.clabel         (CS2, fontsize=19, fmt='%.'+str(cdp)+'f',ticks=levs[::2])
# Tropopause height
plt.plot  	   (lat, trophgt[:]	 , color='darkgreen', lw=2, label='Tropopause')
#plt.legend	   (loc = 'upper right', frameon = False)
plt.xlabel         (xlab,fontsize=24)
plt.ylabel         (ylab,fontsize=24)
plt.xticks	   (np.arange(-90,120,30),	['90S','60S','30S','EQ','30N','60N','90N'])
plt.tick_params    (axis='both', which='major', labelsize=24, pad=10, direction='in', length=8)
plt.yticks         (np.arange(0,lid+yby,yby), ylabs)
plt.ylim           (0,lid)
cbar=plt.colorbar  (CS, orientation='horizontal',ticks=levs[::2])
cbar.ax.set_xlabel (clab, fontsize=22)
cbar.ax.tick_params(labelsize=22)
plt.title          (modnames[1]+'-'+modnames[0], fontsize=22)
plt.savefig	   (outdir+plotname, bbox_inches='tight')
plt.show	   ()
