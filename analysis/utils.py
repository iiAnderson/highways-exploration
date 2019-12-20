import pandas as pd
import plotly.express as px
import glob

cols = ["Local Date","Local Time","Day Type ID","Total Carriageway Flow","Total Flow vehicles less than 5.2m","Total Flow vehicles 5.21m - 6.6m","Total Flow vehicles 6.61m - 11.6m","Total Flow vehicles above 11.6m","Speed Value","Quality Index", "Network Link Id", "NTIS Model Version"]

def read_data(data_dir, csv_file=None):
    path = f"data/{data_dir}"

    if csv_file is not None:
        all_files = [f"{path}/{csv_file}.csv"]
    else:
        all_files = glob.glob(f"{path}/*.csv")

    df = pd.concat([pd.read_csv(f"{f}") for f in all_files ])

    return df

def get_all_files(data_dir):
    path = f"data/{data_dir}"

    return glob.glob(f"{path}/*.csv")

    