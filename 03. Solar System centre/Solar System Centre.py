#Space Science with Python
#(#03) The Solar System centre

import datetime
import spiceypy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


#spiceypy.furnsh('kernel_meta.txt')	<-- does not work! why??
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\lsk\naif0012.tls')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\spk\de432s.bsp')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\pck\pck00010.tpc')

# Time interval.
INIT_TIME_UTC = datetime.datetime(year=2000, month=1, day=1, \
								  hour=0, minute=0, second=0)

DELTA_DAYS = 15000
END_TIME_UTC = INIT_TIME_UTC + datetime.timedelta(days=DELTA_DAYS)

INIT_TIME_UTC_STR = INIT_TIME_UTC.strftime('%Y-%m-%dT%H:%M:%S')
END_TIME_UTC_STR = END_TIME_UTC.strftime('%Y-%m-%dT%H:%M:%S')

print('Init time in UTC: %s' % INIT_TIME_UTC_STR)
print('End time in UTC: %s\n' % END_TIME_UTC_STR)

INIT_TIME_ET = spiceypy.utc2et(INIT_TIME_UTC_STR)
END_TIME_ET = spiceypy.utc2et(END_TIME_UTC_STR)

TIME_INTERVAL_ET = np.linspace(INIT_TIME_ET, END_TIME_ET, DELTA_DAYS)

# Convert to ET.
INIT_TIME_ET = spiceypy.utc2et(INIT_TIME_UTC_STR)

# Extract sun radius and use X component.
_, RADII_SUN = spiceypy.bodvcd(bodyid=10, item='RADII', maxn=3)

RADIUS_SUN = RADII_SUN[0]

# All computed parameters will be stored in a panda dataframe.
# First we create an empty one.
SOLAR_SYSTEM_DF = pd.DataFrame()

# Column stores all ETs.
SOLAR_SYSTEM_DF.loc[:, 'ET'] = TIME_INTERVAL_ET

SOLAR_SYSTEM_DF.loc[:, 'UTC'] = \
	SOLAR_SYSTEM_DF['ET'].apply(lambda x: spiceypy.et2datetime(et=x).date())

# Here is computed the position of the SSB as as seen from the sun.
# spiceypy.spkgps returns position + light time.
# We add the index [0] to obtain only the position array.
SOLAR_SYSTEM_DF.loc[:, 'POS_SSB_WRT_SUN'] = \
	SOLAR_SYSTEM_DF['ET'].apply(lambda x: spiceypy.spkgps(targ=0, \
														  et=x, \
														  ref='ECLIPJ2000', \
														  obs=10)[0])

# Scale SSB position vector with sun's radius
SOLAR_SYSTEM_DF.loc[:, 'POS_SSB_WRT_SUN_SCALED'] = \
	SOLAR_SYSTEM_DF['POS_SSB_WRT_SUN'].apply(lambda x: x / RADIUS_SUN)

# Compute distance between Sun and SSB.
SOLAR_SYSTEM_DF.loc[:, 'SSB_WRT_SUN_SCALED_DIST'] = \
	SOLAR_SYSTEM_DF['POS_SSB_WRT_SUN_SCALED'].apply(lambda x: \
													spiceypy.vnorm(x))

# Plot.
# Set a figure.
FIG, AX = plt.subplots(figsize=(12, 8))

# Plot distance between the sun and the SSB.
AX.plot(SOLAR_SYSTEM_DF['UTC'], SOLAR_SYSTEM_DF['SSB_WRT_SUN_SCALED_DIST'], \
		color='tab:blue')
		
# Label and color axis.
AX.set_xlabel('Date in UTC')
AX.set_ylabel('SSB Dist. in Sun Radii', color='tab:blue')
AX.tick_params(axis='y', labelcolor='tab:blue')

# Limit axis.
AX.set_xlim(min(SOLAR_SYSTEM_DF['UTC']), max(SOLAR_SYSTEM_DF['UTC']))
AX.set_ylim(0, 2)

# Set grid.
AX.grid(axis='x', linestyle='dashed', alpha=0.5)

# Save.
plt.savefig('SSB2SUN_DISTANCE_50000.png', dpi=300)

# Position vector gas giants.
# Name them (NAIF ID code).
NAIF_ID_DICT = {'JUP': 5, \
				'SAT': 6, \
				'URA': 7, \
				'NEP': 8}

