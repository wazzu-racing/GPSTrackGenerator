import math
import numpy as np
from scipy.interpolate import CubicSpline


class Interpolator:
    def __init__(self, raw_path_data):
        self.raw_path_data = raw_path_data

        self.interpolated_path_data = []

        # self.generate_all_splines(graby_points=2)

    class InterpSetting:
        def __init__(self, setting_number):
            self.setting_number = setting_number
            self.paths = []

    class InterpPath:
        def __init__(self):
            self.segments = []

    class InterpSegment:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    def generate_all_splines(self, graby_points):
        for setting_index, setting in enumerate(self.raw_path_data):
            self.interpolated_path_data.append(self.InterpSetting(setting.setting_number))
            for path_index, path in enumerate(setting.paths):
                self.interpolated_path_data[-1].paths.append(self.InterpPath())
                for segment_index in range(len(path.segments)-1):
                    # Grab the last points of the current segment and the starting points of the next segment.
                    path.segments[segment_index].calculate_all_points()
                    path.segments[segment_index+1].calculate_all_points()
                    points_x = path.segments[segment_index].x[-graby_points:]+path.segments[segment_index+1].x[:graby_points]
                    points_y = path.segments[segment_index].y[-graby_points:]+path.segments[segment_index+1].y[:graby_points]
                    # Calculate the differences between each x and y value.
                    diff_x, diff_y = [], []
                    for i in range(len(points_x)-1):
                        diff_x.append(points_x[i+1] - points_x[i])
                        diff_y.append(points_y[i+1] - points_y[i])
                    # Calculate the distances between each point and make a cumulative summation array "t".
                    dists, t = [], [0.0]
                    for i in range(len(diff_x)):
                        dists.append(math.sqrt(diff_x[i]**2 + diff_y[i]**2))
                        t.append(np.sum(dists))
                    spline_x = CubicSpline(np.array(t), y=points_x, bc_type="clamped")
                    spline_y = CubicSpline(np.array(t), y=points_y, bc_type="clamped")
                    eval_x = spline_x(np.linspace(t[0], t[-1], 100))
                    eval_y = spline_y(np.linspace(t[0], t[-1], 100))

                    # Append segment into interpolated_path_data
                    interp_seg = self.InterpSegment(eval_x, eval_y)
                    self.interpolated_path_data[-1].paths[-1].segments.append(interp_seg)