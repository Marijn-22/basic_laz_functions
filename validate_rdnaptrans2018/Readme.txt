This folder contains the files that where used to validate the RDNAPTRANS2018 implementation in python
of the file rd_nap_trans_2018_python.

The function rdnaptrans2018_etrs_latlonheight_to_rd_validatated results in 100% correct in all the validated columns. This can also be seen in the screenshot in this folder. 

The function rdnaptrans2018_etrs_latlonheight_to_rd results results in 100% correct results inside the grid files that are required to perform the correct height transformation. However outside these bounds the function returns inf. A screenshot in this folder shows the results. This function is however easier and therefore implemented in more code. 

The following link gives the location to the validation service of the kadaster:
https://www.nsgi.nl/web/nsgi/geodetische-infrastructuur/producten/programma-rdnaptrans/validatieservice#etrsresult

The following link gives an example with correct transformed coordinates, so you can check your conversion yourself:
https://www.nsgi.nl/web/nsgi/geodetische-infrastructuur/producten/programma-rdnaptrans/zelfvalidatie