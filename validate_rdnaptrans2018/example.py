

from pyproj import Transformer
import pyproj
import numpy as np

import coordinate_projection_conversion as cpc
# This code has contains the correct RDNAPTRANS2018 conversion, and has been validated using the kadaster validation service.

# Specify location where resource files are located 
pyproj.datadir.append_data_dir(r"C:\Users\marij\Documents\Code\msc_thesis\pyproj_dir")

# Proj string 
pipeline_string_rd_trans_2018 = f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=axisswap +order=2,1 +step +proj=vgridshift +grids=nlgeo2018.tif +step +proj=hgridshift +inv +grids=rdtrans2018.tif +step +proj=sterea +lat_0=52.156160556 +lon_0=5.387638889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel'

# Transformer from etrs89 to RD
transformer_to_rd_trans = Transformer.from_pipeline(pipeline_string_rd_trans_2018)

# Load the data in python
data_array = np.genfromtxt("validate_rdnaptrans2018\\002_ETRS89.txt", skip_header = 1)

# Transform the data
# Example rd_coords = transformer_to_rd_trans.transform(lats, lons, heights)
rd_coords = transformer_to_rd_trans.transform(data_array[:,1], data_array[:,2], data_array[:,3])