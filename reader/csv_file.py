import csv


class CSVFile():

    def __init__(self, file_path):

        self.csv_reader = csv.reader(open(file_path), delimiter=',')
        self.headers = self.get_csv_headers(self.csv_reader)
        self.filters = []


    def get_csv_headers(self, csv_reader):
        return next(csv_reader)

    def add_filter(self, func):
        self.filters.append(func)

    def to_file(self, output_location):
        output_rows = []
        i = 0

        for row in self.csv_reader:

            for func in self.filters:
                func_output = func(self.headers, row)

                if func_output:
                    output_rows.append(func_output)

            i += 1
            if i % 100000 == 0:
                print(f"Processed {i} Records")

        self._to_file(output_location, output_rows)
    
    def _to_file(self, output_location, rows):
        with open(output_location, mode='w') as output_file:

            writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(self.headers)

            for row in rows:
                writer.writerow(row)


