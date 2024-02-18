from .collect_busStops import collect_busStops
from .collect_current_positions import collect_current_positions
from .collect_public_transport_routes import collect_public_transport_routes
from .collect_dictionary import collect_dictionary
from .collect_schedule import collect_schedule


def collect_all(path: str, api_key: str, dataSize: int = 100) -> int:
    '''Collects all necessary data from UM API and saves it to files'''

    collect_busStops(path, api_key)
    collect_dictionary(path, api_key)
    collect_public_transport_routes(path, api_key)
    dataSet = collect_current_positions(path, api_key, dataSize=dataSize)
    collect_schedule(path, api_key)

    return dataSet
