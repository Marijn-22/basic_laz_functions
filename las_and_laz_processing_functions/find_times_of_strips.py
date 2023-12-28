import laspy
import numpy as np
import glob
import os
import pandas as pd
import math

# This scrips can be used to find flight characteristics of the mission, including
# start and stop time of strips and other useful information that 
# can be calculated relatively quickly.
# Made by: Marijn Brandwijk
# Date: 2023-6-1

def find_start_and_end_time(gps_time, filename):
    # find start and end time strip
    start_time_strip = min(gps_time)
    end_time_strip = max(gps_time)

    # find flight nr and strip number
    list_of_strings = filename.split('-')
    for string in list_of_strings:
        try:
            number = int(string[1:4])
            if string[0] == 'F':
                flight_number = number
            elif string[0] == 'S':
                flight_line = number
        except:
            pass
    print(f'found flight line {flight_line} and number {flight_number}')
    return start_time_strip, end_time_strip, flight_number, flight_line

def find_nearest_idx(array,value):
    # required for function calculate_est_range_incidence_headings()
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx

def distance_between_lines(line1_start, line1_end, line2_start, line2_end):
    # # Calculate direction vector
    line1_vector = [line1_end[0] - line1_start[0], line1_end[1] - line1_start[1]]


    # # Calculate the length of both lines
    line1_length = math.sqrt(line1_vector[0] ** 2 + line1_vector[1] ** 2)
    # line2_length = math.sqrt(line2_vector[0] ** 2 + line2_vector[1] ** 2)

    # Closest point between two lines is estimated by checking the coordintas of corner points of a single
    # line to the minimum distance to the other line. 
    x1 = line1_start[0]
    x2 = line1_end[0]
    y1 = line1_start[1]
    y2 = line1_end[1]
    test_points = [line2_start, line2_end]
    dists = np.zeros(len(test_points))
    for i in range(len(test_points)):
        point = test_points[i]
        x3 = point[0]
        y3 = point[1]
        dists[i] = abs((y2 - y1) * x3 - (x2 - x1) * y3 + x2 * y1 - y2 * x1)/line1_length
    est_shortest_dist = np.mean(dists)

    return est_shortest_dist


