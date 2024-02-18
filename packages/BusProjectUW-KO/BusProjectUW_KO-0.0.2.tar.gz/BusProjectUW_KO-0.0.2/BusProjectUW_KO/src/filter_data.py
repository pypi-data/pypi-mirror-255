import os
import json
from datetime import datetime
from typing import Dict, List, Type, Union
from alive_progress import alive_bar, alive_it
from shapely.geometry import Point
from shapely.prepared import prep
from .tools import calculate_distance, bcolors, read_geojson


MS_TO_KMH = 3.6
MIN_TIME = 10
MAX_TIME = 20

warsaw_gdf = read_geojson('warszawa-dzielnice.geojson')
warsaw_simple_gdf = read_geojson('warszawa-simple.geojson')
warsaw_prepared_polygon = [prep(geom) for geom in warsaw_gdf[1:]["geometry"]]
warsaw_simple_prepared_polygon = [prep(geom) for geom in warsaw_simple_gdf[1:]["geometry"]]


def point_in_simple_Warsaw(point: Type[Point]) -> Union[str, None]:
    '''Improved point in polygon algorithm for Warsaw'''

    # Check if the point is in the polygon
    for index, prepared_polygon in enumerate(warsaw_simple_prepared_polygon):
        if prepared_polygon.contains(point):
            return warsaw_simple_gdf.loc[index + 1, "name"]

    return None


def point_in_Warsaw(point: Type[Point]) -> Union[str, None]:
    '''Point in polygon algorithm for Warsaw'''

    # Check if the point is in the simple polygon
    simple = point_in_simple_Warsaw(point)
    if (simple is not None):
        return simple

    # Check if the point is in the polygon
    for index, prepared_polygon in enumerate(warsaw_prepared_polygon):
        if prepared_polygon.contains(point):
            return warsaw_simple_gdf.loc[index + 1, "name"]

    return None


def get_important_data(raw_data: List[Dict]) -> Dict:
    '''Returns a dictionary with important bus data from all API data in a friendly format.'''

    data = dict()
    for bus_info in raw_data['result']:
        data[bus_info['VehicleNumber']] = {
            "Position": (bus_info['Lon'], bus_info['Lat']),
            "Time": bus_info['Time'],
            "Line": bus_info['Lines'],
            "Brigade": bus_info['Brigade'],
        }

    return data


def filter_and_save_data(path: str, dataSet: int = 1) -> None:
    '''Filters the data and saves it to a file.'''

    # Open the file to save the segments
    data_path = os.path.join(path, "DATA_SETS", f"DATA_SET_{dataSet}")
    segments_file = open(os.path.join(path, "FILTERED_DATA", "FILTERED_SEGMENTS", f"filtered_segments_{dataSet}.csv"), "w")
    segments_file.write("start_lon,start_lat,start_district,end_lon,end_lat,end_district,velocity,line\n")

    # Count the number of files
    file_count = sum(1 for item in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, item)))

    # Estimate the number of vehicles
    vehicles = 0
    for i in alive_it(range(0, file_count - 1), title=bcolors.OKCYAN + "Estimating data size..." + bcolors.ENDC, spinner='dots'):
        curr_file_path = os.path.join(data_path, f"{i}.json")
        curr_file = open(curr_file_path, "r")
        vehicles += len(json.load(curr_file)["result"])
        curr_file.close()

    # Open the first file and prepare results
    prev_file_path = os.path.join(data_path, "0.json")
    prev_file = open(prev_file_path, "r")
    prev_data = get_important_data(json.load(prev_file))
    valid_positions = []

    with alive_bar(vehicles, spinner='dots') as bar:
        bar.title(bcolors.OKCYAN + "Generating segments and positions..." + bcolors.ENDC)

        # Iterate through all files
        for i in range(1, file_count):
            curr_file_path = os.path.join(data_path, f"{i}.json")
            curr_file = open(curr_file_path, "r")
            curr_data = get_important_data(json.load(curr_file))

            # Iterate through all buses
            for VehicleNumber in prev_data:
                prev = prev_data.get(VehicleNumber)
                curr = curr_data.get(VehicleNumber)

                # If the bus is not in the current data set, skip it
                if (curr is None):
                    bar(skipped=True)
                    continue

                # Calculate the time difference (getting many errors here)
                try:
                    prev_time = datetime.strptime(prev["Time"], '%Y-%m-%d %H:%M:%S')
                    curr_time = datetime.strptime(curr["Time"], '%Y-%m-%d %H:%M:%S')
                    time_diff = curr_time - prev_time
                except Exception:
                    print(bcolors.WARNING + "[ERROR] Could not parse time." + bcolors.ENDC)
                    bar(skipped=True)
                    continue

                # If the bus has not moved, skip it or if it has moved more than 20 seconds ago
                if (not (MIN_TIME <= time_diff.seconds <= MAX_TIME)):
                    bar(skipped=True)
                    continue

                # Calculate the velocity
                distance = calculate_distance(prev["Position"], curr["Position"])
                velocity = (distance / time_diff.seconds) * MS_TO_KMH

                # Calculate the districts
                if ("District" not in prev):
                    prev["District"] = point_in_Warsaw(Point(prev["Position"]))
                curr["District"] = point_in_Warsaw(Point(curr["Position"]))

                # If the bus is not in Warsaw, skip it
                if (prev["District"] is None or curr["District"] is None):
                    bar(skipped=True)
                    continue

                # Save the segment and points
                segments_file.write(f"{prev['Position'][0]},{prev['Position'][1]},{prev["District"]},{curr['Position'][0]},{curr['Position'][1]},{curr["District"]},{velocity},{prev['Line']}\n")
                valid_positions.append(curr)
                if (i == 1):
                    valid_positions.append(prev)

                bar(skipped=False)

            prev_file.close()
            prev_file = curr_file
            prev_data = curr_data

    prev_file.close()
    segments_file.close()

    # Save the valid positions
    print(bcolors.OKBLUE + "Saving data..." + bcolors.ENDC)
    with open(os.path.join(path, "FILTERED_DATA", "VALID_POSITIONS", f"valid_positions_{dataSet}.json"), "w") as file:
        json.dump(valid_positions, file)
