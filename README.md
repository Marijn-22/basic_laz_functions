# Code for manipulating .las and .laz files
This repository contains three functions to manipulate .las and .laz files in the "las_and_laz_processing_functions" repository. These are listed below

- find_times_of_scripts.py: Used to find flight characteristics of the mission when the data is acquired with an UAV LiDAR system. These characteristics contain start and stop time of flight strips, orientation and speed of flight strips and other useful information.
- las_from_epsg7930_to_rd.py: Used to reproject .las and .laz files from epsg7930 to the Dutch Rijksdriehoeks coordinate system, with the RDNAP2018 transformation.
- las_to_laz.py : Used to transform .las files to .laz files.

## Install:
Install all the required packages as found in the scripts. Make sure the installed laspy version supports .laz files. Install for example with: "pip install laspy[lazrs]"
