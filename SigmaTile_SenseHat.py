#!/usr/bin/env python

#---------------------------------------------------------------------------#
# Import Packages and Functions
#---------------------------------------------------------------------------#

import pymodbus.server.async as psa
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

from struct import pack, unpack

from time import sleep

import socket
import logging
import threading

from sense_hat import SenseHat

#---------------------------------------------------------------------------#
# Package Modifications
#---------------------------------------------------------------------------#

#---------------------------------------------------------------------------#
# Worker Functions
#---------------------------------------------------------------------------#
def update_datastore(sense, context): # Updates the sensors

    sleep(3)
    logging.debug('Polling Sensors')
    register = 3
    slave_id = 0x00
    address  = 0x00

    while (True):
       	newValues = []

        newValues.extend(float_to_uint16(sense.temperature))
    	newValues.extend(float_to_uint16(sense.humidity))
    	newValues.extend(float_to_uint16(sense.pressure))

    	acceleration = sense.accel_raw
    	newValues.extend(float_to_uint16(acceleration["x"]))
    	newValues.extend(float_to_uint16(acceleration["y"]))
    	newValues.extend(float_to_uint16(acceleration["z"]))

    	gyroscope = sense.gyro_raw
    	newValues.extend(float_to_uint16(gyroscope["x"]))
    	newValues.extend(float_to_uint16(gyroscope["y"]))
    	newValues.extend(float_to_uint16(gyroscope["z"]))

    	orientation = sense.orientation
    	newValues.extend(float_to_uint16(orientation["roll"]))
    	newValues.extend(float_to_uint16(orientation["pitch"]))
    	newValues.extend(float_to_uint16(orientation["yaw"]))


    	context[slave_id].setValues(register, address, newValues)

def display_manager(sense, context, IP_Address):
    r = [255,0,0]
    o = [255,127,0]
    y = [255,255,0]
    w = [255,255,255]
    g = [0,120,0]
    lg =[0,100,0]
    b = [0,0,255]
    i = [75,0,130]
    v = [159,0,255]
    e = [0,0,0]

    good_image = [
        e,e,g,g,g,g,e,e,
        e,g,g,g,g,g,g,e,
        g,g,g,g,g,w,g,g,
        g,g,g,g,w,g,g,g,
        g,w,g,g,w,g,g,g,
        g,g,w,w,g,g,g,g,
        e,g,g,w,g,g,g,e,
        e,e,g,g,g,g,e,e,
        ]
    connecting_images = []
    connecting_images.append([
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,b,b,e,e,e,
        e,e,b,e,e,b,e,e,
        e,e,e,e,e,e,e,e,
        ])
    connecting_images.append([
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,b,b,b,b,e,e,
        e,b,e,e,e,e,b,e,
        e,e,e,b,b,e,e,e,
        e,e,b,e,e,b,e,e,
        e,e,e,e,e,e,e,e,
        ])
    connecting_images.append([
        e,e,b,b,b,b,e,e,
        e,b,e,e,e,e,b,e,
        b,e,e,e,e,e,e,b,
        e,e,b,b,b,b,e,e,
        e,b,e,e,e,e,b,e,
        e,e,e,b,b,e,e,e,
        e,e,b,e,e,b,e,e,
        e,e,e,e,e,e,e,e,
        ])
    alert_image = [
        e,e,e,y,e,e,e,e,
        e,e,e,y,e,e,e,e,
        e,e,y,r,y,e,e,e,
        e,e,y,r,y,e,e,e,
        e,y,y,r,y,y,e,e,
        e,y,y,y,y,y,e,e,
        y,y,y,r,y,y,y,e,
        y,y,y,y,y,y,y,e,
        ]
    broken_image = [
        e,e,r,r,r,r,e,e,
        e,w,r,r,r,r,w,e,
        r,r,w,r,r,w,r,r,
        r,r,r,w,w,r,r,r,
        r,r,r,w,w,r,r,r,
        r,r,w,r,r,w,r,r,
        e,w,r,r,r,r,w,e,
        e,e,r,r,r,r,e,e,
        ]
    previousValues = 100

    for i in range (0, 3):
        sense.show_message(IP_Address)

    logging.info('Initialization Complete')
    while(True):
        #logging.info('Number of Connections {0}'.format(number_connections))
        values = context[0x00].getValues(3, 0x18, count=1)
        if values[0] != previousValues:
            logging.info('Screen State Changing')
	    previousValues = values[0]
            if values[0] == 0:
                sense.set_pixels(good_image)
            elif values[0] == 1:
                sense.set_pixels(alert_image)
            elif values[0] == 2:
                sense.set_pixels(broken_image)
            else:
                sense.show_message('PTC Sigma Tile')
        else:
            sleep(1)



#---------------------------------------------------------------------------#
# Helper Functions
#---------------------------------------------------------------------------#
def float_to_uint16(number):
    i1, i2 = unpack('HH', pack('f', number))
    return i1, i2

def initialize(): # Function Initialization
    network_connected = False
    connecting_images = []
    sense = SenseHat()
    e = [0,0,0]
    b = [0,0,255]
    connecting_images.append([
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,b,b,e,e,e,
        e,e,b,e,e,b,e,e,
        e,e,e,e,e,e,e,e,
        ])
    connecting_images.append([
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,e,e,e,e,e,e,
        e,e,b,b,b,b,e,e,
        e,b,e,e,e,e,b,e,
        e,e,e,b,b,e,e,e,
        e,e,b,e,e,b,e,e,
        e,e,e,e,e,e,e,e,
        ])
    connecting_images.append([
        e,e,b,b,b,b,e,e,
        e,b,e,e,e,e,b,e,
        b,e,e,e,e,e,e,b,
        e,e,b,b,b,b,e,e,
        e,b,e,e,e,e,b,e,
        e,e,e,b,b,e,e,e,
        e,e,b,e,e,b,e,e,
        e,e,e,e,e,e,e,e,
        ])
    while (network_connected==False):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("gmail.com",80))
            IP_Address = s.getsockname()[0]
            s.close()
        except:
            for image in range(3):
                sense.set_pixels(connecting_images[image])
                sleep(1)
        else:
            network_connected = True
    return IP_Address, sense

#---------------------------------------------------------------------------#
# Main Function
#---------------------------------------------------------------------------#

# Define global connections variable
#number_connections = 0

# Set logging
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

# Initialize your data store
store = ModbusSlaveContext(
    di = ModbusSequentialDataBlock(0, [1]*100),
    co = ModbusSequentialDataBlock(0, [2]*100),
    hr = ModbusSequentialDataBlock(0, [0]*100),
    ir = ModbusSequentialDataBlock(0, [4]*100))
context = ModbusServerContext(slaves=store, single=True)

# Initialize the server information
identity = ModbusDeviceIdentification()
identity.VendorName  = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName   = 'pymodbus Server'
identity.MajorMinorRevision = '1.0'


# Run the server you want
time = 1 # 5 seconds delay
IP_Address, sense = initialize()
Query = threading.Thread(name = 'Query', target = update_datastore, args = (sense, context))
Query.setDaemon(True)
Query.start()

Screen = threading.Thread(name = 'Screen', target = display_manager, args = (sense, context, IP_Address))
Screen.setDaemon(True)
Screen.start()

psa.StartTcpServer(context, identity=identity, address=(IP_Address, 502))
