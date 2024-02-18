import json
import os
from .tools import force_response, bcolors


def collect_dictionary(path: str, api_key: str) -> None:
    '''Collects dictionary data from UM API and saves it to a file'''

    print(bcolors.HEADER + "Collecting dictionary..." + bcolors.ENDC)
    url = 'https://api.um.warszawa.pl/api/action/public_transport_dictionary/'  # URL for UM API

    # Parameters for UM API
    params = {
        'apikey': api_key
    }

    # Get data from UM API
    response = force_response(url, params, None)

    # Save to file
    with open(os.path.join(path, 'SCHEDULE', 'dictionary.json'), 'w') as file:
        json.dump(response, file)
