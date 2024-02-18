# BIG PROJECT - my Python project for UW

Project about buses in Warsaw.

# Project Goals

This project aims to achieve the following goals:

1. Show routes of buses in Warsaw that exceed the speed of 50 km/h.
2. Evaluate the delays of buses according to their schedule.

By accomplishing these goals, the project aims to provide valuable insights into the efficiency and performance of the bus system in Warsaw. 

All results are district-focused.

# Sample code

```python
from BusProjectUW_KO import collect_all
from BusProjectUW_KO import analyse_all

api_key = "your_api_key"  # API key for UM API
path = os.getcwd()

dataSet = collect_all(path, api_key)
analyse_all(path, dataSet)
```

```python
from BusProjectUW_KO import collect_current_positions
from BusProjectUW_KO import analyse_all

api_key = "your_api_key"  # API key for UM API
path = os.getcwd()

dataSet = collect_current_positions(path, api_key)
analyse_all(path, dataSet)
```

# Documentation

## collect.py
- `collect_all(path: str, api_key: str, dataSize: int = 100 -> int` collects all data mentioned below -> all needed data for the project and returns the new dataSet id

### collect_busStops.py
- `collect_busStops(path: str, api_key : str) -> None` gets bus stop positions 

### collect_dictionary.py
- `collect_dictionary(path: str, api_key: str) -> None:` gets a dictionary with definitions from the api

### collect_public_transport_routes.py
- `collect_public_transport_routes(path: str, api_key: str) -> None:` gets public transport routes - information about busstops for each line

### collect_schedule.py
- `collect_schedule(path: str, api_key: str) -> None:` gets a full schedule for all lines and all brigades. This function takes AGES, so make sure to make yourself a cup of tea ;)

### collect_current_positions.py
- `collect_current_positions(path: str, api_key: str, dataSize: int = 100) -> int:` creates a new dataSet by collecting data. Will take at least `dataSize * 10 seconds`


## analyse.py
- `analyse_all(path: str, dataSet: int = 1) -> None:` Analyses the data, saves segments and points that are in Warsaw. Analyses buses in terms of both excesive speed and possible delay 

- `analyse_speed(path: str, dataSet: int = 1) -> None:` Analyses the data, saves segments and points that are in Warsaw. Analyses buses ONLY in terms of excesive speed

- `analyse_schedule(path: str, dataSet: int = 1) -> None` Analyses the data, saves segments and points that are in Warsaw. Analyses buses ONLY in temrs of possible delays

### plot_data_set_schedule.py

- `plot_data_set_schedule(path: str, dataSet: int = 1, show: bool = False) -> None:` assumes that the dataSet has already been analysed and only prepares a plot regarding schedule. `show` set to `True` will show the plot.

- `plot_data_set_speed(path: str, dataSet: int = 1, show: bool = False) -> None:` assumes that the dataSet has already been analysed and only prepares a plot regarding excessive speed. `show` set to `True` will show the plot.

# All other methods are not recommended for user to use :)