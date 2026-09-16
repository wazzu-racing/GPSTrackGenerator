import tkinter

import numpy as np
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch


class Visualizer:
    def __init__(self, raw_path_data, files, interpolated_path_data=None):
        self.raw_path_data = raw_path_data
        self.interpolated_path_data = interpolated_path_data

        self.files = files

        self.colors = ["red", "green", "blue", "teal", "magenta", "cyan", "orange", "lime", "purple", "maroon"]

    def center_all_settings(self):
        arc_x, arc_y = [], []
        for segment in self.raw_path_data[0].paths[0].segments:
            arc_x += segment.x
            arc_y += segment.y
        arc_x_avg, arc_y_avg = np.average(arc_x), np.average(arc_y)

        for setting_index, setting in enumerate(self.raw_path_data):
            for path_index, path in enumerate(setting.paths):
                if path_index == 0 and setting_index == 0:
                    continue

                # Calculate average for this path
                curr_arc_x, curr_arc_y = [], []
                for segment in path.segments:
                    curr_arc_x += segment.x
                    curr_arc_y += segment.y
                path_x_avg, path_y_avg = np.average(curr_arc_x), np.average(curr_arc_y)

                distance_x, distance_y = path_x_avg - arc_x_avg, path_y_avg - arc_y_avg

                for segment_index, segment in enumerate(path.segments):
                    self.raw_path_data[setting_index].paths[path_index].segments[segment_index].x -= distance_x
                    self.raw_path_data[setting_index].paths[path_index].segments[segment_index].y -= distance_y

                # Do the same thing for interpolated stuff
                if self.interpolated_path_data is not None:
                    for interp_segment_index, interp_segment in enumerate(self.interpolated_path_data[setting_index].paths[path_index].segments):
                        for i in range(len(interp_segment.x)):
                            self.interpolated_path_data[setting_index].paths[path_index].segments[interp_segment_index].x[i] -= distance_x
                            self.interpolated_path_data[setting_index].paths[path_index].segments[interp_segment_index].y[i] -= distance_y

    def graph_all_settings(self, interpolate=False):
        tk = tkinter.Tk()
        fig = Figure(figsize=(10, 10), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, tk)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, tk)
        canvas.get_tk_widget().pack()
        toolbar.update()

        if interpolate:
            for setting_index, setting in enumerate(self.interpolated_path_data):
                for path in setting.paths:
                    for segment in path.segments:
                        ax.plot(segment.x, segment.y, color=self.colors[setting_index], alpha=0.5)

        legend = []
        for setting_index, setting in enumerate(self.raw_path_data):
            legend.append(Patch(facecolor=self.colors[setting_index], label=f"Setting {setting.setting_number}".split('/')[
                -1]))
            for path in setting.paths:
                for segment in path.segments:
                    ax.plot(segment.x, segment.y, color=self.colors[setting_index])

        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.legend(handles=legend)
        ax.grid()
        tk.mainloop()