#!/usr/bin/python 
import serial
import socket
import struct
import time 
import sys

#We load the datamap that translates Serial inputs and define the serial interface.
from datamap import datamap, fmt
ser = serial.Serial('/dev/ttyUSB0', 
    baudrate=9600, 
    timeout=0, 
    parity='N', 
    bytesize=8,
    stopbits=1
)
print 'serial open', ser.isOpen()

#We define UDP port used by InfluxDB on localhost
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('localhost', 8125)

#Serial Interfacing magic codes
RemehaSerialString = "\x02\xFE\x01\x05\x08\x02\x01\x69\xAB\x03"

#Time to get the data from Serial
def parse_data(data):
    for n, x in enumerate(data):
        value = datamap[n][1](x)
        if isinstance(value, list):
            for i in zip(datamap[n][2], value, datamap[n][5]):
                if i[0]:
                    yield i
        elif datamap[n][2]:
            if value < 0:
                yield datamap[n][2], 0, datamap[n][5]
            yield datamap[n][2], value, datamap[n][5]

while True:
    sys.stdout.flush()
    ser.write(RemehaSerialString)
    time.sleep(1)
 
    data = ser.read(ser.inWaiting())
    unpacked = struct.unpack(fmt, data)

    stats = list(parse_data(unpacked))
    for stat in stats:
    #We can either configure InfluxDB to not use nanoseconds or we can adjust the input (as we're doing here).
	epoch_time = int(time.time())*1000000000
        influxformat = 'serial,type=cv {}={}'.format(*stat) + ' ' + str(epoch_time)
        sock.sendto(influxformat, addr)
        assert not ser.inWaiting()
    #Define data resolution here. 5 second by default
    time.sleep(5)

print 'kthxbye'

