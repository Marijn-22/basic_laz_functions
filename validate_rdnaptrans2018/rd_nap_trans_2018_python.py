from pyproj import Transformer
import pyproj
import numpy as np

import coordinate_projection_conversion as cpc
# This code has contains the correct RDNAPTRANS2018 conversion, and has been validated using the kadaster validation service.

# Specify location where resource files are located 
pyproj.datadir.append_data_dir(r"C:\Users\marij\Documents\Code\msc_thesis\pyproj_dir")

# Proj string 
pipeline_string_rd_trans_2018 = f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=axisswap +order=2,1 +step +proj=vgridshift +grids=nlgeo2018.tif +step +proj=hgridshift +inv +grids=rdtrans2018.tif +step +proj=sterea +lat_0=52.156160556 +lon_0=5.387638889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel'

# Transforms from etrs89 to RD
transformer_to_rd_trans = Transformer.from_pipeline(pipeline_string_rd_trans_2018)

def rdnaptrans2018_etrs_latlonheight_to_rd(lat, lon, height):
    ''' Function transforms coordinates correctly inside the provided gridfiles
    of the kadaster, but does not function correctly outside these areas.'''
    rd_coords = transformer_to_rd_trans.transform(lat, lon, height)
    return rd_coords

def rdnaptrans2018_etrs_cart_to_rd(x, y, z):
    coord_ertf2000_llh = cpc.cart_to_lat_lon(x, y, z)
    rd_coords = transformer_to_rd_trans.transform(coord_ertf2000_llh[0], coord_ertf2000_llh[1], coord_ertf2000_llh[2])
    return rd_coords

# Added support for transformations outside of the grid files. This is required for the validation service of the Kadaster. 
pipeline_string_rd_trans_2018_extra = f"+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=axisswap +order=2,1 +step +proj=push +v_3 +step +proj=set +v_3=43 +omit_inv +step +proj=cart +ellps=GRS80 +step +proj=helmert +x=-565.7346 +y=-50.4058 +z=-465.2895 +rx=-0.395023 +ry=0.330776 +rz=-1.876073 +s=-4.07242 +convention=coordinate_frame +exact +step +proj=cart +inv +ellps=bessel +step +proj=hgridshift +inv +grids=rdcorr2018.tif,null +step +proj=sterea +lat_0=52.156160556 +lon_0=5.387638889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +step +proj=set +v_3=0 +omit_fwd +step +proj=pop +v_3"
transformer_to_rd_trans_extra = Transformer.from_pipeline(pipeline_string_rd_trans_2018_extra)

def rdnaptrans2018_etrs_latlonheight_to_rd_validatated(lat, lon, height):
    ''' Validated function by the official website. This function also 
    works outside the provided gridfiles but does not return a height
    value in this case.'''
    rd_coords = transformer_to_rd_trans.transform(lat, lon, height)
    rd_coordz = rd_coords[2]
    indexes = np.isinf(rd_coordz)
    lat_extra = lat[indexes]
    lon_extra = lon[indexes]
    height_extra = height[indexes]
    # Calc location for positions outside grids and update this to the output data without height information. 
    rd_coords_extra = transformer_to_rd_trans_extra.transform(lat_extra, lon_extra, height_extra)
    rd_coords[0][indexes] = rd_coords_extra[0]
    rd_coords[1][indexes] = rd_coords_extra[1]
    return rd_coords


if __name__ == "__main__":
    # Validate code at the kadaster
    # https://www.nsgi.nl/web/nsgi/geodetische-infrastructuur/producten/programma-rdnaptrans/validatieservice#etrsresult
    # https://www.nsgi.nl/web/nsgi/geodetische-infrastructuur/producten/programma-rdnaptrans/zelfvalidatie

    # Load the data in python
    data_array = np.genfromtxt("validate_rdnaptrans2018\\002_ETRS89.txt", skip_header = 1)#, dtype=None) #r"C:\Users\marij\Downloads\test.txt")

    # Transform the data
    rd_coords = rdnaptrans2018_etrs_latlonheight_to_rd_validatated(data_array[:,1], data_array[:,2], data_array[:,3])
    
    # Save the data
    f = open('validate_rdnaptrans2018\\rd_out.txt', 'w')
    f.write("point_id\tx_coordinate\t\ty_coordinate\t\theight\n")
    for i in range(len(rd_coords[0])):
        
        if len(str(rd_coords[0][i])) != 19:
            number = 19-len(str(rd_coords[0][i]))
            rd_coordx = number*" " + str(rd_coords[0][i])
        else:
            rd_coordx = str(rd_coords[0][i])

        if len(str(rd_coords[1][i])) != 19:
            number = 19-len(str(rd_coords[1][i]))
            rd_coordy = number*" " + str(rd_coords[1][i])
        else:
            rd_coordy = str(rd_coords[1][i])
        f.write(str(int(data_array[i,0])) + "\t" + rd_coordx + "\t" + rd_coordy + "\t" + str(rd_coords[2][i]) + "\n")
    f.close()
