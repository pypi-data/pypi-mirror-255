import requests
import time
import sys
import os
import numpy as np
import pkg_resources
import json
import geopandas as gpd
from typing import Tuple, NewType, Dict, List, Union


Coordinates = NewType('Coordinate', Tuple[float, float])
EARTH_RADIUS = 6371000.0


def calculate_distance(point_A: Coordinates, point_B: Coordinates) -> float:
    '''Calculates distance between two points on Earth using Haversine formula.'''

    lon_A, lat_A = point_A
    lon_B, lat_B = point_B

    lat_A, lon_A = np.radians(lat_A), np.radians(lon_A)
    lat_B, lon_B = np.radians(lat_B), np.radians(lon_B)

    lon_diff = lon_B - lon_A
    lat_diff = lat_B - lat_A

    # Magic formula calculating distance between two points on Earth
    a = np.sin(lat_diff / 2)**2 + np.cos(lat_A) * np.cos(lat_B) * np.sin(lon_diff / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return EARTH_RADIUS * c


def force_response(url: str, params: Dict, i: Union[int, None], timeout: int = 100, allowFail: bool = False) -> Dict:
    '''Forces response from UM API.
    If the response is empty, it retries until it gets a response.
    If it fails, it returns an empty response.
    timeout - number of retries
    allowFail - if True, it does not print error messages'''

    error_count = 0
    error_message = ""
    response = {"result": []}
    SHIFT = bcolors.MOVE_RIGHT * (5 + len(str(i))) if i is not None else ""

    # Get data from UM API
    while (True):
        # Get response
        try:
            response = requests.get(url, params=params).json()
        except Exception:
            error_count += 1

        # Check if the response is empty or if it is a bad response
        if len(response['result']) == 0 or (isinstance(response['result'], str) and response['result'][0] == 'B'):
            error_count += 1

            if (error_message == "" and not allowFail):
                print(bcolors.WARNING + "[ERROR]" + bcolors.ENDC)

            error_message = f"[ERROR] Could not get data from UM API. ({error_count})"
            if (not allowFail):
                print(bcolors.PREV_LINE + SHIFT + bcolors.WARNING + error_message + bcolors.ENDC)
            time.sleep(0.1)
        else:  # Success
            break

        # Timeout
        if (error_count >= timeout):
            if (not allowFail):
                print(bcolors.PREV_LINE + SHIFT + bcolors.FAIL + "[FAIL] Could not get data from UM API." + " " * 20 + bcolors.ENDC)
            return response

    # Change the error message to success message
    if (error_message != "" and not allowFail):
        print(bcolors.PREV_LINE + SHIFT + bcolors.WARNING + error_message + bcolors.OKGREEN + " [OK]" + bcolors.ENDC)

    return response


def check_params(path: str, DataSetId: int) -> int:
    '''Checks if DataSetId is valid'''

    # Check if the DATA_SET_{DataSetId} file exists
    data_set_file = os.path.join(path, "DATA_SETS", f"DATA_SET_{DataSetId}")
    if not os.path.exists(data_set_file):
        print(bcolors.FAIL + f"Error: {data_set_file} does not exist." + bcolors.ENDC)
        sys.exit(1)


def read_geojson(path: str) -> List[Coordinates]:
    '''Reads GeoJSON file and returns a list of coordinates'''

    with pkg_resources.resource_stream(__name__, path) as f:
        data = gpd.read_file(f)

    return data


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    PREV_LINE = "\033[F"
    MOVE_RIGHT = "\033[C"
