from ..utils import get_all_files, read_data, get_files_for_motorway
from ..tools import aggregate_times_by_carraige_flow
from metaflow import FlowSpec, step, Parameter
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd

import re


class HeatMapTimeByTotalTrafficFlow(FlowSpec):
    motorway = Parameter('motorway',
                      help='Motorway',
                      default="M32")
    direction = Parameter('direction',
                      help='Direction',
                      default="ns")
    @step
    def start(self):

        if self.direction == "ns":
            self.dataset_names = ["northbound", "southbound"]
        else:
            self.dataset_names = ["eastbound", "westbound"]

        file_paths = get_files_for_motorway("m26", self.motorway)

        self.files = list(filter(lambda f: self.dataset_names[0] in f or self.dataset_names[1] in f, file_paths))

        self.next(self.initial_process)

    @step
    def initial_process(self):
        datasets = {name:[] for name in self.dataset_names}
        for file_name in self.files:
            split_name = file_name.split(" ")

            between_char_index = self.index(split_name, "between")
            within_char_index = self.index(split_name, "within")
            tame_char_index = self.index(split_name, "GPS")

            if between_char_index != -1:
                to_junc = re.sub('[^0-9]','', split_name[between_char_index+1])
            else:
                if (within_char_index != -1 and tame_char_index == -1): 
                    print(split_name)
                    to_junc = re.sub('[^0-9]','', split_name[within_char_index+1])
                else:
                    continue 


            direction = self.multiple_contains(file_name, self.dataset_names)
            if direction:
                datasets[direction].append([to_junc, file_name])

        for key in datasets.keys():
            datasets[key].sort(key=lambda x: int(x[0]), reverse=True)
        print(datasets)
        self.datasets = [[k, v] for k, v in datasets.items()]

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
            fig, ax = plt.subplots()
            ax.imshow(np.array(self_result['data']))

            ax.set_xticks(np.arange(len(self_result['x_axis'])))
            ax.set_yticks(np.arange(len(self_result['y_axis'])))

            ax.set_xticklabels(self_result['x_axis'], fontsize=12)
            ax.set_yticklabels(self_result['y_axis'], fontsize=12)

            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                    rotation_mode="anchor")
            fig = plt.gcf()
            fig.set_size_inches(20, 15)
            plt.savefig(f"img/{self_result['name']}-{self.motorway}.png", dpi=100)

        self.next(self.end)

    @step
    def end(self):
        pass

    def multiple_contains(self, string, lst):
        for l in lst:
            if l in string:
                return l
        return None

    def index(self, lst, contains_str):
        try:
            return lst.index(contains_str)
        except:
            return -1

        
if __name__ == '__main__':
    HeatMapTimeByTotalTrafficFlow()