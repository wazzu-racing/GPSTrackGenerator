from RustCode.file_parser import FileParser
from SplineInterpolator import Interpolator
from Visualizer import Visualizer


class Main:
    def __init__(self):
        parser = FileParser()
        interpolator = Interpolator(parser.raw_path_data)
        visualizer = Visualizer(parser.raw_path_data, parser.folders, interpolator.interpolated_path_data)
        visualizer.center_all_settings()
        visualizer.graph_all_settings(interpolate=False)

main = Main()