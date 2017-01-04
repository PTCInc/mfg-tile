#!/usr/bin/env python
'''
Pymodbus Server With Updating Thread
--------------------------------------------------------------------------

This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::

    from threading import Thread

    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
'''
#---------------------------------------------------------------------------#
# import the modbus libraries we need
#---------------------------------------------------------------------------#
from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

#---------------------------------------------------------------------------#
# import the twisted libraries we need
#---------------------------------------------------------------------------#
from twisted.internet.task import LoopingCall
import socket

#---------------------------------------------------------------------------#
# configure the service logging
#---------------------------------------------------------------------------#
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------#
# FAE Sensor Configuration
#---------------------------------------------------------------------------#
from ctypes import cdll
fae_agent = cdll.LoadLibrary("/home/pi/Documents/twc_agent.so")
fae_init = fae_agent.fae_init
queryADT75 = fae_agent.queryADT75
querySHT21_Temp = fae_agent.querySHT21_Temp
querySHT21_Humidity = fae_agent.querySHT21_Humidity
queryADXL_x=fae_agent.queryADXL_x
queryADXL_y=fae_agent.queryADXL_y
queryADXL_z=fae_agent.queryADXL_z
queryTSL = fae_agent.queryTSL
queryMPL_Pressure = fae_agent.queryMPL_Pressure
queryMPL_Altitude = fae_agent.queryMPL_Altitude



#import sys
#import Adafruit_DHT

#sensor = Adafruit_DHT.DHT11
#pin = 17

#---------------------------------------------------------------------------#
# define your callback process
#---------------------------------------------------------------------------#
def initialize():
    fae_init()
    temperatureADT75 = queryADT75()
    temperatureSHT21 = querySHT21_Temp()
    humidity = querySHT21_Humidity()
    accelX  = queryADXL_x()
    accelY  = queryADXL_y()
    accelZ  = queryADXL_z()
    lux = queryTSL()
    pressure = queryMPL_Pressure()
    altitude = queryMPL_Altitude()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    IP_Address = s.getsockname()[0]
    s.close()
    return IP_Address

def updating_writer(a):
    ''' A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    '''
    log.debug("updating the context")
    context  = a[0]
    register = 3
    slave_id = 0x00
    address  = 0x00
    values   = context[slave_id].getValues(register, address, count=8)
    temperatureADT75 = queryADT75()
    temperatureSHT21 = querySHT21_Temp()
    humidity = querySHT21_Humidity()
    accelX  = queryADXL_x()
    accelY  = queryADXL_y()
    accelZ  = queryADXL_z()
    lux = queryTSL()
    pressure = queryMPL_Pressure()
    altitude = queryMPL_Altitude()

    # humidity, bull = (random.randint(0,9), random.randint(0,9))

    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!
   # if humidity is None or temperature is None:
#	print 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
#    if humidity is None or temperature is None:
#	humidity, temperature = (0, 0)

    values[0] = temperatureADT75
    values[1] = temperatureSHT21
    values[2] = humidity
    values[3] = accelX
    values[4] = accelY
    values[5] = accelZ
    values[6] = lux
    values[7] = pressure
    # values[8] = altitude
    log.debug("new values: " + str(values))
    context[slave_id].setValues(register, address, values)

#---------------------------------------------------------------------------#
# initialize your data store
#---------------------------------------------------------------------------#
store = ModbusSlaveContext(
    di = ModbusSequentialDataBlock(0, [1]*100),
    co = ModbusSequentialDataBlock(0, [2]*100),
    hr = ModbusSequentialDataBlock(0, [3]*100),
    ir = ModbusSequentialDataBlock(0, [4]*100))
context = ModbusServerContext(slaves=store, single=True)

#---------------------------------------------------------------------------#
# initialize the server information
#---------------------------------------------------------------------------#
identity = ModbusDeviceIdentification()
identity.VendorName  = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName   = 'pymodbus Server'
identity.MajorMinorRevision = '1.0'

#---------------------------------------------------------------------------#
# run the server you want
#---------------------------------------------------------------------------#
time = 5 # 5 seconds delay
IP_Address = initialize()
loop = LoopingCall(f=updating_writer, a=(context,))
loop.start(time, now=False) # initially delay by time
StartTcpServer(context, identity=identity, address=(IP_Address, 502))
