import laspy
import numpy as np
from pyproj import Transformer
import pyproj
import glob
import os
import pandas as pd

# These function transform pointclouds in epsg 7930 to RD
# Made by: Marijn Brandwijk
# Date: 2023-6-1

def find_ellps_param(ellps_string):
    ''' Ellps string can be GRS80 or WGS84. Is supporting function
     for cart_to_lat_lon.
    '''
    GRS80 = {}
    GRS80['a'] = 6378137 #m
    GRS80['f'] = 1/298.257222101

    WGS84 = {}
    WGS84['a'] = 6378137
    WGS84['f'] = 1/298.257223563
 
    ellps = {}
    ellps['WGS84'] = WGS84
    ellps['GRS80'] = GRS80

    f = ellps[ellps_string]['f']
    a = ellps[ellps_string]['a']
    return f, a

def cart_to_lat_lon_quick(x, y, z,  ellps = 'GRS80', it = 3):
    ''' Function projects cartesian coordinates to 
    lat lon coordinates. x y and z can be a single value
    or np.array of size N.

    Number of 3 iterations seems optimal around NL, is 
    set so this function can work with x, y and z arrays
    and speed up the calculation significantly. 
    
    Output is in lat (deg), lon (deg), height (m)'''

    f, a = find_ellps_param(ellps)
    lam = np.arctan2(y,x)
    # find ellipse parameters
    e = np.sqrt(f*(2-f))
    
    p = np.sqrt(x**2 + y**2)
    e_ac_sq = e**2/(1-e**2)
    phi_0 = np.arctan2(z*(1+e_ac_sq),p)
    phi = phi_0

    error = np.ones(len(x))
    loop = 0

    while np.all(error > 1e-9):
        v = a/np.sqrt(1-(e**2*np.sin(phi)**2))
        phi_new = np.arctan2(z+v*e**2*np.sin(phi),p)
        error = abs(phi_new-phi)*180/np.pi
        loop += 1
        phi = phi_new

    h = (p/np.cos(phi)) - v

    # print(loop, 'iterations performed')
    return phi*180/np.pi, lam*180/np.pi,h

def transform_etrf2000_epoch_2017_5_to_rd(input_path, output_path):
    # Transformer to transform to RD
    proj_pipeline_string_rd_trans_2018 = f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=axisswap +order=2,1 +step +proj=vgridshift +grids=nlgeo2018.tif +step +proj=hgridshift +inv +grids=rdtrans2018.tif +step +proj=sterea +lat_0=52.156160556 +lon_0=5.387638889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel'
    transformer_to_rd_trans = Transformer.from_pipeline(proj_pipeline_string_rd_trans_2018)

    # Read las file
    las = laspy.read(input_path)

    # Convert cartesian coordinates to lat lon height
    coord_ertf2000_llh_las = cart_to_lat_lon_quick(np.array(las.x), np.array(las.y), np.array(las.z))

    # Transform coordinates from epsg 7930 to RD
    rd_coords = transformer_to_rd_trans.transform(
        coord_ertf2000_llh_las[0],
        coord_ertf2000_llh_las[1],
        coord_ertf2000_llh_las[2],
        )

    # Update header offset of las file, las scale is kept
    las.header.offsets = np.array((np.floor(min(rd_coords[0])),np.floor(min(rd_coords[1])),0))
    las.header.add_crs(pyproj.CRS.from_epsg(28992))

    las.x = rd_coords[0] 
    las.y = rd_coords[1] 
    las.z = rd_coords[2] 

    las.write(output_path)

