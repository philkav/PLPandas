"""
Philip Kavanagh
August 2022

SSBtaXNzIHlvdSBEYWQK

API - The API I use is from football-data.org
In order to use the API, you need an API KEY in your environment variables
eg:
$ export FOOTBALL_DATA_API_KEY=1337C0FFEE

Sample Usage:
>>> import API
>>> import json
>>> api = API.API()
>>> teams = api.map[6]  # ("competitions", "teams")
>>> endpoint = api.get_endpoint(teams[API.RESOURCE], teams[API.ACTION])
>>> pl = endpoint.format(code='PL')  # Get the Premier League endpoint URL
>>> r = api.request(pl)  # Request data from the PL endpoint
>>> js = json.loads(r.text)  # Load the data into json format (dict)
>>> js.keys()
  dict_keys(['count', 'filters', 'competition', 'season', 'teams'])
>>> mufc = js['teams'][7]  # Select team in element 7 (Man Utd)
>>> mufc['name']
'Manchester United FC'
>>> mufc['coach']['name']
'Erik ten Hag'
>>> [ x['name'] for x in mufc['squad']]
['David De Gea', 'Tom Heaton', 'Harry Maguire', 'Raphaël Varane', 'Victor Nilsson-Lindelöf', 'Axel Tuanzebe',
 'Tyrell Malacia', 'Phil Jones', 'Luke Shaw', 'Eric Bailly', 'Aaron Wan-Bissaka', 'Diogo Dalot', 'Lisandro Martínez',
 'Brandon Williams', 'Teden Mengi', 'Jadon Sancho', 'Fred', 'Bruno Fernandes', 'Christian Eriksen', 'Donny van de Beek',
 'Scott McTominay', 'Tahith Chong', 'James Garner', 'Anthony Elanga', 'Cristiano Ronaldo', 'Marcus Rashford',
 'Anthony Martial', 'Mason Greenwood', 'Facundo Pellistri', 'Amad Diallo', 'Shola Shoretire', 'Alejandro Garnacho']
"""

import json
import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RESOURCE = 0
ACTION = 1

class API:
    """
    API Reference: https://docs.football-data.org/general/v4/index.html

    Resources:
    - Area
    - Competition
    - Match
    - Team
    - Person
    """
    def __init__(self):
        self.API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY') or None
        self.API_VERSION = "v4"
        self.API_URL = f"http://api.football-data.org/{self.API_VERSION}"

        self.request_headers = {
            'X-Response-Control': 'full',
            'X-Auth-Token': self.API_KEY
        }

        # Map of resource/action combinations
        self.map = [
            ("areas", "list"),
            ("areas", "get"),
            ("competitions", "list"),
            ("competitions", "get"),
            ("competitions", "standings"),
            ("competitions", "matches"),
            ("competitions", "teams"),
            ("competitions", "scorers"),
        ]

        self.endpoints = {
            # Areas
            "areas": {
                "list": {
                    "url": "/areas",
                    "filters": None
                },
                "get": {
                    "url": "/areas/{id}",
                    "filters": None
                }
            },
            # Competitions
            "competitions": {
                "list": {
                    "url": "/competitions",
                    "filters": ["areas={areas}"]
                },
                "get": {
                    "url": "/competitions/{code}",
                    "filters": None
                },
                "standings": {
                    "url": "/competitions/{code}/standings",
                    "filters": ["matchday={matchday}", "season={year}", "date={date}"]
                },
                "matches": {
                    "url": "/competitions/{code}/matches",
                    "filters": ["dateFrom={dateFrom}", "dateTo={dateTo}", "stage={stage}", "status={status}", "matchday={matchday}", "group={group}", "season={year}"]
                },
                "teams": {
                    "url": "/competitions/{code}/teams",
                    "filters": ["season={year}"]
                },
                "scorers": {
                    "url": "/competitions/{code}/scorers",
                    "filters": ["limit={limit}", "season={year}"]
                },
            },
        }

    def get_endpoint(self, resource, action):
        """ Example Usage:
        > scorers = API.API().get_endpoint('competitions', 'scorers')
        > scorers
          'http://api.football-data.org/v4/competitions/{code}/scorers'
        > scorers.format(code='PL')
          'http://api.football-data.org/v4/competitions/PL/scorers' """
        k = self.endpoints[resource][action]['url']
        return self.API_URL+k

    def get_filters(self, resource, action):
        """ Example Usage:
        > scorers = API.API().get_filters('competitions', 'scorers')
        > scorers
          ['limit={limit}', 'season={year}'] """
        return self.endpoints[resource][action]['filters']

    def request(self, url, filters=None):
        r = requests.get(url, headers=self.request_headers, params=filters)
        return r