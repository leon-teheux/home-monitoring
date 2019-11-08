#!/usr/bin/python
import socket
import time
import subprocess

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#We define UDP port used by InfluxDB on localhost
addr = ('localhost', 8126)
while True:
     #We get the data from the Youless. Use your own IP here.
     wgetcmdusage = "wget http://192.168.0.251/a -q -O - |grep 'l\/\u'|sed s/\ 'l\/u'//|sed s/\,/\./|sed s/^\ //"
     wgetcmdtotal = "wget http://192.168.0.251/a -q -O - |grep m3|sed s/\ m3//|sed s/\,/\./|sed s/^\ //"
     inputusage = str.rstrip(subprocess.check_output(wgetcmdusage, shell=True))
     inputtotal = str.rstrip(subprocess.check_output(wgetcmdtotal, shell=True))
     inputtotalformatted = inputtotal.replace(",",".")
     #We can either configure InfluxDB to not use nanoseconds or we can adjust the input (as we're doing here).
     epoch_time = int(time.time())*1000000000
     #Converting to proper format for InfluxDB and send it over.
     influxformatusage = 'youless,type=gas liter/u=' + str(inputusage) + ' ' + str(epoch_time)
     influxformattotal = 'youless,type=gas m3totaal=' + str(inputtotalformatted) + ' ' + str(epoch_time)
     sock.sendto(influxformatusage, addr)
     sock.sendto(influxformattotal, addr)
     #Pick your own data-resolution here. 3 seconds by default.
     time.sleep(3)
print 'kthxbye'

