import requests
from xml.dom import minidom
from datetime import datetime
from datetime import timedelta
from weather_secret import API_KEY #This is API key for the weather underground API
from pprint import pprint #DEBUG

class Weather:
    def __init__(self):
        self.query_cache = {}
        self.ttl = timedelta(minutes=5)
    
    def get_weather(self, query):
        if not (query in self.query_cache) or (self.query_cache[query].timestamp < (datetime.now() - self.ttl)):
            self.fetch_weather(query)
        if isinstance(self.query_cache[query], Observation): 
            return "Conditions at %s: %s, %s" % (self.query_cache[query].location, 
                                                 self.query_cache[query].conditions, 
                                                 self.query_cache[query].temperature)
        else:
            return self.query_cache[query]

    def fetch_weather(self, query):
        print "Fetching weather for:" #DEBUG
        pprint(query) #DEBUG
        autocomplete_results = requests.get("http://autocomplete.wunderground.com/aq", params={"query": query,  "h": 0}).json()
        if len(autocomplete_results['RESULTS']) > 0:
            new_observation = Observation(str(autocomplete_results['RESULTS'][0]['name']), autocomplete_results['RESULTS'][0]['l'])
            weather_data = requests.get("http://api.wunderground.com/api/%s/conditions%s.json" % (API_KEY, new_observation.link)).json()
            new_observation.temperature = weather_data['current_observation']['temperature_string']
            new_observation.conditions = weather_data['current_observation']['icon']
            self.query_cache[query] = new_observation
        else:
            self.query_cache[query] = "No results found for %s" % query

class Observation:
    def __init__(self, name, wunderground_link):
        self.location = name,
        self.link = wunderground_link
        self.temperature = ""
        self.conditions = ""
        self.timestamp = datetime.now()


    