def transform_trj_to_rd(input_path, output_path):
    # WARNING: THINK ABOUT VALIDITY OF THE ANGLES THAT ARE NOT TRANSFORMED
    # Transformer to transform to RD
    proj_pipeline_string_rd_trans_2018 = f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=axisswap +order=2,1 +step +proj=vgridshift +grids=nlgeo2018.tif +step +proj=hgridshift +inv +grids=rdtrans2018.tif +step +proj=sterea +lat_0=52.156160556 +lon_0=5.387638889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel'
    transformer_to_rd_trans = Transformer.from_pipeline(proj_pipeline_string_rd_trans_2018)
    
    # Load the input data
    data = np.loadtxt(input_path, skiprows = 1)
    coords = data[:,1:4]
    time = data[:,0]

    # Convert cartesian coordinates to lat lon height
    coord_ertf2000_llh_las = cart_to_lat_lon_quick(coords[:,0], coords[:,1], coords[:,2])

    # Transform coordinates from epsg 7930 to RD
    rd_coords = transformer_to_rd_trans.transform(
        coord_ertf2000_llh_las[0],
        coord_ertf2000_llh_las[1],
        coord_ertf2000_llh_las[2],
        )
    
    dictionary = {
        'time': time,
        'x': rd_coords[0],
        'y': rd_coords[1],
        'z': rd_coords[2],
        'roll': data[:,4],
        'pitch': data[:,5],
        'heading': data[:,6],
        'sdx': data[:,7],
        'sdy': data[:,8],
        'sdz': data[:,9],
        'sdroll': data[:,10],
        'sdpitch': data[:,11],
        'sdheading': data[:,12],
    }

    df = pd.DataFrame(data=dictionary)
    df.to_csv(output_path, index=None)

if __name__ == '__main__':
    # Specify location where resource files are located 
    ###  Use your own link to the pyproj_dir folder instead of the provided link below!!!!
    pyproj.datadir.append_data_dir(r"C:\Users\marij\Documents\Code\msc_thesisV2\pyproj_dir")

    transform_las_files = True
    transform_trj_files = True

    temp_input = r"C:\Users\marij\Documents\Marijn\TU_Delft_light\Master\Year_2\Master_Thesis\flights\flight_data\20230411_slik-westerschelde-nioz\50m\epsg7930"#"#r"C:\Users\marij\Documents\Marijn\TU Delft light\Master\Year_2\Master_Thesis\flights\flight_data\Goerree-Overflakkee\epsg7930"
    temp_output = r"C:\Users\marij\Documents\Marijn\TU_Delft_light\Master\Year_2\Master_Thesis\flights\flight_data\20230411_slik-westerschelde-nioz\50m\test" #r"C:\Users\marij\Documents\Marijn\TU Delft light\Master\Year_2\Master_Thesis\flights\flight_data\Goerree-Overflakkee\rd_coords"
    input_folder_path = temp_input # r"C:\Users\marij\Documents\Marijn\TU Delft light\Master\Year_2\Master_Thesis\flights\transform_point_cloud\input_folder_epsg7930"#"H:\My Documents\Marijn\Msc Thesis\data\transform_point_cloud\input_folder_epsg7930"
    output_folder_path = temp_output # r"C:\Users\marij\Documents\Marijn\TU Delft light\Master\Year_2\Master_Thesis\flights\transform_point_cloud\output_folder_rd"#"H:\My Documents\Marijn\Msc Thesis\data\transform_point_cloud\output_folder_rd"

    if transform_las_files:
        search_path = os.path.join(input_folder_path,'*.laz')
        input_paths = glob.glob(search_path)
        print('Input paths:\n',input_paths)

        for i, path in enumerate(input_paths):
            filename  = os.path.split(path)[1]
            start_name = np.char.split(filename, sep='.').tolist()
            new_filename = start_name[0]+'_RD.'+'laz'#start_name[1]
            output_path = os.path.join(output_folder_path, new_filename)

            transform_etrf2000_epoch_2017_5_to_rd(path, output_path)
            print(f'Exported {i+1} from {len(input_paths)} files.')
        
    if transform_trj_files:
        # Transform also the trajectory files found in the input folder
        trj_paths_search = os.path.join(input_folder_path,'*.txt')
        trj_paths = glob.glob(trj_paths_search)
        print('Input trajectory paths:\n',trj_paths)

        for i, path in enumerate(trj_paths):
            filename  = os.path.split(path)[1]
            start_name = np.char.split(filename, sep='.').tolist()
            new_filename = start_name[0]+'_RD.'+'txt'#start_name[1]
            output_path = os.path.join(output_folder_path, new_filename)

            transform_trj_to_rd(path, output_path)
            print(f'Exported {i+1} from {len(trj_paths)} files.')
