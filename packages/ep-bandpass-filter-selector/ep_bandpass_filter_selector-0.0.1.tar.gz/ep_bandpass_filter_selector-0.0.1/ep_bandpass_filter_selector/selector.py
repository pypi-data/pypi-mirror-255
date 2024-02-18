import csv
import numpy as np
from itertools import combinations
from loguru import logger

from eeg_filters.filters import make_filter, search_max_min


class PassbandSelector:
    """
    Class to implement the selection of a bandpass filter.
    """

    def __init__(
        self,
        curves: list,
        tick_times: list,
        fsr: int,
        max_search_range: tuple,
        min_search_range: tuple,
        **kwargs,
    ) -> None:
        """
        Initialization of an item.
        """
        self.filter_low_limit_range = 1, 30
        self.step_low_filter = 1
        self.filter_high_limit_range = 100, 500
        self.step_high_filter = 10
        self.type_mean = "average"
        self.cheb_filter_order = 3
        self.cheb_ripple = 3

        self.curves = curves
        self.tick_times = tick_times
        self.frequency_sample_rate = fsr
        self.max_search_range = max_search_range
        self.min_search_range = min_search_range

        if "fllr" in kwargs:
            self.filter_low_limit_range = kwargs["fllr"]
        if "filter_low_limit_range" in kwargs:
            self.filter_low_limit_range = kwargs["filter_low_limit_range"]
        self.filter_low_limit_range = [int(x) for x in self.filter_low_limit_range]
        if "fhlr" in kwargs:
            self.filter_high_limit_range = kwargs["fhlr"]
        if "filter_high_limit_range" in kwargs:
            self.filter_high_limit_range = kwargs["filter_high_limit_range"]
        self.filter_high_limit_range = [int(x) for x in self.filter_high_limit_range]
        if "slf" in kwargs:
            self.step_low_filter = kwargs["slf"]
        if "step_low_filter" in kwargs:
            self.step_low_filter = kwargs["step_low_filter"]
        self.step_low_filter = int(self.step_low_filter)
        if "shf" in kwargs:
            self.step_high_filter = kwargs["shf"]
        if "step_high_filter" in kwargs:
            self.step_high_filter = kwargs["step_high_filter"]
        self.step_high_filter = int(self.step_high_filter)
        if "tm" in kwargs:
            self.type_mean = kwargs["tm"]
        if "type_mean" in kwargs:
            self.type_mean = kwargs["type_mean"]
        if "chfo" in kwargs:
            self.cheb_filter_order = kwargs["chfo"]
        if "cheb_filter_order" in kwargs:
            self.cheb_filter_order = kwargs["cheb_filter_order"]
        self.cheb_filter_order = int(self.cheb_filter_order)
        if "chr" in kwargs:
            self.cheb_ripple = kwargs["chr"]
        if "cheb_ripple" in kwargs:
            self.cheb_ripple = kwargs["cheb_ripple"]
        self.cheb_ripple = int(self.cheb_ripple)

        logger.info(f"TYPE: {type(self.filter_low_limit_range[0])}")

        self.filtered_curves = []
        self.filter_by_optimum = {}
        self.optimums = []
        self.optimum_matrix = {}

    def get_reproduct(self, filtered_curves: list) -> float:
        """
        Calculates the average reproducibility of the filtered curves.

        Parameters:
            filtered_curves(list): List of filtered curves.

        Returns:
            (float): The average reproducibility.
        """
        integrals = []
        for curve1, curve2 in combinations(filtered_curves, 2):
            integral = self.get_integral(curve1, curve2)
            integrals.append(integral)
        if self.type_mean == "average":
            ave_integral = sum(integrals) / len(integrals)
        # elif self.check_square:
        #     ave_integral = self.get_square_mean(integrals)
        return ave_integral

    def get_delta_extremum(self, filtered_curves: list) -> float:
        """
        Calculates the average difference in extrema for the list
        of filtered curves.

        Parameters:
            filtered_curves(list): List of the filtered curves.

        Returns:
            (float): The average difference in extrema.
        """
        deltas = []
        for curve in filtered_curves:
            curve_max = search_max_min(
                self.tick_times, curve, self.max_search_range, "max"
            )
            curve_min = search_max_min(
                self.tick_times, curve, self.min_search_range, "min"
            )
            deltas.append(curve_max[1] - curve_min[1])
        return sum(deltas) / len(deltas)

    def get_integral(self, curve1: list, curve2: list) -> float:
        """
        Calculates the integral of the absolute difference of curves.

        Parameters:
            curve1(list): List of values from the first curve.
            curve2(list): List of values from the second curve.

        Returns:
            (float): The value of the integral of the absolute difference.
        """
        return np.trapz(np.absolute(np.subtract(curve1, curve2)))

    def filter_curves(self, lb: int, hb: int) -> list:
        """
        Filters curves using the eeg_filters library.

        Parameters:
            lb(int): The low border of the bandpass filter.
            hb(int): The high border of the pandpass filter.

        Returns:
            (list): list of values from the filtered curve.
        """
        filtered_curves = []
        for curve in self.curves:
            filtered_curve = make_filter(
                curve,
                (lb, hb),
                self.frequency_sample_rate,
                self.cheb_filter_order,
                self.cheb_ripple,
            )
            filtered_curves.append(filtered_curve)
        return filtered_curves

    def start(self) -> tuple:
        """
        Initiates the main process of selecting the optimal bandpass filter.
        """
        heatmap_data = []
        head_row = []
        head_row_created = False
        for lb in range(
            self.filter_low_limit_range[0],
            self.filter_low_limit_range[1] + self.step_low_filter,
            self.step_low_filter,
        ):
            data_row = []
            for hb in range(
                self.filter_high_limit_range[0],
                self.filter_high_limit_range[1] + self.step_high_filter,
                self.step_high_filter,
            ):
                if not head_row_created:
                    head_row.append(hb)
                filtered_curves = self.filter_curves(lb, hb)
                reproduct = self.get_reproduct(filtered_curves)
                delta_extrmums = self.get_delta_extremum(filtered_curves)
                optimum = reproduct / delta_extrmums
                data_row.append(optimum)
                self.optimums.append(optimum)
                self.filter_by_optimum[optimum] = (lb, hb)
            if not head_row_created:
                heatmap_data.append(["-"] + head_row)
                head_row_created = True
            heatmap_data.append([lb] + data_row)
        result_optimum = min(self.optimums)
        return (self.filter_by_optimum[result_optimum], heatmap_data)


def export_data(filepath: str, bandpass: list, data: list) -> None:
    """
    Exports data to file.

    Parameters:
        filepath(str): The path to the file for export data.
        bandpass(list): List of values of the selected bandpass filter.
        data(list): List of values of the optimality parameters.
    """
    with open(filepath, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(bandpass)
        writer.writerows(data)

    return True
