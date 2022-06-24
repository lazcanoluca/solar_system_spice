#Space Science with Python
#(#01) Setup and first steps

#import libraries
import spiceypy
import datetime
import math

#add kernels
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\SpaceScienceTutorial-master\_kernels\lsk\naif0012.tls')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\SpaceScienceTutorial-master\_kernels\spk\de432s.bsp')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\SpaceScienceTutorial-master\_kernels\pck\gm_de431.tpc')

_, GM_SUN = spiceypy.bodvcd(bodyid=10, item='GM', maxn=1)

#today's date
DATE_TODAY = datetime.datetime.today()

#convert the datetime to a string, replacing the time with midnight
DATE_TODAY = DATE_TODAY.strftime("%Y-%m-%dT00:00:00")

#UTC (universal time) to ET (east time)
ET_TODAY_MIDNIGHT = spiceypy.utc2et(DATE_TODAY)

print("East time today midnight: ", \
		ET_TODAY_MIDNIGHT)

################################################

#state vector
#first 3 values -> xyz components in km
#las 3 values -> velocity componentes in km/s
EARTH_STATE_WRT_SUN, EARTH_SUN_LT = spiceypy.spkgeo(targ=399, \
													et=ET_TODAY_MIDNIGHT, \
													ref='ECLIPJ2000', obs=10)

print('\nState vector of the Earth w.r.t. the Sun for "today" (midnight): \n', \
		EARTH_STATE_WRT_SUN, EARTH_SUN_LT)

################################################

EARTH_SUN_DISTANCE = math.sqrt(EARTH_STATE_WRT_SUN[0]**2.0 \
							 + EARTH_STATE_WRT_SUN[1]**2.0 \
							 + EARTH_STATE_WRT_SUN[2]**2.0)
							 
EARTH_SUN_DISTANCE_AU =	spiceypy.convrt(EARTH_SUN_DISTANCE, 'km', 'AU')

print('\nCurrent distance between Earth and Sun in AU is: ', \
		EARTH_SUN_DISTANCE_AU)

################################################

EARTH_ORB_SPEED_WRT_SUN = math.sqrt(EARTH_STATE_WRT_SUN[3]**2.0 \
								  + EARTH_STATE_WRT_SUN[4]**2.0 \
								  + EARTH_STATE_WRT_SUN[5]**2.0)
								  
print('Current orbital speed of the Earth around the Sun in km/s:', \
	   EARTH_ORB_SPEED_WRT_SUN)
	   
V_ORB_FUNC = lambda gm, r: math.sqrt(gm/r)
EARTH_ORB_SPEED_WRT_SUN_THEORY = V_ORB_FUNC(GM_SUN[0], EARTH_SUN_DISTANCE)

print('Theoretical orbital speed of the Eart around the Sun in km/s:', \
		EARTH_ORB_SPEED_WRT_SUN)