# Iterate thru dic nd compute pos vector for each planet as seen from Sun.
# Computer phase bt SSB as seen from Sun.
for planets_name_key in NAIF_ID_DICT:
	
	# Def pandas DF column for each planet (pos and phase).
	# Each %s substring is replaced with the planets name as indicated.
	planet_pos_col = 'POS_%s_WRT_SUN' % planets_name_key
	planet_angle_col = 'PHASE_ANGLE_SUN_%s2SSB' % planets_name_key
	
	# Get NAIF ID.
	planet_id = NAIF_ID_DICT[planets_name_key]
	
	# Compute planet's pos as seen from Sun.
	SOLAR_SYSTEM_DF.loc[:, planet_pos_col] = \
		SOLAR_SYSTEM_DF['ET'].apply(lambda x: \
									spiceypy.spkgps(targ=planet_id, \
									et=x, \
									ref='ECLIPJ2000', \
									obs=10)[0])
									
	# Compute phase bt SSB and planet as seen from Sun.
	# Since we apply lambda on all col, set axis=1, otherwise: error.
	SOLAR_SYSTEM_DF.loc[:, planet_angle_col] = \
		SOLAR_SYSTEM_DF.apply(lambda x: \
							  np.degrees(spiceypy.vsep(x[planet_pos_col], \
													   x['POS_SSB_WRT_SUN'])), \
							  axis=1)
	
# Verify vsep and compute phase bt SS and Jupiter as from Sun.
# Define lambda func computes angle bt two vectors.
COMP_ANGLE = lambda vec1, vec2: np.arccos(np.dot(vec1, vec2) \
										 / (np.linalg.norm(vec1) \
											* np.linalg.norm(vec2)))
											
print('Phase angle between the SSB and Jupiter as seen form the sun (first ' \
	  'array entry, lambda function): %s' % \
	  np.degrees(COMP_ANGLE(SOLAR_SYSTEM_DF['POS_SSB_WRT_SUN'].iloc[0], \
							SOLAR_SYSTEM_DF['POS_JUP_WRT_SUN'].iloc[0])))

print('Phase angle between the SSB and Jupiter as seen form the Sun (first ' \
	  'array entry, SPICE vsep function): %s' % \
	  np.degrees(spiceypy.vsep(SOLAR_SYSTEM_DF['POS_SSB_WRT_SUN'].iloc[0], \
							   SOLAR_SYSTEM_DF['POS_SSB_WRT_SUN'].iloc[0])))
							   
# Create a 4 axes plot where all 4 plots are vertically aligned and share the X.
FIG, (AX1, AX2, AX3, AX4) = plt.subplots(4, 1, sharex=True, figsize=(8, 20))

# Iterate thru planets and plot phase.
for ax_f, planet_abr, planet_name in zip([AX1, AX2, AX3, AX4], \
										 ['JUP', 'SAT', 'URA', 'NEP'], \
										 ['Jupiter', 'Saturn', 'Uranus', \
										  'Neptune']):

	# Set planet's name as sub plot title.
	ax_f.set_title(planet_name, color='tab:orange')
	
	# Distance bt SSB and sun.
	ax_f.plot(SOLAR_SYSTEM_DF['UTC'], \
			  SOLAR_SYSTEM_DF['SSB_WRT_SUN_SCALED_DIST'], \
			  color='tab:blue')
	
	# Y set, setup.
	ax_f.set_ylabel('SSB distance in Sun Radii', color='tab:blue')
	ax_f.tick_params(axis='y', labelcolor='tab:blue')
	
	# X set and Y limits.
	ax_f.set_xlim(min(SOLAR_SYSTEM_DF['UTC']), max(SOLAR_SYSTEM_DF['UTC']))
	ax_f.set_ylim(0, 2)
	
	# Add phase.
	ax_f_add = ax_f.twinx()
	
	# Plot phase.
	ax_f_add.plot(SOLAR_SYSTEM_DF['UTC'], \
				  SOLAR_SYSTEM_DF['PHASE_ANGLE_SUN_%s2SSB' % planet_abr], \
				  color='tab:orange', \
				  linestyle='-')
	
	# Y label and setup.
	ax_f_add.set_ylabel('Planet phase in degrees', color='tab:orange')
	ax_f_add.tick_params(axis='y', labelcolor='tab:orange')
	
	# Invert Y and set limit.
	ax_f_add.invert_yaxis()
	ax_f_add.set_ylim(180, 0)
	
	# Set a grid (only date)
	ax_f.grid(axis='x', linestyle='dashed', alpha=0.5)
	

# Set x label.
AX4.set_xlabel('Date in UTC')

# tight figs.
FIG.tight_layout()

# reduce dist bt axes
plt.subplots_adjust(hspace=0.2)

# save in H!
plt.savefig('PLANETS_SUN_SSB_PHASE_ANGLE.png', dpi=300)
