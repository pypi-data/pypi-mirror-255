# FPL API

This is a simple python API wrapper for the Fantasy Premier League game. It scrapes the official FPL site to retrieve data and present it in JSON format.

## Documentation

The API design is inspired by the [Fantasy Premier League API Endpoints: A Detailed Guide](https://medium.com/@frenzelts/fantasy-premier-league-api-endpoints-a-detailed-guide-acbd5598eb19) by [Frenzel Timothy](https://medium.com/@frenzelts?source=post_page-----acbd5598eb19--------------------------------).
The guide shows all endpoint that are implemented in this API wrapper.

## Installation

Run the following command to download the most recent release:

```bash
pip install git+https://github.com/C-Roensholt/fpl-api.git 
```

To install a specific version:

```bash
pip install git+https://github.com/C-Roensholt/fpl-api.git@v0.0.1
```

## Usage

A basic example of how to use the API could be:

```python

from fplapi import fplAPI

# Initialize API connection
client = fplAPI()

# Extract metadata
fpl_data = client.get_fpl_data()
fixtures = client.get_fixtures()

# Get first 10 players data
player_detailed_data_list = []
for player in fpl_data["elements"][:10]:
    player_detailed_data = client.get_player_detailed_data(element_id=player["id"])
    player_detailed_data_list.append(player_detailed_data)

```
