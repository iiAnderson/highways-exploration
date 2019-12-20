from csv_file import CSVFile

def reducer(header, row):

    if row[header.index("road_name")] == "M4":
        return row
    return None

f = CSVFile('data/counts_raw.csv')
f.add_filter(reducer)

f.to_file('output/m4.csv')