import csv
import sys
import requests
import threading
import collections
import string
import random
import io
import zipfile
import re
import gc

file_path = "data/links/M40-M26.csv"
base_url = "http://tris.highwaysengland.co.uk/detail/journeytimedata"

exception_rows = []

midas_sites = {}

def random_string(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def download_extract_zip(url):
    """
    Download a ZIP file and extract its contents in memory
    yields (filename, file-like object) pairs
    """
    response = requests.get(url)
    file_rows = []

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_dir:
        for zipinfo in zip_dir.infolist():
            with zip_dir.open(zipinfo) as zip_file:
                for r in zip_file:
                    file_rows.append(r.decode('utf-8'))

    return file_rows

def add_midas_site(midas_id, data_tuple):
    if str(midas_id) in midas_sites:
        midas_sites[str(midas_id)].append(data_tuple)
    else:
        midas_sites[str(midas_id)] = [data_tuple]

def flush_data(midas_sites):
    print(f"Flushing data to file, writing {len(midas_sites.keys())} files.")
    for key in midas_sites:
        f_name, _ = midas_sites[key][0]
        with open(f'output/m26/{f_name}^{random_string(8)}.csv', 'w+', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            for f_name, f_data in midas_sites[key]:

                    for r in f_data[4:]:
                        csv_writer.writerow(r.split(","))

    midas_sites.clear()
    gc.collect()
    midas_sites = {}

def process(row):
    try:

        url = row[0]
        name = row[1]
        
        data = download_extract_zip(url)

        if re.search(r'\((.*?)\)', name) is None:
            midas_id = name.split(" ")[3]
        else:
            midas_id = re.search(r'\((.*?)\)', name).group(1)

        spl_name = name.split("at")

        if len(spl_name) > 1:
            name = spl_name[1]

        add_midas_site(midas_id, (name, data))
        

    except Exception as e:
        print("Exception writing file " + row[0])
        exception_rows.append(row)

 
with open(file_path) as f:
    reader = csv.reader(f, delimiter=',')

    threads = []
    total = 0
    row_number = 0

    for r in reader:

        if "download" in r[0]:
            x = threading.Thread(target=process, args=(r,))
            threads.append(x)
            row_number += 1

        if len(threads) >= 50:
            print(f"Processing batch {total}")

            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join() 
            total += len(threads)
 
            threads = []

        if total % 10000 == 0 and total == row_number and total != 0:
            flush_data(midas_sites)

    flush_data(midas_sites)

    for thread in threads:
        thread.start()
            
    for thread in threads:
        thread.join() 


    with open('error3.csv', 'w+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        for r in exception_rows:
            csv_writer.writerow(r)


