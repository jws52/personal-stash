#Code to obtain zonal mean and meridional mean across 10degS-10degN

import iris
import iris.analysis

#Load from external file
filename1 = "tq-selection-aojed.nc"
cubes = iris.load(filename1) # load nc data onto cubes
#Check that dimension number 4 is specific humidity
specific_humidity = cubes[4] # Assign specific humidity cube to its own name
specific_humidity # Use to check that latitude is 3rd co-ordinate of this cube

# Obtaining zonal mean
zonal_mean = specific_humidity.collapsed('longitude', iris.analysis.MEAN)

# Obtaining latitudinal co-ordinates for tropics
coord = specific_humidity.coord('latitude')
tropics1 = coord.points <= 10
tropics2 = coord.points >= -10
tropics = tropics1 == tropics2 # Only taking region between 10degS and 10degN
tropics # Look at array output to check that it makes sense
print(coord.points[tropics]) #Also check that this makes sense

# Taking zonal, then meridional mean, then selecting 70hPa level
tropics_mean = specific_humidity.collapsed('latitude', iris.analysis.MEAN)
trop_zonal_mean = tropics_mean.collapsed('longitude', iris.analysis.MEAN)
q_trop_zonal_70hpa = trop_zonal_mean.extract(iris.Constraint(Pressure=70.0))

# plotting

import matplotlib.pyplot as plt
import iris.plot as iplt
import iris.quickplot as qplot
qplot.plot(q_trop_zonal_70hpa)
plt.show()
