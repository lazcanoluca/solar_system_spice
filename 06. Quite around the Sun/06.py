import datetime
import pathlib
import urllib
import os
import numpy as np
import spiceypy

def download_kernel(dl_path, dl_url):
	
	file_name = dl_url.split('/')[-1]
	
	pathlib.Path(dl_path).mkdir(exist_ok=True)
	
	if not os.path.isfile(dl_path + file_name):
		
		urllib.request.urlretrieve(dl_url, dl_path + file_name)

PATH = 'r\ C:\Users\Luca\Desktop\Python_space\Programs\_kernels\spk'	
URL = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/asteroids/' \
      + 'codes_300ast_20100725.bsp'

download_kernel(PATH, URL)

PATH = 'r\ C:\Users\Luca\Desktop\Python_space\Programs\_kernels\_misc'
URL = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/asteroids/' \
      + 'codes_300ast_20100725.tf'

download_kernel(PATH, URL)

spiceypy.furnsh('kernel_meta.txt')
