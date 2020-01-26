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
        self.data_entry = aggregate_times_by_carraige_flow(data_entry) if data_entry is not None else {}
        self.data_exit = aggregate_times_by_carraige_flow(data_exit) if data_exit is not None else {}
        self.data = aggregate_times_by_carraige_flow(data) if data is not None else {}

    def print(self, n=0, single=False):
        print(f" - Node {n}: J{self.name}")
        print(f"     entry: {self.data_entry}")
        print(f"     junc: {self.data}")
        print(f"     exit: {self.data_exit}")
        print("             ")

        if self.next is None or single:
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
        i = 0

        for junction_key, junction_objects in dataset:
            n = Node(prev_node, junction_key, self.read_object_data(junction_objects, 'a'), self.read_object_data(junction_objects, 'j'), self.read_object_data(junction_objects, 'e'))

            if linked_list is None:
                linked_list = n

            prev_node = n
            i += 1

        linked_list.print()
        times = linked_list.data_entry.keys()

        data = [[] for k in times]

        n_d = self.parse_nodes(prev_node, data, times)

        # prev_node.print()
        self.data = n_d
        self.x_axis = self.get_node_labels(prev_node, [])
        self.y_axis = list(times)
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
            plt.savefig(f"img/network/{self_result['name']}-{self.motorway}.png", dpi=100)

        self.next(self.end)

    @step
    def end(self):
        pass

    def get_node_labels(self, node, labels):

        labels.append(f"{node.name}j")
        labels.append(f"{node.name}")

        if node.next is None:
            return labels
        else:
            return self.get_node_labels(node.next, labels)

    def parse_nodes(self, node, data, times):

        for index, hour in enumerate(times):

            if node.data:
                data[index].append(node.data[hour])

            if node.data_entry and node.data_exit:
                try:
                    data[index].append(node.data_entry[hour]-node.data_exit[hour])
                except Exception as e:
                    print(data[index])
                    node.print(single=True)
                    raise e


        if node.next is not None:
            return self.parse_nodes(node.next, data, times)
        else:
            return data


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