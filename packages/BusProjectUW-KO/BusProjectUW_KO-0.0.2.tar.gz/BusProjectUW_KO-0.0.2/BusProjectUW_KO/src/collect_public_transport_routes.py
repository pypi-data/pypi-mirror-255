import json
import os
from .tools import force_response, bcolors


def collect_public_transport_routes(path: str, api_key: str) -> None:
    '''Collects public transport routes data from UM API and saves it to a file'''

    print(bcolors.HEADER + "Collecting public transport routes..." + bcolors.ENDC)
    url = 'https://api.um.warszawa.pl/api/action/public_transport_routes/'  # URL for UM API

    # Parameters for UM API
    params = {
        'apikey': api_key
    }

    # Get data from UM API
    response = force_response(url, params, None)

    # Save to file
    with open(os.path.join(path, 'SCHEDULE', 'public_transport_routes.json'), 'w') as file:
        json.dump(response, file)
