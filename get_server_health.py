import shutil
import logging
from logging.config import fileConfig
import sys
import socket


fileConfig('log.ini', defaults={'logfilename': 'bee.log'})
logger = logging.getLogger('health')

# get hard drive space
total, used, free = shutil.disk_usage("/")
percent_used = used / total * 100.0
percent_used = '{:0.2f}'.format(percent_used)
logger.info ("Hard drive (total)  : %d GiB" % (total // (2**30)))
logger.info ("Hard drive (used)   : %d GiB" % (used // (2**30)))
logger.info ("Hard drive (free)   : %d GiB" % (free // (2**30)))
logger.info ("Hard drive (%% used) : %s%%" % percent_used)


# add data to database
import mysql.connector

mydb = mysql.connector.connect(
  host="45.76.113.79",
  database="hivekeeper",
  user="pi_write",
  password=")b*I/j3s,umyp0-8"
)

mycursor = mydb.cursor()
sql = "INSERT INTO `server_health` (host, sensor_id, value) VALUES (%s, %s, %s)"
val = (socket.gethostname(), "hard_drive_space_free", percent_used)
mycursor.execute(sql, val)
mydb.commit()
logger.debug (str(mycursor.rowcount) + " record inserted.")