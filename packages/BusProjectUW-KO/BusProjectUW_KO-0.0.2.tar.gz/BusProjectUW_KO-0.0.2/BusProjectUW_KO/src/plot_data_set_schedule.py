import json
import warnings
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.axes import Axes
from alive_progress import alive_it
from typing import Dict, Union, List, Tuple, Type
from .tools import bcolors


def prepare_plot(ax: Type[Axes], pos: Tuple[int, int], name: str, idx: int, data: Dict[int, int], color: Union[str, List[str]], xaxis_defalut: bool = True):
    '''Prepares the plot for the schedule plot. Can plot a single district or the summary data.'''

    total_count = sum(data.values())
    # Calculate percentages
    percentages = sorted([(key, (value / total_count) * 100) for key, value in data.items()])

    # Axes
    x_keys = [x[0] for x in percentages]
    y_values = [x[1] for x in percentages]

    # Prepare the plot
    ax[pos].bar(x_keys, y_values, width=1, color=color, edgecolor='black')
    ax[pos].set_title(f"{name}", fontsize=12 if xaxis_defalut else 8)

    if (idx is not None):
        ax[pos].text(1, 1.1, f"{idx}", transform=ax[pos].transAxes, ha='right', va='top')

    # Format y-axis tick labels as percentages
    formatter = mticker.PercentFormatter()
    ax[pos].yaxis.set_major_formatter(formatter)

    # Set font size for x and y labels
    ax[pos].tick_params(axis='x', labelsize=6)
    ax[pos].tick_params(axis='y', labelsize=6)

    # Set x-axis ticks to [0, 20, 40, 60] or to district names
    if (xaxis_defalut):
        ax[pos].set_xticks(range(0, 61, 5))
    else:
        warnings.filterwarnings("ignore")
        ax[pos].set_xticklabels(x_keys, rotation=45, ha='right', fontsize=4)
        warnings.filterwarnings("default")


def plot_data_set_schedule(path: str, dataSet: int = 1, show: bool = False) -> None:
    '''Plots the percentage of buses in each district of Warsaw that are delayed by a certain amount of time.'''

    # Colors for the plots
    colors = ["blue", "green", "red", "cyan", "magenta", "yellow", "blueviolet", "hotpink", "orange", "coral", "mediumspringgreen", "royalblue", "orangered", "lime", "khaki", "turquoise", "darkorange", "aquamarine", "dodgerblue"]

    # Load the filtered positions from the file
    with open(os.path.join(path, f"./FILTERED_DATA/FILTERED_POSITIONS/filtered_positions_{dataSet}.json"), "r") as file:
        data = json.load(file)

    # Calculate the time differences between the scheduled and actual bus times
    time_diffs = map(lambda x: ((x[0] // 60), x[1]), map(lambda x: (x["Time"], x["District"]), data))

    delay_per_district = dict()
    delay_total = dict()
    district_counter = dict()

    # Count the number of buses in each district and the number of buses delayed by a certain amount of time
    for time_diff in alive_it(time_diffs, title=bcolors.OKCYAN + "Filtering points..." + bcolors.ENDC):
        if (time_diff[1] not in delay_per_district):
            delay_per_district[time_diff[1]] = dict()
        delay_per_district[time_diff[1]][time_diff[0]] = delay_per_district[time_diff[1]].get(time_diff[0], 0) + 1
        delay_total[time_diff[0]] = delay_total.get(time_diff[0], 0) + 1
        district_counter[time_diff[1]] = district_counter.get(time_diff[1], 0) + 1

    # Create the plot
    fig, ax = plt.subplots(4, 5, gridspec_kw={'hspace': 0.5})
    fig.suptitle('Niezgodności w rozkładzie jazdy autobusów w Warszawie i jej dzielnicach.', fontsize=25)
    fig.supxlabel('Czas opóźnienia [minuty]', fontsize=12)
    fig.supylabel('Procent autobusów', fontsize=12)

    # Prepare the plot - plot districts in correct subplots
    positions = [(0, i) for i in range(5)] + [(i, j) for i in range(1, 3) for j in (0, 1, 3, 4)] + [(3, i) for i in range(5)]
    idx = 0

    # Plot the data
    print(bcolors.OKBLUE + "Plotting..." + bcolors.ENDC)
    for district in list(sorted(delay_per_district.keys())):
        prepare_plot(ax, positions[idx], district, idx + 1, delay_per_district[district], colors[idx])
        idx += 1

    # plot summary data
    prepare_plot(ax, (1, 2), "WARSZAWA", None, delay_total, colors[idx])
    prepare_plot(ax, (2, 2), "Procent autobusów wg dzielnic", None, district_counter, colors, False)

    plt.get_current_fig_manager().full_screen_toggle()
    plt.savefig(os.path.join(path, f"./PLOTS/schedule_plot_{dataSet}.png"))

    if (show):
        plt.show()
