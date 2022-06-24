import datetime
import spiceypy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\lsk\naif0012.tls')
spiceypy.furnsh(r'C:\Users\Luca\Desktop\Python_space\Programs\_kernels\spk\de432s.bsp')

DATETIME_UTC = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
DATETIME_ET = spiceypy.utc2et(DATETIME_UTC)

# Pandas dataframe to append data.
solsys_df = pd.DataFrame()

solsys_df.loc[:, 'ET'] = [DATETIME_ET]
solsys_df.loc[:, 'UTC'] = [DATETIME_UTC]

# Dictionary that lists body names.
SOLSYS_DICT = {'SUN': 10, 'VENUS': 299, 'MOON': 301, 'MARS': 4}

# Iterate thru dictionary and compute position info.
for body_name in SOLSYS_DICT:	
	
	# First compute directional vector Earth - body in ECLIP2000.
	# Use LT+S light time correction. spekzp returns directional vector and light time.
	# Apply [0] to get only vector.
	solsys_df.loc[:, f'dir_{body_name}_wrt_earth_ecl'] = solsys_df['ET'] \
		.apply(lambda x: spiceypy.spkezp(targ=SOLSYS_DICT[body_name], \
										 et=x, \
										 ref='ECLIPJ2000', \
										 abcorr='LT+S', \
										 obs=399)[0])
	
	# Compute longitude and latitude of the body in radians in ECLIPJ2000 using recrad.
	# recrad returns distance, longitude and latitude values; thus apply [1] and [2] to
	# get longitude and latitude, respectively.
	solsys_df.loc[:, f'{body_name}_long_rad_ecl'] = \
		solsys_df[f'dir_{body_name}_wrt_earth_ecl'] \
			.apply(lambda x: spiceypy.recrad(x)[1])
			
	solsys_df.loc[:, f'{body_name}_lat_rad_ecl'] = \
		solsys_df[f'dir_{body_name}_wrt_earth_ecl'] \
			.apply(lambda x: spiceypy.recrad(x)[2])

# Plot.
for body_name in SOLSYS_DICT:
	
	solsys_df.loc[:, f'{body_name}_long_rad4plot_ecl'] = \
		solsys_df[f'{body_name}_long_rad_ecl'] \
			.apply(lambda x: -1*((x % np.pi) - np.pi) if x > np.pi \
				   else -1*x)

plt.style.use('dark_background')

plt.figure(figsize=(12, 8))
plt.subplot(projection="aitoff")

plt.title(f'{DATETIME_UTC} UTC'	, fontsize=10)

BODY_COLOR_ARRAY = ['y', 'tab:orange', 'tab:gray', 'tab:red']

for body_name, body_color in zip(SOLSYS_DICT, BODY_COLOR_ARRAY):
	
	plt.plot(solsys_df[f'{body_name}_long_rad4plot_ecl'], \
			 solsys_df[f'{body_name}_lat_rad_ecl'], \
			 color=body_color, marker='o', linestyle='None', markersize=12, \
			 label=body_name.capitalize())

plt.xticks(ticks=np.radians([-150, -120, -90, -60, -30, 0, \
							 30, 60, 90, 120, 150]),
		   labels=['150°', '120°', '90°', '60°', '30°', '0°', \
				   '330°', '300°', '270°', '240°', '210°'])
				   
plt.xlabel('Eclip. long. in deg')
plt.ylabel('Eclip. lat. in deg')

plt.legend()
plt.grid(True)

plt.savefig('eclipj2000_sky_map.png', dpi=300)


