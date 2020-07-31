import mysql.connector
import socket
import logging

from logging.config import fileConfig

fileConfig('log.ini', defaults={'logfilename': 'bee.log'})
logger = logging.getLogger('database')


mydb = mysql.connector.connect(
  host="45.76.113.79",
  database="hivekeeper",
  user="pi_write",
  password=")b*I/j3s,umyp0-8"
)


def upload_wx(wx, verbose=False):
    
    mycursor = mydb.cursor()

    sql = "INSERT INTO `weather` (dt, location, wind_deg, wind_gust, wind_speed, temp, temp_min, temp_max, temp_feels_like, humidity, pressure, clouds, sunrise, sunset, visibility, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (
        wx['calc_time'],
        wx['location'],
        wx['wind_deg'],
        wx['wind_gust'],
        wx['wind_speed'],
        wx['temp'],
        wx['temp_min'],
        wx['temp_max'],
        wx['temp_feels_like'],
        wx['humidity'],
        wx['pressure'],
        wx['clouds'],
        wx['sunrise'],
        wx['sunset'],
        wx['visibility'],
        wx['wx_description'],
    )
    
    mycursor.execute(sql, val)
    mydb.commit()
    
    if verbose:
        logger.debug (str(mycursor.rowcount) + " record inserted.")
    return True
    
    
def get_host_name():
    return socket.gethostname()
    
def send_data(sensor_id, sensor_value, table=u'raw_data', verbose=False):

    mycursor = mydb.cursor()

    sql = "INSERT INTO `" + table + "` (host, sensor_id, value) VALUES (%s, %s, %s)"
    val = (socket.gethostname(), sensor_id, sensor_value)
    mycursor.execute(sql, val)
    mydb.commit()
    
    if verbose:
        logger.debug (str(mycursor.rowcount) + " record inserted.")
    return True
