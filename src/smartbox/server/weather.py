import logging

from smartbox_msgs import weather_pb2
from smartbox_msgs import weather_pb2_grpc

from smartbox.components.sb_weather_station import SmartBoxWeatherStation

class SmartBoxWeatherController(weather_pb2_grpc.WeatherControllerServicer):
	def __init__(self):
		self.weather = SmartBoxWeatherStation()
		self.logger = logging.getLogger(__name__)

	def get_weather(self, request, context):
		self.logger.info("Weather request received")
		response = weather_pb2.WeatherResponse()
		
		try:
			weather = self.weather.get_recent_weather()
		except Exception as e:
			self.logger.error("Getting weather failed with an exception, must be a tornado")
			self.logger.error(e, exc_info=True)
			return response

		if len(weather) == 0:
			self.logger.error("Getting weather failed, let's just assume it's sunny")
			return response

		response.date = weather['date']
		response.date_utc = weather['dateutc']

		response.weather.barometer_relative = weather['baromrelin']
		response.weather.barometer_absolute = weather['baromabsin']

		response.temperature.outdoor = weather['tempf']
		response.temperature.indoor = weather['tempinf']
		response.temperature.feels_like = weather['feelsLike']
		response.temperature.dew_point = weather['dewPoint']

		response.rain.hourly = weather['hourlyrainin']
		response.rain.daily = weather['dailyrainin']
		response.rain.weekly = weather['weeklyrainin']
		response.rain.monthly = weather['monthlyrainin']
		response.rain.total = weather['totalrainin']
		response.rain.last = weather['lastRain']

		response.wind.direction = weather['winddir']
		response.wind.speed = weather['windspeedmph']
		response.wind.gust = weather['windgustmph']
		response.wind.max_daily_gust = weather['maxdailygust']

		response.solar.uv = weather['uv']
		response.solar.radiation = weather['solarradiation']

		return response