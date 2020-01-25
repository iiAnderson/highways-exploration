import pandas as pd
import plotly.express as px
import glob
import re

cols = ["Local Date","Local Time","Day Type ID","Total Carriageway Flow","Total Flow vehicles less than 5.2m","Total Flow vehicles 5.21m - 6.6m","Total Flow vehicles 6.61m - 11.6m","Total Flow vehicles above 11.6m","Speed Value","Quality Index", "Network Link Id", "NTIS Model Version"]

def read_data(data_dir, csv_file=None):
    path = f"data/{data_dir}"

    if csv_file is not None:
        all_files = [f"{path}/{csv_file}.csv"]
    else:
        all_files = glob.glob(f"{path}/*.csv")

    df = pd.concat([pd.read_csv(f"{f}") for f in all_files ])

    return df

def get_all_files(data_dir, filter_str=None):
    path = f"data/{data_dir}"

    files = glob.glob(f"{path}/*.csv")

    if filter_str:
        files = list(filter(lambda x: f"{filter_str} " in x or f"{filter_str}a " in x, files))
    
    return files

def get_files_for_motorway(data_dir, motorway):
    return get_all_files(data_dir, filter_str=motorway)

def get_link_data(split_name):

    to_junc = None

    between_char_index = index_util(split_name, "between")
    within_char_index = index_util(split_name, "within")
    tame_char_index = index_util(split_name, "GPS")

    if between_char_index != -1:
        to_junc = re.sub('[^0-9]','', split_name[between_char_index+1])
    else:
        if (within_char_index != -1 and tame_char_index == -1): 
            to_junc = re.sub('[^0-9]','', split_name[within_char_index+1])

    return to_junc, "j"

def get_junc_exit_data(split_name):

    to_junc = None
    junc_prefix = None

    exit_char_index = index_util(split_name, "exit")
    access_char_index = index_util(split_name, "access")

    if exit_char_index != -1:
        to_junc = re.sub('[^0-9]','', split_name[exit_char_index-2])
        junc_prefix = "e"
    else:
        if access_char_index != -1: 
            to_junc = re.sub('[^0-9]','', split_name[access_char_index-2])
            junc_prefix = "a"

    return (to_junc, junc_prefix)

def index_util(lst, contains_str):
    try:
        return lst.index(contains_str)
    except:
        return -1