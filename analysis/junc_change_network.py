from utils import get_all_files, read_data, get_files_for_motorway, get_junc_exit_data, get_link_data
from tools import aggregate_times_by_carraige_flow
from metaflow import FlowSpec, step, Parameter
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd

class Node():

    def __init__(self, node, name, data_entry, data, data_exit):

        self.next = node
        self.name = name
        self.data_entry = data_entry
        self.data_exit = data_exit
        self.data = data

    def print(self, n=0):
        print(f" - Node {n}: J{self.name}")
        print(f"     entry: {self.data_entry is not None}")
        print(f"     junc: {self.data is not None}")
        print(f"     exit: {self.data_exit is not None}")
        print("             ")

        if self.next is None:
            print(" END ")
            return

        self.next.print(n+1)

class JunctionChangeNetworkFlow(FlowSpec):
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
        datasets = {name:{} for name in self.dataset_names}
        test = {name:{} for name in self.dataset_names}

        for file_name in self.files:
            try:
                split_name = file_name.split(" ")

                to_junc, junc_prefix = get_link_data(split_name)

                if to_junc is None:
                    to_junc, junc_prefix = get_junc_exit_data(split_name)
                
                if to_junc is None:
                    continue

                direction = self.multiple_contains(file_name, self.dataset_names)
                if direction:

                    if to_junc in datasets[direction]:
                        datasets[direction][to_junc][junc_prefix].append(file_name)
                        test[direction][to_junc][junc_prefix] = True
                    else:

                        test[direction][to_junc] = {
                            "j": False,
                            "a": False,
                            "e": False,
                        }
                        test[direction][to_junc][junc_prefix] = True

                        obj = {
                            "j": [],
                            "a": [],
                            "e": [],
                        }
                        obj[junc_prefix].append(file_name)

                        datasets[direction][to_junc] = obj
            except:
                print(file_name)

        new_data = {}
        for key in datasets.keys():
            
            vals = [None for x in range(0, 1000)]

            for k, v in datasets[key].items():
                vals[int(k)] = [k, v]

            new_data[key] = [x for x in vals if x]
        
        self.datasets = [[k, v] for k, v in new_data.items()]

        self.next(self.process_dataset, foreach='datasets')

    @step
    def process_dataset(self):
        dataset = self.input[1]
        dataset_name = self.input[0]

        linked_list = None
        prev_node = None

        for junction_key, junction_objects in dataset:
            n = Node(prev_node, junction_key, self.read_object_data(junction_objects, 'a'), self.read_object_data(junction_objects, 'j'), self.read_object_data(junction_objects, 'e'))

            if linked_list is None:
                linked_list = n

            prev_node = n

        prev_node.print()
        self.next(self.join)

    @step
    def join(self, inputs):
        # self.processing_results = [{"data": i.data, "x_axis": i.x_axis, "y_axis": i.y_axis, "name": i.dataset_name} for i in inputs]
        self.next(self.save_plots)

    @step
    def save_plots(self):

        self.next(self.end)

    @step
    def end(self):
        pass

    def read_object_data(self, junction_objects, key):

        if len(junction_objects[key]) != 0:

            d = []

            for file_name in junction_objects[key]:
                file_split = file_name.split("/")
                data = read_data(file_split[1], file_split[2].split(".")[0])

                d.append(data)

            if len(d) == 0:
                return None

            return pd.concat(d)
        return None


    def multiple_contains(self, string, lst):
        for l in lst:
            if l in string:
                return l
        return None

    def calc_junc_change(self, access, ex):
        ret_dict = {}
        # dict time: mean_flow
        for key in access:
            try:
                ret_dict[key] = access[key] - ex[key]
            except Exception as e:
                print(access)
                print(ex)
                raise e
        return ret_dict
        
if __name__ == '__main__':
    JunctionChangeNetworkFlow()