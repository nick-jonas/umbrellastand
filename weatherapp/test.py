import forecastio
import json
from pprint import pprint

with open('config.json') as data_file:
	data = json.load(data_file)
	api_key = data['api_key']
	lat = float(data['lat'])
	lng = float(data['lng'])