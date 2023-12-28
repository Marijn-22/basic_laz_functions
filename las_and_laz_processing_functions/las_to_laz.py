import laspy
import numpy as np
from pyproj import Transformer
import pyproj
import glob
import os


# input  and output path
input_folder = r'C:\Users\marij\Documents\Marijn\TU_Delft_light\Master\Year_2\Master_Thesis\flights\flight_data\zegveld\YS-20221206-150252_store_version\100m\epsg7930'
output_folder_path = input_folder #
input_file_paths = glob.glob(os.path.join(input_folder,'*.las'))

for path in input_file_paths:
    path_no_ext = os.path.splitext(path)[0]
    filename = os.path.split(path_no_ext)[1] + '.laz'
    output_path = os.path.join(output_folder_path, filename)
    las = laspy.read(path)
    las.write(output_path)
