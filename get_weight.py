#!/usr/bin/env python3

import serial
import sys
import argparse
import logging
from logging.config import fileConfig

fileConfig('log.ini', defaults={'logfilename': 'bee.log'})
logger = logging.getLogger('openscale')


if sys.version_info<(3,4,2):
  sys.stderr.write("You need python 3.4.2 or later to run this script\n")
  exit(1)



class OpenScale:


    def InitSerialPort(self):
        try:
            self.port = serial.Serial(
                port= self.server_settings['port'],
                baudrate = self.server_settings['baud'],
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=2
            )
            logging.debug("Serial port initialised")
            return True
        except:
            logging.error ("Could not open " + self.server_settings['port'])
            logging.error ("Does this port exist???")
            return False


    def read_serial(self):
        try:
            serialLine = self.port.readline().decode()
            serialLine = serialLine.replace("\r\n", '')
        except UnicodeDecodeError:
            #self.errmsg("invalid Serial string:%s" % serialLine)
            return None
        except serial.serialutil.SerialException as e:
            #self.errmsg("Serial connection failed, pausing for 5 seconds then will try again")
            config_serial(False)
            time.sleep(5)
            return None
    
    def extract_weight_data(self, data):
        weight = data.split(',')[0]
        units = data.split(',')[1]
        return weight, units
    

    def get_measurement(self):

        # wait for \r\n to get stream "in sych"
        while True:
            raw = self.port.readline().decode("utf-8")
            if "Readings:" in raw:
                break
        while True:
            raw = self.port.readline().decode("utf-8")
            if "\r\n" in raw:
                break

        try:
            raw = self.port.readline().decode("utf-8")
            weight, units = self.extract_weight_data(raw)
        except serial.SerialException as e:
            logging.error ("Failed to read from serial port")
            pass
        if raw != None:
            if len(raw) > 0:
                return weight, units

   

    #---------------------------------------------------------------------------
    # Main function called when script executed
    #---------------------------------------------------------------------------
    def __init__(self, server_settings):

        self.server_settings = server_settings
        if not self.InitSerialPort():
            sys.exit()

        
    def __del__(self):
        try:
            self.port.close()
        except:
            pass


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help="Show program version", action="store_true")
    parser.add_argument("-p", "--port", help="define the serial/USB port to connect to")
    parser.add_argument("-b", "--baud", help="define the baud rate (default 9600)")
    parser.add_argument("-d", "--nodb", help="dont write to the database", action="store_true")
    args = parser.parse_args()
    
    # Check for --version or -V
    if args.version:
        logger.info("Weight measurement via OpenScale PCB - version 0.1")
    if not args.port:
        logger.info("A port must be defined. eg: '/dev/ttyUSB0'")
        parser.print_help()
        sys.exit()
    writeToDatabase = False if args.nodb else True
    baud = args.baud if args.baud else 9600
        
    server_settings = {
        "port": args.port,
        "baud": baud
    }
    scale = OpenScale(server_settings)
    weight, units = scale.get_measurement()    
    logging.info ("Weight is " + weight + units)
    
    if writeToDatabase:
        import database
        database.send_data("weight", weight)
        if database.send_data("weight", weight, table=database.get_host_name()):
            logging.info ("Saved to database ok")
        

if __name__ == '__main__':
    main()