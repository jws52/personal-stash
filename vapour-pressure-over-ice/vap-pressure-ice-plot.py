import matplotlib.pyplot as plt
import math

### Current plot does not show differences between sources well enough, consider taking a difference from all of them ###

# Initialising temperature range
T= []
T = range(50,273, 1)

# Developing list of vapour pressure values
# Marti and Mauersberger[1993]
# Note: valid for T between 170 and 253K only
T1 = range(170,253,1)
Pice1 = []
for i in range(len(T1)): Pice1 += [10.0**(12.537 -2663.5/T1[i])]

# Simmons et al. [1999]
# Note: Simmons treats as valid for all T below 273.16K
Pi2 = [] # For vapour pressure over ice
Pw2 = [] # For vapour pressure over water (combined with Pi2 for T between -23C and 0C)
for i in range(len(T)): Pi2 += [611.21 *math.exp(22.587*(T[i]-273.16)/(T[i]+0.7))]
for i in range(len(T)): Pw2 += [611.21 *math.exp(17.502*(T[i]-273.16)/(T[i]-32.19))]
Pice2 = []
for i in range(len(T))[:-23]: Pice2 += [Pi2[i]]
for i in range(len(T))[-23:]: Pice2 += [Pi2[i] +(Pw2[i]-Pi2[i])*((T[i]-250.16)/23)**2]

# Murphy and Koop [2005]
# Note: valid for 110K to 273.16K
T3 = range(110,273,1)
Pice3 = []
for i in range(len(T3)): Pice3 += [math.exp(9.550426 -5723.265/T3[i] +3.53068*math.log(T3[i]) -0.00728332*T3[i])]

# Wagner et al. [2011]
# Note: valid for 50K to 273.16K
Th = []
for i in range(len(T)): Th += [T[i]/273.16]
Pice4 = []
for i in range(len(T)): Pice4 += [611.657*math.exp((1/Th[i])*(-21.2144006*Th[i]**0.00333333333 + 27.3203819*Th[i]**1.2066667 -6.10598130*Th[i]**1.70333333))]

# Calculation of differences
Pdiff1 = []
Pdiff2 = [] 
Pdiff3 = [] 
Pdiff4 = []
print "Pdiff1 = ",Pdiff1
for i in range(len(T1)): Pdiff1 += [(Pice1[i]-Pice3[i+170-110])*100/Pice3[i+170-110]]
for i in range(len(T3)): Pdiff2 += [(Pice2[i+110-50]-Pice3[i])*100/Pice3[i]]
for i in range(len(T3)): Pdiff3 += [(Pice3[i]-Pice3[i])*100/Pice3[i]]
for i in range(len(T3)): Pdiff4 += [(Pice4[i+110-50]-Pice3[i])*100/Pice3[i]]

# Plotting
plt.gca().set_color_cycle(['black', 'red', 'blue', 'green', 'magenta', 'yellow', 'cyan'])
# Values plot
plt.plot(T1, Pice1, T, Pice2, T3, Pice3, T, Pice4, linewidth=2)
plt.yscale('log')
plt.legend(['Murphy and Koop [2005]', 'Marti and Mauersberger[1993]', 'Simmons et al. [1999]', 'Wagner et al. [2011]'], loc=4)
plt.title('Vapour pressure over ice from various sources')
plt.show()

# Differences plot
plt.gca().set_color_cycle(['black', 'red', 'blue', 'green', 'magenta', 'yellow', 'cyan'])
plt.plot(T3, Pdiff3, '--', T1, Pdiff1, T3, Pdiff2, T3, Pdiff4, linewidth=2)
plt.ylim(-10,10)
plt.yscale('linear')
#plt.xlim(190, 274)
plt.legend(['Murphy and Koop [2005] (baseline)', 'Marti and Mauersberger[1993]', 'Simmons et al. [1999]', 'Wagner et al. [2011]'], loc=2)
plt.title('Vapour pressure over ice from various sources - % difference from Murphy and Koop [2005]')
plt.xlabel('Temperature (K)')
plt.ylabel('Difference in vapour pressure (%)')
plt.show()
