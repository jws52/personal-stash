import matplotlib.pyplot as plt
import math

### Current plot does not show differences between sources well enough, consider taking a difference from all of them ###

# Initialising temperature range
T= []
T = range(111,273, 1)

# Developing list of vapour pressur values
# Marti and Mauersberger[1993]
Pice1 = []
for i in range(len(T)): Pice1 += [10.0**(12.537 -2663.5/T[i])]

# Simmons et al. [1999]
Pi2 = []
Pw2 = []
for i in range(len(T)): Pi2 += [611.21 *math.exp(22.587*(T[i]-273.16)/(T[i]+0.7))]
for i in range(len(T)): Pw2 += [611.21 *math.exp(17.502*((T[i]-273.16)/(T[i]-32.19))**2)]

Pice2 = []
for i in range(len(T))[:-23]: Pice2 += [Pi2[i]]
for i in range(len(T))[-23:]: Pice2 += [Pi2[i] +(Pw2[i]-Pi2[i])*((T[i]-250.16)/23)**2]

# Murphy and Koop [2005]
Pice3 = []
for i in range(len(T)): Pice3 += [math.exp(9.550426 -5723.265/T[i] +3.53068*math.log(T[i]) -0.00728332*T[i])]

# Bielska et al. [2013]
Th = []
for i in range(len(T)): Th += [T[i]/273.16]
Pice4 = []
for i in range(len(T)): Pice4 += [611.657*math.exp(1/Th[i]*(-21.2144006*Th[i]**0.0333333333 + 27.3203819*Th[i]**1.2066667 -6.10598130*Th[i]**1.70333333))]

# Plotting
plt.plot(T, Pice1, T, Pice2, T, Pice3, T, Pice4, linewidth=2)
plt.ylim(0.01,1000)
plt.yscale('log')
plt.xlim(190, 274)
plt.legend(['Marti and Mauersberger[1993]', 'Simmons et al. [1999]', 'Murphy and Koop [2005]', 'Bielska et al. [2013]'], loc=2)
plt.title('Vapour pressure over ice from various sources')
plt.xlabel('Temperature (K)')
plt.ylabel('Vapour pressure (Pa)')
plt.show()
