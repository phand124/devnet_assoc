# Simple example of the requests module against the Star Wars API


import requests
import json

base_url = "https://swapi.info/api/"
endpoint = "people/"

response = requests.get(base_url + endpoint)
data = response.json()

print(data[0]['name'])

