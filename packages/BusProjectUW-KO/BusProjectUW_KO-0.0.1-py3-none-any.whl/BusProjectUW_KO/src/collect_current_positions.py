import os
import time
import json
from alive_progress import alive_it
from .tools import bcolors, force_response


def collect_current_positions(path: str, api_key: str, dataSize: int = 100) -> int:
    '''Collects current positions of buses from UM API.'''

    print(bcolors.HEADER + "Collecting current positions..." + bcolors.ENDC)
    url = 'https://api.um.warszawa.pl/api/action/busestrams_get/'  # URL for UM API

    # Parameters for UM API
    params = {
        'resource_id': 'f2e5503e-927d-4ad3-9500-4ab9e55deb59',
        'type':	'1',
        'apikey': api_key
    }

    # Directory path
    directory = os.path.join(path, 'DATA_SETS')

    if not os.path.exists(directory):
        os.mkdir(directory)

    # Get the number of directories
    num_directories = sum(1 for item in os.listdir(directory) if os.path.isdir(os.path.join(directory, item)))

    # Create a new folder
    new_folder_name = f'DATA_SET_{num_directories + 1}'
    new_folder_path = os.path.join(directory, new_folder_name)
    os.mkdir(new_folder_path)

    # Collect data
    for i in alive_it(range(dataSize), title=bcolors.OKCYAN + "Downloading data from API..." + bcolors.ENDC, spinner='dots'):
        if (i != 0):
            time.sleep(10)

        # Get data from UM API
        response = force_response(url, params, i)

        # Save to file
        path = os.path.join(new_folder_path, f'{i}.json')
        with open(path, 'w') as file:
            json.dump(response, file)

    return num_directories + 1
