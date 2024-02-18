import os
import json
from typing import List, Dict
from .tools import bcolors, force_response


def get_info(info: List[Dict]) -> Dict:
    '''Returns a dictionary with bus data in a friendly format.'''

    good_info = dict()

    for dic in info["values"]:
        good_info[dic["key"]] = dic["value"]

    return good_info


def collect_busStops(path: str, api_key: str) -> None:
    '''Collects bus stops data from UM API and saves it to a file'''

    print(bcolors.HEADER + "Collecting bus Stops..." + bcolors.ENDC)
    url = 'https://api.um.warszawa.pl/api/action/dbstore_get'  # URL for UM API

    # Parameters for UM API
    params = {
        'apikey': api_key,
        'id': 'ab75c33d-3a26-4342-b36a-6e5fef0a3ac3',
        # 'id' : '1c08a38c-ae09-46d2-8926-4f9d25cb0630'		# busStops_curr
    }

    # Get data from UM API
    response = force_response(url, params, None)

    busStops = dict()

    # Save to dictionary
    for info in response['result']:
        info = get_info(info)
        key = "|".join((info["zespol"], info["slupek"]))
        busStops[key] = info

    # Save to file
    with open(os.path.join(path, 'SCHEDULE', 'busStops.json'), 'w') as file:
        json.dump(busStops, file)
