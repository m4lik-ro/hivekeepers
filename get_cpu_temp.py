from gpiozero import CPUTemperature
import logging
from logging.config import fileConfig

fileConfig('log.ini', defaults={'logfilename': 'bee.log'})
logger = logging.getLogger('default')


import database
cpu_temp = CPUTemperature().temperature
logger.info("CPU temp is " + str(cpu_temp) + "C")

output = database.send_data ('cpu_temp', cpu_temp, table=database.get_host_name(), verbose=True)
#output = database.send_data ('cpu_temp', cpu_temp, table="hive1", verbose=True)
#output = database.send_data ('cpu_temp', cpu_temp, table="hive2", verbose=True)
#output = database.send_data ('cpu_temp', cpu_temp, table="hive3", verbose=True)

