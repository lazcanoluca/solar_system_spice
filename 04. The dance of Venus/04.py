# Space Science with Python
# (#4) The dance of Venus

import datetime
import spiceypy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as matpl_dates

spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\lsk\naif0012.tls')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\spk\de432s.bsp')

INIT_TIME_UTC_STR = datetime.datetime(year=2020, month=1, day=1) \
						.strftime('%Y-%m-%dT%H:%M:%S')
END_TIME_UTC_STR = datetime.datetime(year=2020, month=6, day=1) \
						.strftime('%Y-%m-%dT%H:%M:%S')
						
INIT_TIME_ET = spiceypy.utc2et(INIT_TIME_UTC_STR)
END_TIME_ET = spiceypy.utc2et(END_TIME_UTC_STR)

# Sec per hour, used to compute phase angles in 1 hour steps.
DELTA_HOUR_IN_SECONDS = 3600.0
TIME_INTERVAL_ET = np.arange(INIT_TIME_ET, END_TIME_ET, DELTA_HOUR_IN_SECONDS)

# Pandas dataframe.
INNER_SOLSYS_DF = pd.DataFrame()

# Set the column ET that stores all ET's.
INNER_SOLSYS_DF.loc[:, 'ET'] = TIME_INTERVAL_ET

# Column UTC transforms all ET's back to UTC.
INNER_SOLSYS_DF.loc[:, 'UTC'] = \
	INNER_SOLSYS_DF['ET'].apply(lambda x: spiceypy.et2datetime(et=x))

# Compute phase between Venus and Sun as seen form Earth.
# We need SPICE function phaseq.
# Target is Earth, illmn source is the Sun, the obsrv Venus.
# We apply correction that considers the movement of the planets and the light time (LT+S).
INNER_SOLSYS_DF.loc[:, 'EARTH_VEN2SUN_ANGLE'] = \
	INNER_SOLSYS_DF['ET'].apply(lambda x: \
									np.degrees(spiceypy.phaseq(et=x, \
															   target='399', \
															   illmn='10', \
															   obsrvr='299', \
															   abcorr='LT+S')))
# Same for Moon-Sun.
INNER_SOLSYS_DF.loc[:, 'EARTH_MOON2SUN_ANGLE'] = \
	INNER_SOLSYS_DF['ET'].apply(lambda x: \
									np.degrees(spiceypy.phaseq(et=x, \
															   target='399', \
															   illmn='10', \
															   obsrvr='301', \
															   abcorr='LT+S')))
# Same for Moon-Venus.
INNER_SOLSYS_DF.loc[:, 'EARTH_MOON2VEN_ANGLE'] = \
	INNER_SOLSYS_DF['ET'].apply(lambda x: \
									np.degrees(spiceypy.phaseq(et=x, \
															   target='399', \
															   illmn='299', \
															   obsrvr='301', \
															   abcorr='LT+S')))

# Filter with artificially set angular distances and create a binary tag for
# nice (1), not nice (0) constellations.

# Angular distance Venus - Sun: > 30°
# Angular distance Moon - Sun: > 30°
# Angular distance Moon - Venus: < 10°
INNER_SOLSYS_DF.loc[:, 'PHOTOGENIC'] = \
	INNER_SOLSYS_DF.apply(lambda x: 1 if (x['EARTH_VEN2SUN_ANGLE'] > 30.0) \
									   & (x['EARTH_MOON2SUN_ANGLE'] > 30.0) \
									   & (x['EARTH_MOON2VEN_ANGLE'] < 10.0) \
									   else 0, axis=1)

# Print temporal results (# of computed hours and # of nice hours).
print('Number of hours computed: %s (around %s days)' \
	  % (len(INNER_SOLSYS_DF), round(len(INNER_SOLSYS_DF) / 24)))
	  
print('Number of photogenic hours: %s (around %s days)' \
	  % (len(INNER_SOLSYS_DF.loc[INNER_SOLSYS_DF['PHOTOGENIC'] == 1]), \
		 round(len(INNER_SOLSYS_DF.loc[INNER_SOLSYS_DF['PHOTOGENIC'] == 1]) \
			   / 24)))

# Plot.
FIG, AX = plt.subplots(figsize=(12, 8))

AX.plot(INNER_SOLSYS_DF['UTC'], INNER_SOLSYS_DF['EARTH_VEN2SUN_ANGLE'], \
		color='tab:orange', label='Venus - Sun')

AX.plot(INNER_SOLSYS_DF['UTC'], INNER_SOLSYS_DF['EARTH_MOON2SUN_ANGLE'], \
		color='tab:gray', label='Moon - Sun')

AX.plot(INNER_SOLSYS_DF['UTC'], INNER_SOLSYS_DF['EARTH_MOON2VEN_ANGLE'], \
		color='black', label='Moon - Venus')

AX.set_xlabel('Date in UTC.')
AX.set_ylabel('Angle in degrees.')

AX.set_xlim(min(INNER_SOLSYS_DF['UTC']), max(INNER_SOLSYS_DF['UTC']))

AX.grid(axis='x', linestyle='dashed', alpha=0.5)

AX.xaxis.set_major_locator(matpl_dates.MonthLocator())
AX.xaxis.set_minor_locator(matpl_dates.DayLocator())

AX.xaxis.set_major_formatter(matpl_dates.DateFormatter('%Y-%b'))

# Iterate thru "photogenic" results and draw vertical lines when applies.
for photogenic_utc in INNER_SOLSYS_DF.loc[INNER_SOLSYS_DF['PHOTOGENIC'] == 1]['UTC']:
	AX.axvline(photogenic_utc, color='tab:blue', alpha=0.2)

AX.legend(fancybox=True, loc='upper right', framealpha=1)

plt.xticks(rotation=45)

plt.savefig('VENUS_SUN_MOON.png', dpi=300)
