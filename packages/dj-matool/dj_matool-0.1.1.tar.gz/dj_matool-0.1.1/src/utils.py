import pandas as pd
import numpy as np
import csv


def read_data(is_excel_or_csv, file_name):
    """
    This method will read file. It will read excel if flag is 1, or it will read csv
    :param is_excel_or_csv:
    :return: df
    """
    if is_excel_or_csv:
        df = pd.read_excel(str(file_name))
    else:
        df = pd.read_csv(str(file_name))
    return df

def converting_data_frame_to_dict_form(df):
    """
    This method will convert data frame into dictionary form.
    :return: dict_df
    """
    df_dict = {}
    for i in range(len(df)):
        df_dict[i] = []
        df_dict[i].append(df.iloc[i].to_dict())
    return df_dict

def generate_big_stick_possible_combinations(lower_range_width, upper_range_width, lower_range_depth, upper_range_depth,
                                             width_step_size, depth_step_size):
    """

    :param lower_range_width:
    :param upper_range_width:
    :param lower_range_depth:
    :param upper_range_depth:
    :param width_step_size:
    :param depth_step_size:
    :return:
    """
    big_stick_possible_combinations = []
    for width_stick_size in np.arange(lower_range_width, upper_range_width, width_step_size):
        for depth_stick_size in np.arange(lower_range_depth, upper_range_depth, depth_step_size):
            if depth_stick_size > width_stick_size:
                continue
            big_stick_possible_combinations.append((width_stick_size, depth_stick_size))
    big_stick_width_combinations = []
    for width_stick_size in np.arange(lower_range_width, upper_range_width, width_step_size):
        big_stick_width_combinations.append(width_stick_size)
    big_stick_depth_combinations = []
    for depth_stick_size in np.arange(lower_range_depth, upper_range_depth, depth_step_size):
        big_stick_depth_combinations.append(depth_stick_size)
    return big_stick_possible_combinations, big_stick_width_combinations, big_stick_depth_combinations

def store_dict_to_csv(dict_to_save, file_name, key_header_name, value_header_name):
    """
    Order of row will not matter
    every key will be first element
    value will be second element.
    :param dict_to_save:
    :return:
    """
    f = open(file_name, 'w+')
    writer = csv.writer(f)
    writer.writerow([key_header_name, value_header_name])
    for key,value in dict_to_save.items():
        writer.writerow([key, value])
    f.close()
    pass