#accessing weather station via AmbientWeather API
#using REST api instead of real-time API
#TODO: switch to websocket API?
#docs here https://ambientweather.docs.apiary.io/#reference/ambient-realtime-api/query-device-data?console=1
import requests
import json
import api_config

#TODO: move to git-secret instead of separate API config
class SmartBoxWeatherStation:
    def __init__(self):

        self.app_key=api_config.application_key
        self.device_key=api_config.device_key
        self.mac=api_config.MAC

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
            response.raise_for_status()


if __name__=="__main__":
    #testing
    sbw = SmartBoxWeatherStation()
    data = sbw.query_data()
    print(data)
