import json
import os
from datetime import datetime
from alive_progress import alive_it
from .tools import calculate_distance, bcolors

DELTA_DISTANCE = 50


def filter_positions(path: str, dataSet: int = 1) -> None:
    '''Filter positions of buses which are around bus stops.'''

    # Load bus stops
    file_busStops = os.path.join(path, "SCHEDULE/busStops.json")
    with open(file_busStops, 'r') as file:
        busStops = json.load(file)

    # Load valid positions
    file_path = os.path.join(path, f"FILTERED_DATA/VALID_POSITIONS/valid_positions_{dataSet}.json")
    with open(file_path, 'r') as file:
        valid_positions = json.load(file)

    filtered_positions = []

    # Filter positions
    for bus in alive_it(valid_positions, title=bcolors.OKCYAN + "Filering positions..." + bcolors.ENDC, spinner='dots'):
        # Load bus possible positions (some lines do not exist in the schedule, so we need to handle this case)
        try:
            file_bus_positions = os.path.join(path, f"SCHEDULE/LINES/line_{bus["Line"]}.json")
            with open(file_bus_positions, 'r') as file:
                bus_positions = json.load(file)
        except Exception:
            continue

        # Some brigades do not exist in the schedule, so we need to handle this case
        if (bus["Brigade"] not in bus_positions):
            continue

        # If a bus is over 1h late, it is not considered, as it is probably wrong
        bestTime = 3600

        bus_time = datetime.strptime(bus["Time"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")

        # Find best busStop for bus
        for busStop in bus_positions[bus["Brigade"]]:
            # Bus stop does not exist :)
            if busStop not in busStops:
                continue

            busStopPosition = (float(busStops[busStop]["dlug_geo"]), float(busStops[busStop]["szer_geo"]))

            distance = calculate_distance(bus["Position"], busStopPosition)

            # The bus is not close enough to the bus stop
            if (distance > DELTA_DISTANCE):
                continue

            # Find best time for bus
            for curr_time in bus_positions[bus["Brigade"]][busStop]:
                # Time parsing correction :)
                if (int(curr_time[:2]) >= 24):
                    curr_time = str(int(curr_time[:2]) - 24) + curr_time[2:]
                time_diff = abs((datetime.strptime(curr_time, "%H:%M:%S") - datetime.strptime(bus_time, "%H:%M:%S")).seconds)

                bestTime = min(bestTime, time_diff)

            # If the bus is over 1h late, it is not considered, as it is probably wrong
            if (bestTime >= 3600):
                continue

            # Save the best time for the bus
            bus["Time"] = bestTime
            filtered_positions.append(bus)

    # Save the filtered positions
    print(bcolors.OKBLUE + "Saving data..." + bcolors.ENDC)
    with open(os.path.join(path, f"FILTERED_DATA/FILTERED_POSITIONS/filtered_positions_{dataSet}.json"), "w") as file:
        json.dump(filtered_positions, file)
