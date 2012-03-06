import requests
from xml.dom import minidom
from datetime import datetime
from datetime import timedelta

class Weather:
    def __init__(self, weather_url):
        self.url = weather_url
        self.timeout = timedelta(0, 300) #Expire cache every 5 minutes
        self.timestamp = None #No timestamp means that we haven't fetched anything yet
        self.weather_data = None #This is the xml.dom.minidom where we cache our weather data
        
    def get_weather_data(self):
        if self.timestamp == None or datetime.now() > self.timestamp + self.timeout:
            self.weather_doc = self.fetch_weather_data()
            self.timestamp = datetime.now()
        degrees_f = self.parse_farenheit()
        degrees_c = self.parse_celcius()
        current_conditions = self.parse_conditions()
        return degrees_f, degrees_c, current_conditions

    def fetch_weather_data(self):
        r = requests.get(self.url)
        if r.status_code == 200:
            self.weather_data = minidom.parseString(r.text)
            if len(self.weather_data.getElementsByTagName("weather")[0].getElementsByTagName("current_conditions")) < 1:
                #No current conditions returned; this is not the data we're looking for
                raise Exception("Invalid weather data")
        else:
            raise Exception("Could not retrieve weather data")

    def parse_farenheit(self):
        return self._get_temperature_node("temp_f").getAttribute("data")

    def parse_celcius(self):
        return self._get_temperature_node("temp_c").getAttribute("data")

    def parse_conditions(self):
        return self.weather_data.getElementsByTagName("weather")[0].getElementsByTagName("current_conditions")[0].getElementsByTagName("condition")[0].getAttribute("data")
    

    def _get_temperature_node(self, temperature_tag_name):
        return self.weather_data.getElementsByTagName("weather")[0].getElementsByTagName("current_conditions")[0].getElementsByTagName(temperature_tag_name)[0]

    
