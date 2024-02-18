from .tools import check_params
from .filter_data import filter_and_save_data
from .filter_positions import filter_positions
from .plot_data_set_speed import plot_data_set_speed
from .plot_data_set_schedule import plot_data_set_schedule


def analyse_all(path: str, dataSet: int) -> None:
    check_params(path, dataSet)
    filter_and_save_data(path, dataSet)
    plot_data_set_speed(path, dataSet)
    filter_positions(path, dataSet)
    plot_data_set_schedule(path, dataSet)


def analyse_speed(path: str, dataSet: int = 1) -> None:
    check_params(path, dataSet)
    filter_and_save_data(path, dataSet)
    plot_data_set_speed(path, dataSet)


def analyse_schedule(path: str, dataSet: int = 1) -> None:
    check_params(path, dataSet)
    filter_and_save_data(path, dataSet)
    filter_positions(path, dataSet)
    plot_data_set_schedule(path, dataSet)
