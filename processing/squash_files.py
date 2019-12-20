from os import listdir
from os.path import isfile, join
import pandas as pd

mypath = "output/"

files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

file_outputs = {}

for f in files:
    split_file = f.split("^")[0]

    if split_file in file_outputs:
        file_outputs[split_file].append(f)
    else:
        file_outputs[split_file] = [f]

for key_file in file_outputs:

    print(f"Processing {key_file}")
    key_name = key_file.split("^")[0].split(".")[0].strip()
    list_files = file_outputs[key_file]
    print(list_files)

    cols = ["Local Date","Local Time","Day Type ID","Total Carriageway Flow","Total Flow vehicles less than 5.2m","Total Flow vehicles 5.21m - 6.6m","Total Flow vehicles 6.61m - 11.6m","Total Flow vehicles above 11.6m","Speed Value","Quality Index", "Network Link Id", "NTIS Model Version"]

    concat = []
    for f in list_files:
        temp_df = pd.read_csv(f"output/{f}", names=cols).iloc[4:]
        temp_df = temp_df[temp_df['Local Date'] != "Local Date"]

        concat.append(temp_df)


    combined_csv = pd.concat(concat)
    #export to csv
    combined_csv.to_csv(f"data/m1/{key_name}.csv")