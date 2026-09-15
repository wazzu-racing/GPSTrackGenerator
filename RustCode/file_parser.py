import csv
import os
import subprocess
from pathlib import Path
import shutil

class FileParser:
    def __init__(self):
        self.raw_path_data = []

        self.created_exe = False
        self.folders = []
        self.files = []
        self.results = []

        self.rust_code_folder_name = "RustCode"

        self.parse_all_data()
        self.parse_all_arcs()

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
            self.arcs = []
            self.x, self.y = [], []

        def calculate_all_points(self):
            points_x, points_y = [], []
            for arc in self.arcs:
                points_x.append(arc.start_x)
                points_y.append(arc.start_y)
            points_x.append(self.arcs[-1].end_x)
            points_y.append(self.arcs[-1].end_y)
            self.x, self.y = points_x, points_y

    class Arc:
        def __init__(self, arc_id, start_x, start_y, end_x, end_y):
            self.arc_id = arc_id
            self.start_x = start_x
            self.start_y = start_y
            self.end_x = end_x
            self.end_y = end_y

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

    def parse_all_data(self):
        # Take all file names and put them into 2D array
        self.files = []
        for folder in Path(os.getcwd()+"/Data").iterdir():
            if not str(folder).endswith("Results"):
                self.files.append([])
                self.folders.append(str(folder))
                for file in folder.iterdir():
                    self.files[-1].append(str(file))

        # Create "Results" folder if it does not exist.
        results_dir_path = Path(os.getcwd()+"/Data/Results")
        if not os.path.isdir(results_dir_path):
            os.mkdir(results_dir_path)
        else: # If the "Results" folder exists, empty it.
            for folder in results_dir_path.iterdir():
                shutil.rmtree(folder)
        for folder in self.folders:
            os.mkdir(str(results_dir_path)+"/"+str(folder).split('/')[-1])

        # Go through files and run the rust code to get each corresponding "04_arcs.csv" file.
        self.results = []
        for index, folder in enumerate(self.files):
            self.results.append([])
            for file in folder:
                # Copy the csv file to RustCode
                shutil.copyfile(file, os.getcwd()+f"/{self.rust_code_folder_name}/data/data.csv")
                self.run_rust_code()

                # Copy resulting "04_arcs.csv" to results folder
                path = str(results_dir_path)+"/"+self.folders[index].split('/')[-1]+"/"+file.split('/')[-1]
                shutil.copyfile(os.getcwd()+f"/{self.rust_code_folder_name}/output/04_arcs.csv", path)
                self.results[-1].append(path)

    def run_rust_code(self):
        if not self.created_exe:
            # Paths
            self.working_dir = os.path.join(os.getcwd()+f"/{self.rust_code_folder_name}")
            self.rust_exe = os.path.join(self.working_dir, "target", "release", "gps-data-smoothing-v2")

            # Create an executable for the Rust code.
            subprocess.run(["cargo", "build", "--release"], cwd=self.working_dir, check=True)

            self.created_exe = True

        # Run the executable that was just created
        subprocess.run([self.rust_exe], cwd=self.working_dir, check=True)