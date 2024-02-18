import json
import os
from alive_progress import alive_it
from .tools import bcolors, force_response


def get_info(info):
    '''Returns a dictionary with data in a friendly format.'''

    good_info = dict()

    for dic in info["values"]:
        good_info[dic["key"]] = dic["value"]

    return good_info


def get_schedule(path: str, api_key: str, line: int) -> None:
    '''Collects bus schedule of a set line data from UM API and saves it to a file.'''

    api_key = "c7fc874d-fcff-4480-8671-f452e945b35a"  # API key for UM API
    url = 'https://api.um.warszawa.pl/api/action/dbtimetable_get'  # URL for UM API
    public_transport_routes = os.path.join(path, 'SCHEDULE/public_transport_routes.json')
    main_directory = os.path.join(path, 'SCHEDULE/LINES')
    os.makedirs(main_directory, exist_ok=True)

    my_line_data = dict()

    with open(public_transport_routes, 'r') as file:
        # Load data from file
        data = json.load(file)
        info = []
        for route_name in data['result'][line]:
            for idx in data['result'][line][route_name].keys():
                info.append(data['result'][line][route_name][idx])

        for i in alive_it(range(len(info)), title=bcolors.OKCYAN + f"Working on bus schedule for line {line}" + bcolors.ENDC, spinner='dots'):
            params = {
                'apikey': api_key,
                'id': 'e923fa0e-d96c-43f9-ae6e-60518c9f3238',
                'busstopId': info[i]['nr_zespolu'],
                'busstopNr': info[i]['nr_przystanku'],
                'line': line
            }

            # Get data from UM API
            busStop = params['busstopId'] + "|" + params['busstopNr']
            response = force_response(url, params, i, timeout=3, allowFail=True)

            # Save to dictionary
            for data in response['result']:
                data = get_info(data)
                brigade = data['brygada']
                if brigade not in my_line_data:
                    my_line_data[brigade] = dict()

                if busStop not in my_line_data[brigade]:
                    my_line_data[brigade][busStop] = []

                my_line_data[brigade][busStop].append(data["czas"])

    # Save to file
    file_name = f"line_{line}.json"
    with open(os.path.join(main_directory, file_name), 'w') as file:
        json.dump(my_line_data, file)


def collect_schedule(path: str, api_key: str) -> None:
    '''Collects bus schedule for all lines data from UM API and saves it to a file.'''

    print(bcolors.HEADER + "Collecting schedule..." + bcolors.ENDC)
    print(bcolors.HEADER + "This process might take around 5-6 hours to fully complete." + bcolors.ENDC)
    with open(os.path.join(path, 'SCHEDULE/public_transport_routes.json'), 'r') as file:
        data = json.load(file)
        lines = list(data['result'].keys())

        # Collect data for each line
        for i in range(len(lines)):
            get_schedule(path, api_key, lines[i])
            print(bcolors.OKGREEN + "[SUCCESS] Collected ", str((i + 1)) + " out of " + str(len(lines)) + " line schedules." + bcolors.ENDC)