if __name__ == '__main__':
    # Give as input folder a location where laz files are stored per flight strip in RD coordinates and containing the trajectory file in RD coords as text file. 
    folder_path = r"E:\export\rdnap2018"  #'E:\flight_data\20230411_slik-westerschelde-nioz\Merged_YS-20230411-122317_and_YS-20230411-142532\rd'
    height = 100 #m
    search_path = os.path.join(folder_path, '*.laz')
    paths = glob.glob(search_path)

    save_additional_trj_file_with_strips = True
    
    if len(paths) == 0:
        raise ValueError('No files found. Please check the input folder location and file extention (las or laz).')

    # Find path to the trajectory file
    search_path_trj = os.path.join(folder_path, '*.txt')
    paths_trj_unfiltered = glob.glob(search_path_trj)

    paths_trj = {}
    for path in paths_trj_unfiltered:
        if os.path.split(path)[1].split('-')[1] != 'global_information_flight.txt':
            # find flight nr and strip number
            filename = os.path.split(path)[1]
            list_of_strings = filename.split('-')
            for string in list_of_strings:
                try:
                    number = int(string[1:4])
                    if string[0] == 'F':
                        flight_number = number
                except:
                    pass
                    # raise ValueError(f'Flight number could not be found in trajectory file name. Filename now in use is {filename}. This should contain F001-')
            paths_trj[flight_number] = path

    data = {}
    flight_numbers = []
    flight_lines = []
    start_time_strip = []
    end_time_strip = []
    amount_points = []
    speed_strip = []
    duration_strip_seconds = []
    estimated_distances = []
    start_xs = []
    start_ys = []
    start_zs = []
    end_xs = []
    end_ys = []
    end_zs = []
    average_roll = []
    average_pitch = []
    average_heading = []

    for path in paths:
        # Find filename
        filename = os.path.split(path)[1]
        # Read las file
        las = laspy.read(path)
        gps_time = las['gps_time']

        # Find start and stop time of each strip
        time_data = find_start_and_end_time(gps_time, filename)
        flight_numbers.append(time_data[2])
        flight_lines.append(time_data[3])
        start_time_strip.append(time_data[0])
        end_time_strip.append(time_data[1])
        duration_strip_seconds.append(time_data[1]-time_data[0])

        # Find estimated horizontal distance of UAV strip
        flight_number = time_data[2]
        df_trj = pd.read_csv(paths_trj[flight_number])
        index_start_time = find_nearest_idx(df_trj['time'], time_data[0])
        index_end_time = find_nearest_idx(df_trj['time'], time_data[1])

        start_x = df_trj.loc[index_start_time,'x']
        start_y = df_trj.loc[index_start_time,'y']
        start_z = df_trj.loc[index_start_time,'z']

        end_x = df_trj.loc[index_end_time,'x']
        end_y = df_trj.loc[index_end_time,'y']
        end_z = df_trj.loc[index_end_time,'z']

        start_xs.append(start_x)
        start_ys.append(start_y)
        start_zs.append(start_z)
        end_xs.append(end_x)
        end_ys.append(end_y)
        end_zs.append(end_z)

        estimated_distance = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
        estimated_distances.append(estimated_distance)

        # Find estimated speed UAV strip
        speed_strip.append(estimated_distance/(time_data[1]-time_data[0]))

        # Find estimated sidelap UAV strips

        # Find amount of points
        amount_points.append(len(gps_time))

        # Find average roll, pitch and heading of the flight line
        average_roll.append(np.arctan2(np.sum(np.sin(df_trj.loc[index_start_time:index_end_time,'roll']*np.pi/180)),np.sum(np.cos(df_trj.loc[index_start_time:index_end_time,'roll']*np.pi/180)))*180/np.pi)
        average_pitch.append(np.arctan2(np.sum(np.sin(df_trj.loc[index_start_time:index_end_time,'pitch']*np.pi/180)),np.sum(np.cos(df_trj.loc[index_start_time:index_end_time,'pitch']*np.pi/180)))*180/np.pi)
        average_heading.append(np.arctan2(np.sum(np.sin(df_trj.loc[index_start_time:index_end_time,'heading']*np.pi/180)),np.sum(np.cos(df_trj.loc[index_start_time:index_end_time,'heading']*np.pi/180)))*180/np.pi)
        # print('av_roll',average_roll)
        # print('av_p',average_pitch)
        # print('av_h',average_heading)
        # average_pitch = []
        # average_heading = []

    data['flight_numbers'] = flight_numbers
    data['flight_lines'] = flight_lines
    data['start_time_strip'] = start_time_strip
    data['end_time_strip'] = end_time_strip
    data['amount_of_points'] = amount_points
    data['duration_strip_seconds'] = duration_strip_seconds #s
    data['estimated_dist_strip'] = estimated_distances #m
    data['estimated_speed_strip_m_per_s'] = speed_strip #m/s
    data['trj_x_start'] = start_xs
    data['trj_y_start'] = start_ys
    data['trj_z_start'] = start_zs
    data['trj_x_end'] = end_xs
    data['trj_y_end'] = end_ys
    data['trj_z_end'] = end_zs
    data['mean_roll'] = average_roll #deg
    data['mean_pitch'] = average_pitch #deg
    data['mean_heading'] = average_heading #deg

    df_data = pd.DataFrame.from_dict(data)
    unique_flight_numbers = df_data.flight_numbers.unique()
    for flight_nr in unique_flight_numbers:
        # Find all data for the current flight nr and export 
        df_data_flight_nr = df_data.loc[df_data['flight_numbers']==flight_nr]

        # Estimate overlap between strips
        unique_strip_numbers = df_data_flight_nr.flight_lines.unique()
        distances  = []

        for i in range(len(unique_strip_numbers)-1):
            # get coords strip 1
            strip_nr1 = unique_strip_numbers[i]
            df_strip1 = df_data_flight_nr.loc[df_data_flight_nr['flight_lines']==strip_nr1]
            start_line1 = (df_strip1.trj_x_start.to_numpy()[0], df_strip1.trj_y_start.to_numpy()[0])
            end_line1 = (df_strip1.trj_x_end.to_numpy()[0], df_strip1.trj_y_end.to_numpy()[0])

            # get coords strip 2
            strip_nr2 = unique_strip_numbers[i+1]
            df_strip2 = df_data_flight_nr.loc[df_data_flight_nr['flight_lines']==strip_nr2]
            start_line2 = (df_strip2.trj_x_start.to_numpy()[0], df_strip2.trj_y_start.to_numpy()[0])
            end_line2 = (df_strip2.trj_x_end.to_numpy()[0], df_strip2.trj_y_end.to_numpy()[0])

            distance = distance_between_lines(start_line1, end_line1, start_line2, end_line2)
            distances.append(distance)
            # print('dist', distance)

        # Median is chosen as this is more robust
        av_distance = np.median(distances)
        av_distances = np.ones(len(df_data_flight_nr))*av_distance
        df_data_flight_nr['avg_flightline_distance'] = av_distances

        # With the height the estimated overlap is calculated
        swath_width = 2*np.tan(35*np.pi/180)*height
        factor_overlap = (swath_width-av_distance)/swath_width
        factor_overlaps = np.ones(len(df_data_flight_nr))*factor_overlap
        df_data_flight_nr['factor_overlaps'] = factor_overlaps

        # Convert the integer to a string suitable for the file name
        number_string = str(flight_nr)
        while len(number_string) < 3:
            number_string = "0" + number_string

        # Create filename and export path
        export_filename = 'F'+number_string+'-'+'global_information_flight.csv'
        export_path = os.path.join(folder_path, export_filename)

        # Find export data
        df_data_flight_nr.to_csv(export_path, index = False, sep = ',')

    if save_additional_trj_file_with_strips:


            # Find estimated horizontal distance of UAV strip
        flight_number = time_data[2]
        df_trj = pd.read_csv(paths_trj[flight_number])
        index_start_time = find_nearest_idx(df_trj['time'], time_data[0])
        index_end_time = find_nearest_idx(df_trj['time'], time_data[1])