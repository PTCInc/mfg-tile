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
from struct import pack, unpack

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
log.setLevel(logging.CRITICAL)

#---------------------------------------------------------------------------#
# FAE Sensor Configuration
#---------------------------------------------------------------------------#
from sense_hat import SenseHat
#---------------------------------------------------------------------------#
# define your callback process
#---------------------------------------------------------------------------#
def initialize():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    IP_Address = s.getsockname()[0]
    s.close()
    sense = SenseHat()
    return IP_Address, sense

def updating_writer(a):
    ''' A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    '''
    context  = a[0]
    sense = a[1]
    register = 3
    slave_id = 0x00
    address  = 0x00
    values   = context[slave_id].getValues(register, address, count=24)

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

def float_to_uint16(number):
    i1, i2 = unpack('HH', pack('f', number))
    return i1, i2

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
time = 1 # 5 seconds delay
IP_Address, sense = initialize()
print(sense.temperature)
loop = LoopingCall(f=updating_writer, a=(context,sense))
loop.start(time, now=False) # initially delay by time
StartTcpServer(context, identity=identity, address=(IP_Address, 502))
