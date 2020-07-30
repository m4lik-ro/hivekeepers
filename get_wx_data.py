import json 
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import database
from datetime import datetime as dt
import logging
from logging.config import fileConfig
import sys

fileConfig('log.ini', defaults={'logfilename': 'bee.log'})
logger = logging.getLogger('weather')

_wx_location = 'Frankston East, AU'
_wx_appid = '7a0e2ae12cf4cc52a6b40f9ae4d2456a'

def download_json_from_wx_api():

    _url = 'http://api.openweathermap.org/data/2.5/weather?' + urlencode ({        
        'q' : _wx_location,
        'APPID': _wx_appid
    })
    logger.debug (_url)
    
    data = urlencode(dict(Body='This is a test')).encode('ascii')
    
    try:
        response = urlopen(Request(_url, data))
        return True, response.read().decode()

    except:
        return False, None
        
def kelvinToCelcius(kelvin):
    return kelvin - 273.15
    
def msToKph(ms):
    return ms * 3.6

response, data = download_json_from_wx_api()
if not response:
    logger.error ('Cound not download weather data. Quiting')
    sys.exit(2)
    
try:
    parsed = json.loads(data)
#print(json.dumps(parsed, indent=4, sort_keys=True))
except:
    logger.error ('Count not parse JSON file. Quiting')
    sys.exit(2)


try:
    calc_time = dt.fromtimestamp(parsed['dt'])
except:
    calc_time = '1981-02-10 00:00:00'
    logger.error ('Cound not parse calc_time')

try:
    wind_deg = parsed['wind']['deg']
except:
    wind_deg = -1
    logger.error ('Cound not parse wind_deg')

try:
    wind_gust = '{:.2f}'.format(msToKph(parsed['wind']['gust']))
except:
    wind_gust = -1
    logger.error ('Cound not parse wind_gust')

try:
    wind_speed = '{:.2f}'.format(msToKph(parsed['wind']['speed']))
except:
    wind_speed = -1
    logger.error ('Cound not parse wind_speed')

try:
    temp = '{:.2f}'.format(kelvinToCelcius(parsed['main']['temp']))
except:
    temp = -1
    logger.error ('Cound not parse temp')

try:
    temp_min = '{:.2f}'.format(kelvinToCelcius(parsed['main']['temp_min']))
except:
    temp_min = -1
    logger.error ('Cound not parse temp_min')

try:
    temp_max = '{:.2f}'.format(kelvinToCelcius(parsed['main']['temp_max']))
except:
    temp_max = -1
    logger.error ('Cound not parse temp_max')

try:
    temp_feels_like = '{:.2f}'.format(kelvinToCelcius(parsed['main']['feels_like']))
except:
    temp_feels_like = -1
    logger.error ('Cound not parse temp_feels_like')

try:
    humidity = parsed['main']['humidity']
except:
    humidity = -1
    logger.error ('Cound not parse humidity')

try:
    pressure = parsed['main']['pressure']
except:
    pressure = -1
    logger.error ('Cound not parse pressure')

try:
    clouds = parsed['clouds']['all']
except:
    clouds = -1
    logger.error ('Cound not parse clouds')

try:
    sunrise = dt.fromtimestamp(parsed['sys']['sunrise'])
except:
    sunrise = '1981-02-10 00:00:00'
    logger.error ('Cound not parse sunrise')

try:
    sunset = dt.fromtimestamp(parsed['sys']['sunset'])
except:
    sunset = '1981-02-10 00:00:00'
    logger.error ('Cound not parse sunset')

try:
    visibility = parsed['visibility']
except:
    visibility = -1
    logger.error ('Cound not parse visibility')

try:
    wx_description = parsed['weather'][0]['description']
except:
    wx_description = 'error'
    logger.error ('Cound not parse wx_description')

wx = {
    "calc_time": calc_time,
    "wind_deg": wind_deg,
    "wind_gust": wind_gust,
    "wind_speed": wind_speed,
    "temp": temp,
    "temp_min": temp_min,
    "temp_max": temp_max,
    "temp_feels_like": temp_feels_like,
    "humidity": humidity,
    "pressure": pressure,
    "clouds": clouds,
    "sunrise": sunrise,
    "sunset": sunset,
    "visibility": visibility,
    "wx_description": wx_description,
}

logger.debug (wx)
logger.info ("calc_time       : " + str(calc_time))
logger.info ("wind_deg        : " + str(wind_deg))
logger.info ("wind_gust       : " + str(wind_gust))
logger.info ("wind_speed      : " + str(wind_speed))
logger.info ("temp            : " + str(temp))
logger.info ("temp_min        : " + str(temp_min))
logger.info ("temp_max        : " + str(temp_max))
logger.info ("temp_feels_like : " + str(temp_feels_like))
logger.info ("humidity        : " + str(humidity))
logger.info ("pressure        : " + str(pressure))
logger.info ("clouds          : " + str(clouds))
logger.info ("sunrise         : " + str(sunrise))
logger.info ("sunset          : " + str(sunset))
logger.info ("visibility      : " + str(visibility))
logger.info ("wx_description  : " + str(wx_description))

database.upload_wx(wx, True)
