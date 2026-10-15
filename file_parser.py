import csv
import os
import subprocess
from copy import deepcopy
from pathlib import Path
import shutil
import numpy as np
from matplotlib import pyplot as plt


class FileParser:
    def __init__(self):
        self.raw_path_data_org = []
        self.raw_path_data = []
        self.titles = []
        self.indices = []

        self.created_exe = False
        self.files = {}

        self.data_titles = ["Millis_Uptime","Latitude_Deg","Longitude_Deg"]
        self.parse_all_data(self.data_titles)

    class Setting:
        def __init__(self, setting_number):
            self.setting_number = setting_number
            self.paths = []

    class CarPath:
        def __init__(self):
            self.segments = []

    class Segment:
        def __init__(self, segment_id):
            self.segment_id = segment_id
            self.x, self.y = [], []

    def parse_all_data(self, columns):
        # Take all file names and put them into dictionary self.files
        self.files = {}
        for folder in Path(os.getcwd()+"/Data").iterdir():
            if not folder.name.startswith("."):
                self.files[str(folder)] = []
                for file in folder.iterdir():
                    if not file.name.startswith("."):
                        self.files[str(folder)].append(str(file))

        # Make new dictionary data_arr based on self.files
        self.raw_path_data = deepcopy(self.files)
        for key in self.files.keys():
            self.raw_path_data[key] = {}
        for key, value in self.files.items():
            for val in value:
                self.raw_path_data[key][val] = []

        # Parse data into data_arr
        for key, value in self.files.items():
            for file in value:
                self.indices = []
                with open(file, "r", encoding='cp1252') as f:
                    reader = csv.reader(f, delimiter=',')
                    for index, line in enumerate(reader):
                        if index == 0:
                            self.titles = line
                            for data_index, name in enumerate(line):
                                if name in columns:
                                    self.raw_path_data[key][file].append([])
                                    self.indices.append(data_index)
                        else:
                            for data_index, data in enumerate(line):
                                if data_index in self.indices:
                                    self.raw_path_data[key][str(file)][self.indices.index(data_index)].append(float(
                                        data))

        # Organize data into arrays and classes
        for key, value in self.raw_path_data.items():
            self.raw_path_data_org.append(self.Setting(int(str(key)[-1])))
            for file in value:

                # Get x and y values from the file
                self.raw_path_data_org[-1].paths.append(self.CarPath())
                temp_time = np.array(self.raw_path_data[key][file][self.indices.index(self.titles.index(
                    "Millis_Uptime"))])
                temp_x = np.array(self.raw_path_data[key][file][self.indices.index(self.titles.index("Longitude_Deg"))])
                temp_y = np.array(self.raw_path_data[key][file][self.indices.index(self.titles.index("Latitude_Deg"))])

                # create array for nans
                nan_indices = []
                for index, i in enumerate(temp_x):
                    if np.isnan(i):
                        nan_indices.append(index)
                # create array for 0's
                zero_indices = []
                for index, ele in enumerate(temp_x):
                    if ele == 0:
                        zero_indices.append(index)
                time = np.array([])
                x = np.array([])
                y = np.array([])
                # Remove both
                for index, t in enumerate(temp_time):
                    if index not in zero_indices and index not in nan_indices:
                        time = np.append(time, t)
                        x = np.append(x, temp_x[index])
                        y = np.append(y, temp_y[index])

                # Organize into arcs and segments
                prev_time = time[0]
                segs = []
                curr_seg = self.Segment(0)
                for index, t in enumerate(time):
                    if index > 0 and x[index] != x[index - 1] and y[index] != y[index - 1]:
                        if float(t) - float(prev_time) > 150: # If the data logger cuts out for an extended period
                            segs.append(curr_seg)
                            curr_seg = self.Segment(segs[-1].segment_id+1)
                        else:
                            curr_seg.x.append(x[index])
                            curr_seg.y.append(y[index])
                    prev_time = t

                # Remove bad segments
                for index, seg in enumerate(segs):
                    if len(seg.x) < 2:
                        segs.remove(seg)

                self.raw_path_data_org[-1].paths[-1].segments = segs