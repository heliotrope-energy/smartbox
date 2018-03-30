#accessing weather station via AmbientWeather API
#using REST api instead of real-time API
#TODO: switch to websocket API?
#docs here https://ambientweather.docs.apiary.io/#reference/ambient-realtime-api/query-device-data?console=1
import requests
import json
import smartbox.components.weather_api_config as weather_api_config

#TODO: move to git-secret instead of separate API config
class SmartBoxWeatherStation:
    def __init__(self):

        self.app_key=weather_api_config.application_key
        self.device_key=weather_api_config.device_key
        self.mac=weather_api_config.MAC

    def query_devices(self):
        '''
        Get device info.
        '''
        url="https://api.ambientweather.net/v1/devices?applicationKey={}&apiKey={}".format(self.app_key, self.device_key)

        response = requests.get(url)

        if(response.ok):
              data = json.loads(response.content)
              return data
        else:
            return []
            response.raise_for_status()


    def query_data(self):
        '''
        Get device data.
        '''
        url="https://api.ambientweather.net/v1/devices/{}?apiKey={}&applicationKey={}".format(self.mac, self.device_key, self.app_key)

        response = requests.get(url)

        if(response.ok):
              data = json.loads(response.content)
              return data
        else:
            return []
            response.raise_for_status()

    def get_recent_weather(self):
        data = self.query_data()
        if len(data) > 0:
            return data[0]
        else:
            return {}



if __name__=="__main__":
    #testing
    sbw = SmartBoxWeatherStation()
    data = sbw.get_recent_weather()
    for key, value in data.items():
        print("{}\t{}".format(key, value))