from file_parser import FileParser
from SplineInterpolator import Interpolator
from Visualizer import Visualizer


class Main:
    def __init__(self):
        parser = FileParser()
        interpolator = Interpolator(parser.raw_path_data_org)
        visualizer = Visualizer(parser.raw_path_data_org, parser.files, interpolated_path_data=None)
        visualizer.center_all_settings()
        visualizer.graph_all_settings(interpolate=False)

main = Main()