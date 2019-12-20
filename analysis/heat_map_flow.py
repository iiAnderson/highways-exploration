from utils import get_all_files, read_data
from tools import aggregate_times_by_carraige_flow
from metaflow import FlowSpec, step
import matplotlib.pyplot as plt
import numpy as np 

import re


class HeatMapTimeByTotalTrafficFlow(FlowSpec):

    @step
    def start(self):
        file_paths = get_all_files("m1")

        self.files = list(filter(lambda f: ("between" in f) and ("northbound" in f or "southbound" in f), file_paths))

        self.next(self.initial_process)

    @step
    def initial_process(self):
        northbound = []
        southbound = []
        for file_name in self.files:
            split_name = file_name.split(" ")

            between_char_index = split_name.index("between")

            from_junc = re.sub('[^0-9]','', split_name[between_char_index+3])
            to_junc = re.sub('[^0-9]','', split_name[between_char_index+1])

            if "southbound" in file_name:
                southbound.append([to_junc, file_name])
            else:
                northbound.append([to_junc, file_name])

        northbound.sort(key=lambda x: int(x[0]), reverse=True)
        southbound.sort(key=lambda x: int(x[0]), reverse=True)

        self.datasets = [("northbound", northbound), ("southbound", southbound)]

        self.next(self.process_dataset, foreach='datasets')

    @step
    def process_dataset(self):
        dataset = self.input[1]
        dataset_name = self.input[0]

        for p in dataset:
            file_name_split = p[1].split("/")
            temp_df = read_data(file_name_split[1], file_name_split[2].split(".")[0])

            p[1] = aggregate_times_by_carraige_flow(temp_df)

        y_axis = dataset[0][1].keys() # times
        x_axis = [p[0] for p in dataset] # junctions

        r = [[] for i in dataset[0][1].keys()]

        for i, t in enumerate(list(dataset[0][1].keys())):
            for p in dataset:
                try:
                    r[i].append(p[1][t])
                except Exception as e:
                    pass

        # data = np.array(r)

        self.data = r
        self.x_axis = list(x_axis)
        self.y_axis = list(y_axis)
        self.dataset_name = dataset_name
        self.next(self.join)

    @step
    def join(self, inputs):
        self.processing_results = [{"data": i.data, "x_axis": i.x_axis, "y_axis": i.y_axis, "name": i.dataset_name} for i in inputs]
        self.next(self.save_plots)


    @step
    def save_plots(self):

        for self_result in self.processing_results:
            _, ax = plt.subplots()
            ax.imshow(np.array(self_result['data']))

            ax.set_xticks(np.arange(len(self_result['x_axis'])))
            ax.set_yticks(np.arange(len(self_result['y_axis'])))

            ax.set_xticklabels(self_result['x_axis'])
            ax.set_yticklabels(self_result['y_axis'])

            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                    rotation_mode="anchor")

            plt.savefig(f"{self_result['name']}.png")

        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    HeatMapTimeByTotalTrafficFlow()