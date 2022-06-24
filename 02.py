#Space Science with Python
#(#02) A look at Kepler’s first law

#The orbit of a planet is an ellipse with the Sun at one of the two foci.
#-Kepler's first law

#Solar System Barycentre (SSB): mass centre of the Solar System.

import datetime
import spiceypy
import numpy as np
import matplotlib.pyplot as plt


#spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\kernel_meta.txt')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\lsk\naif0012.tls')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\spk\de432s.bsp')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\pck\pck00010.tpc')

#Compute SSB w.r.t. centre of sun in certain time interval.
#First, set initial time in UTC.
INIT_TIME_UTC = datetime.datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)
print(INIT_TIME_UTC)

#Add # of days.
DELTA_DAYS = 10000
END_TIME_UTC = INIT_TIME_UTC + datetime.timedelta(days=DELTA_DAYS)

print(END_TIME_UTC)

#Convert the datetime objects now to strings.
INIT_TIME_UTC_STR = INIT_TIME_UTC.strftime('%Y-%m-%dT%H:%M:%S')
END_TIME_UTC_STR = END_TIME_UTC.strftime('%Y-%m-%dT%H:%M:%S')

#Print starting and end times.
print('Init time in UTC: %s' % INIT_TIME_UTC_STR)
print('End time in UTC: %s\n' % END_TIME_UTC_STR)

#Convert to ET using SPICE function utc2et.
INIT_TIME_ET = spiceypy.utc2et(INIT_TIME_UTC_STR)
END_TIME_ET = spiceypy.utc2et(END_TIME_UTC_STR)

#Elapsed time
print('Covered time interval in seconds. %s\n' % (END_TIME_ET - INIT_TIME_ET))

#Numpy array covers time interval delta = 1 day stop
TIME_INTERVAL_ET = np.linspace(INIT_TIME_ET, END_TIME_ET, DELTA_DAYS)

#Position SSB w.r.t. sun.
#Set empty list stores xyz for each time step.
SSB_WRT_SUN_POSITION = []	

#Each time step used in for to compute pos SSB.
for TIME_INTERVAL_ET_f in TIME_INTERVAL_ET:
	_position, _ = spiceypy.spkgps(targ=0, et=TIME_INTERVAL_ET_f, \
								   ref='ECLIPJ2000', obs=10)
								   
	#Append result to final list.
	SSB_WRT_SUN_POSITION.append(_position)
	
#Convert list to numpy array.
SSB_WRT_SUN_POSITION = np.array(SSB_WRT_SUN_POSITION)

print('Position of SSB w.r.t. centre of sun at 0s:\n' \
	  'X = %s km \n' \
	  'Y = %s km \n' \
	  'Z = %s km \n' % tuple(np.round(SSB_WRT_SUN_POSITION[0])))

print('Distance between SSB w.r.t. centre of sun at 0s:\n' \
	  'd = %s km \n' % round(np.linalg.norm(SSB_WRT_SUN_POSITION[0])))

#Sun radius, only X value.
_, RADII_SUN = spiceypy.bodvcd(bodyid=10, item='RADII', maxn=3)

RADIUS_SUN = RADII_SUN[0]

#Scale the pos value to sun's radius.
SSB_WRT_SUN_POSITION_SCALED = SSB_WRT_SUN_POSITION / RADIUS_SUN

#Plot trajectory of the SSB w.r.t. Sun using matplotlib
#Only plot XY (ecliptic plane)
SSB_WRT_SUN_POSITION_SCALED_XY = SSB_WRT_SUN_POSITION_SCALED[:, 0:2]

plt.style.use('dark_background')

FIG, AX = plt.subplots(figsize=(12,8))

SUN_CIRC = plt.Circle((0.0, 0.0), 1.0, color='yellow', alpha=0.8)	
AX.add_artist(SUN_CIRC)

AX.plot(SSB_WRT_SUN_POSITION_SCALED_XY[:, 0], \
		SSB_WRT_SUN_POSITION_SCALED_XY[:, 1], \
		ls='solid', color='royalblue')
		
AX.set_aspect('equal')
AX.grid(True, linestyle='dashed', alpha=0.5)
AX.set_xlim(-2, 2)
AX.set_ylim(-2, 2)

AX.set_xlabel('X in sun-radius')
AX.set_ylabel('Y in sun-radius')

plt.savefig('SSB_WRT_SUN.png', dpi=300)

#Days SSB outside Sun.
#Distance SSB-SUN.
SSB_WRT_SUN_DISTANCE_SCALED = np.linalg.norm(SSB_WRT_SUN_POSITION_SCALED, \
								axis=1)
								
print('Computation time: %s days \n' % DELTA_DAYS)

## of days outside sun.
SSB_OUTSIDE_SUN_DELTA_DAYS = len(np.where(SSB_WRT_SUN_DISTANCE_SCALED > 1)[0])

print('Fraction of time where the sun SSB was outside the sun: %s %%' \
	  % (100 * SSB_OUTSIDE_SUN_DELTA_DAYS \
							/ DELTA_DAYS))
							
