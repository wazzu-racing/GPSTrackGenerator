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

        self.parse_all_data(["write_millis","lat","lon"])

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

    def parse_all_arcs(self):
        for index, folder in enumerate(self.results):
            curr_setting = self.Setting(index)
            if os.listdir(self.folders[index]):
                self.raw_path_data.append(curr_setting) # Each array is a setting
            for file in folder:
                curr_path = self.CarPath()
                self.raw_path_data[-1].paths.append(curr_path) # Each array is another run
                curr_file = open(file, "r")
                reader = csv.reader(curr_file, delimiter=',')

                segments, arcs = [], []
                curr_segment_id, prev_segment_id = 0, 0
                curr_segment = None
                for index, line in enumerate(reader):
                    if index == 0:
                        continue

                    curr_segment_id = int(line[0])
                    if curr_segment_id != prev_segment_id:
                        if curr_segment is not None:
                            curr_segment.arcs = arcs
                            segments.append(curr_segment)
                            curr_segment = self.Segment(curr_segment_id)
                            arcs = [self.Arc(int(line[1]), start_x=float(line[7]), start_y=float(line[8]),
                                             end_x=float(line[9]), end_y=float(line[10]))]
                        else:
                            curr_segment = self.Segment(curr_segment_id)
                            arcs.append(self.Arc(int(line[1]), start_x=float(line[7]), start_y=float(line[8]),
                                                 end_x=float(line[9]), end_y=float(line[10])))
                    else:
                        arcs.append(self.Arc(int(line[1]), start_x=float(line[7]), start_y=float(line[8]),
                                             end_x=float(line[9]), end_y=float(line[10])))
                    prev_segment_id = curr_segment_id

                self.raw_path_data[-1].paths[-1].segments = segments

    def parse_all_data(self, columns):
        # Take all file names and put them into dictionary self.files
        self.files = {}
        for folder in Path(os.getcwd()+"/Data").iterdir():
            self.files[str(folder)] = []
            for file in folder.iterdir():
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
                with open(file, "r") as f:
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
                    "write_millis"))])
                x = np.array(self.raw_path_data[key][file][self.indices.index(self.titles.index("lon"))])
                y = np.array(self.raw_path_data[key][file][self.indices.index(self.titles.index("lat"))])

                # Remove 0's
                bad_indices = []
                for index, ele in enumerate(x):
                    if ele == 0:
                        bad_indices.append(index)
                time = np.array([])
                for index, t in enumerate(temp_time):
                    if index not in bad_indices:
                        time = np.append(time, t)
                x = x[x != 0]
                y = y[y != 0]

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