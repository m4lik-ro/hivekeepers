#!/usr/bin/env python

import bme680
import argparse
import logging
from logging.config import fileConfig

fileConfig('log.ini', defaults={'logfilename': 'bee.log'})
logger = logging.getLogger('bme680')



def read_from_sensor (addr):
    try:
        sensor = bme680.BME680(addr)
        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
    except:
        logger.debug('ERROR: Could not connect to sensor')
        logger.debug('       Ensure i2c is turned on via raspi-config')
        logger.debug('       Check wires')
        return False, None
    
    try:
        while True:
            if sensor.get_sensor_data():
                temperature = '{0:.2f}'.format(sensor.data.temperature)
                pressure = '{0:.2f}'.format(sensor.data.pressure)
                humidity = '{0:.2f}'.format(sensor.data.humidity)
                return True, {"temperature":temperature, "pressure":pressure, "humidity":humidity}
    except:
        logger.debug ('ERROR: Could not get sensor data')
        return False, None

def write_to_database(results):
    import database
    database.send_data ('temperature_' + results['label'], results['temperature'])
    database.send_data ('pressure_' + results['label'], results['pressure'])
    database.send_data ('humidity_' + results['label'], results['humidity'])

    database.send_data ('temperature_' + results['label'], results['temperature'], table=database.get_host_name())
    database.send_data ('pressure_' + results['label'], results['pressure'], table=database.get_host_name())
    database.send_data ('humidity_' + results['label'], results['humidity'], table=database.get_host_name())
    return None


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-s", "--secondary", help="use the secondary ic2 address (solder blob)", action="store_true")
    parser.add_argument("-d", "--nodb", help="dont write to the database", action="store_true")
    args = parser.parse_args()

    # Check for --version or -V
    if args.version:
        logger.debug("Temp, Pressure and RH - version 0.1")

    if args.secondary:
        i2c_addr = bme680.I2C_ADDR_SECONDARY
    else:
        i2c_addr = bme680.I2C_ADDR_PRIMARY
    logger.debug ('i2c addr:       ' + hex(i2c_addr))

    if args.nodb:
        writeToDatabase = False
    else:
        writeToDatabase = True
    logger.debug ('writeToDatabase:' + str(writeToDatabase))

    b_return, results = read_from_sensor(i2c_addr)
    if b_return:
        logger.info ("BME680 (%s): %sC, %shPa, %s%%" % (hex(i2c_addr), results['temperature'], results['pressure'], results['humidity']))
        if writeToDatabase:
            results['label'] = 'primary' if i2c_addr == bme680.I2C_ADDR_PRIMARY else 'secondary'
            write_to_database(results)
    else:
        logger.info ("BME680:Could not get data")
    
if __name__ == "__main__":
   main()