# Now we compute coordinates in equatorial J2000.
for body_name in SOLSYS_DICT:
	
	# Directional vector of the body as seen form Earth in J2000.
	solsys_df.loc[:, f'dir_{body_name}_wrt_earth_equ'] = solsys_df['ET'] \
		.apply(lambda x: spiceypy.spkezp(targ=SOLSYS_DICT[body_name], \
										 et=x, \
										 ref='J2000', \
										 abcorr='LT+S', \
										 obs=399)[0])
										 
	# Compute longitude and latitude.
	solsys_df.loc[:, f'{body_name}_long_rad_equ'] = \
		solsys_df[f'dir_{body_name}_wrt_earth_equ'] \
			.apply(lambda x: spiceypy.recrad(x)[1])
	solsys_df.loc[:, f'{body_name}_lat_rad_equ'] = \
		solsys_df[f'dir_{body_name}_wrt_earth_equ'] \
			.apply(lambda x: spiceypy.recrad(x)[2])
			
	# Same logic as before to compute longitudes for matplotlib figure.
	solsys_df.loc[:, f'{body_name}_long_rad4plot_equ'] = \
		solsys_df[f'{body_name}_long_rad_equ'] \
			.apply(lambda x: -1*((x % np.pi) - np.pi) if x > np.pi \
				   else -1*x)

# Set ecliptic plane for visualisation.
eclip_plane_df = pd.DataFrame()

# Add ecliptic longitude and latitude.
eclip_plane_df.loc[:, 'ECLIPJ2000_long_rad'] = np.linspace(0, 2*np.pi, 100)
eclip_plane_df.loc[:, 'ECLIPJ2000_lat_rad'] = np.pi/2.0

# Compute directional vectors for different longitude value (lat constant)
# SPICE function sphrec to transform spherical coordinates to vectors.
# r=1 is the normalised distance.
eclip_plane_df.loc[:, 'ECLIPJ2000_direction'] = \
	eclip_plane_df\
		.apply(lambda x: spiceypy.sphrec(r=1, \
										 colat=x['ECLIPJ2000_lat_rad'], \
										 lon=x['ECLIPJ2000_long_rad']), \
			   axis=1)

# Compute transf matrix bt ECLIPJ2000 and J2000 for a fixed date-time.
# Since both systems are inertial (not changing in time) the resulting
# matrix is the same for different ETs.
ECL2EQU_MAT = spiceypy.pxform(fromstr='ECLIPJ2000', \
							  tostr='J2000', \
							  et=DATETIME_ET)

# Compute direction vectors of ecliptic plane in J2000 using transform matrix.
eclip_plane_df.loc[:, 'j2000_direction'] = \
	eclip_plane_df['ECLIPJ2000_direction'].apply(lambda x: ECL2EQU_MAT.dot(x))
	
# Compute longitude and latitude values using SPICE function recrad.
eclip_plane_df.loc[:, 'j2000_long_rad'] = \
	eclip_plane_df['j2000_direction'].apply(lambda x: spiceypy.recrad(x)[1])

eclip_plane_df.loc[:, 'j2000_long_rad4plot'] = \
	eclip_plane_df['j2000_long_rad'] \
		.apply(lambda x: -1*((x % np.pi) - np.pi) if x > np.pi \
			   else -1*x)
			   
eclip_plane_df.loc[:, 'j2000_lat_rad'] = \
	eclip_plane_df['j2000_direction'].apply(lambda x: spiceypy.recrad(x)[2])

# Plot equatorial J2000.
plt.style.use('dark_background')
plt.figure(figsize=(12, 8))
plt.subplot(projection="aitoff")
plt.title(f'{DATETIME_UTC} UTC', fontsize=10)

for body_name, body_color in zip(SOLSYS_DICT, BODY_COLOR_ARRAY):
	
		plt.plot(solsys_df[f'{body_name}_long_rad4plot_equ'], \
				 solsys_df[f'{body_name}_lat_rad_equ'], \
				 color=body_color, marker='o', linestyle='None', markersize=12, \
				 label=body_name.capitalize())

# Plot ecliptic plane as blue dotted line.
plt.plot(eclip_plane_df['j2000_long_rad4plot'], \
		 eclip_plane_df['j2000_lat_rad'], color='tab:blue', linestyle='None', \
		 marker='o', markersize=2)
		 
# Convert longitude values in right ascension hours.
plt.xticks(ticks=np.radians([-150, -120, -90, -60, -30, 0, \
							30, 60, 90, 120, 150]),
		   labels=['10h', '8h', '6h', '4h', '2h', '0h', \
				   '22h', '20h', '18h', '16h', '14h'])

plt.xlabel('Right ascension in hours')
plt.ylabel('Declination in deg.')

plt.legend()
plt.grid(True)

plt.savefig('j2000_sky_map.png', dpi=300)
