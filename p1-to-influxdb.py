#
# DSMR P1 uitlezer
# (c) 11-2017 2016 - GJ - gratis te kopieren en te plakken
#  11-2019 - Leon Teheux - Extended with InfluxDB integration (UDP to remote host)
versie = "1.2"
import sys
import serial
import time
import socket

################
#Error display #
################
def show_error():
    ft = sys.exc_info()[0]
    fv = sys.exc_info()[1]
    print("Fout type: %s" % ft )
    print("Fout waarde: %s" % fv )
    return

#We define UDP port used by InfluxDB on remote host. Make sure the InfluxDB listens on this IP also!
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('192.168.100.100', 8126)

################################################################################################################################################
#Main program
################################################################################################################################################
#print ("DSMR 5.0 P1 uitlezer",  versie)
#print ("Control-C om te stoppen")

#Set COM port config
ser = serial.Serial()
#Actual baudrate may depend on your smart meter. Check this first.
ser.baudrate = 115200
ser.bytesize=serial.EIGHTBITS
ser.parity=serial.PARITY_NONE
ser.stopbits=serial.STOPBITS_ONE
ser.xonxoff=0
ser.rtscts=0
ser.timeout=20
ser.port="/dev/ttyUSB0"

while True:
	#Open COM port
	try:
	    ser.open()
	except:
	    sys.exit ("Fout bij het openen van %s. Programma afgebroken."  % ser.name)      


	#Initialize
	# stack is mijn list met de 26 regeltjes.
	p1_teller=0
	stack=[]

	while p1_teller < 26:
	    p1_line=''
	#Read 1 line
	    try:
	        p1_raw = ser.readline()
	    except:
	        sys.exit ("Seriele poort %s kan niet gelezen worden. Programma afgebroken." % ser.name )      
	    p1_str=str(p1_raw)
	    p1_line=p1_str.strip()
	    stack.append(p1_line)
	# als je alles wil zien moet je de volgende line uncommenten
	#    print (p1_line)
	    p1_teller = p1_teller +1
	
	#Initialize
	# stack_teller is mijn tellertje voor de 26 weer door te lopen. Waarschijnlijk mag ik die p1_teller ook gebruiken
	stack_teller=0
	meter=0
	
	#We can either configure InfluxDB to not use nanoseconds or we can adjust the input (as we're doing here with the epoch_time variable).	
	#We're using a InflixDB called "Youless" here. Feel free to configure a beter name.
	while stack_teller < 26:
	# Dal tarief, opgenomen vermogen 1-0:1.8.1
		if stack[stack_teller][0:9] == "1-0:1.8.1":
			epoch_time = int(time.time())*1000000000
			influxformatusage = 'youless,type=stroom daldag=' + format(stack[stack_teller][10:16]) + ' ' + format(epoch_time)
			sock.sendto(influxformatusage, addr)
			meter = meter +  int(float(stack[stack_teller][10:16]))
	# Piek tarief, opgenomen vermogen 1-0:1.8.2
		elif stack[stack_teller][0:9] == "1-0:1.8.2":
			epoch_time = int(time.time())*1000000000
			influxformatusage = 'youless,type=stroom piekdagdag=' + format(stack[stack_teller][10:16]) + ' ' + format(epoch_time)
			sock.sendto(influxformatusage, addr)
			meter = meter + int(float(stack[stack_teller][10:16]))
	# Daltarief, teruggeleverd vermogen 1-0:2.8.1
	   elif stack[stack_teller][0:9] == "1-0:2.8.1":
			epoch_time = int(time.time())*1000000000
			influxformatusage = 'youless,type=stroom daldag-terug=' + format(stack[stack_teller][10:16]) + ' ' + format(epoch_time)
			sock.sendto(influxformatusage, addr)
			meter = meter - int(float(stack[stack_teller][10:16]))
	# Piek tarief, teruggeleverd vermogen 1-0:2.8.2
	   elif stack[stack_teller][0:9] == "1-0:2.8.2":
			epoch_time = int(time.time())*1000000000
			influxformatusage = 'youless,type=stroom piekdagdag-terug=' + format(stack[stack_teller][10:16]) + ' ' + format(epoch_time)
			sock.sendto(influxformatusage, addr)
			meter = meter - int(float(stack[stack_teller][10:16]))
	# Totaal meterstand
	# volgende rij uncommenten om een berekening van vorige jaren eraf te tellen.
			#meter = meter + 1751
			epoch_time = int(time.time())*1000000000
			influxformatusage = 'youless,type=stroom metertotaal=' + format(stack[stack_teller][10:16]) + ' ' + format(epoch_time)
			sock.sendto(influxformatusage, addr)
	# Huidige stroomafname: 1-0:1.7.0
	   elif stack[stack_teller][0:9] == "1-0:1.7.0":
			epoch_time = int(time.time())*1000000000
                        kwh = float(stack[stack_teller][10:16])*1000
			influxformatusage = 'youless,type=stroom Huidig-verbruik=' + format(kwh) + ' ' + format(epoch_time)
			sock.sendto(influxformatusage, addr)
	# Huidig teruggeleverd vermogen: 1-0:1.7.0
	   elif stack[stack_teller][0:9] == "1-0:2.7.0":
			epoch_time = int(time.time())*1000000000
			kwh = float(stack[stack_teller][10:16])*1000
			influxformatusage = 'youless,type=stroom Huidig-teruglever=' + format(kwh) + ' ' + format(epoch_time)
			sock.sendto(influxformatusage, addr)
	# Gasmeter: 0-1:24.2.1
	   elif stack[stack_teller][0:10] == "0-1:24.2.1":
			epoch_time = int(time.time())*1000000000
			influxformatusage = 'youless,type=stroom gasMeter-totaal=' + format(stack[stack_teller][26:35]) + ' ' + format(epoch_time)
			sock.sendto(influxformatusage, addr)
	   else:
		pass
	   stack_teller = stack_teller +1

#Debug
#print (stack, "\n")
    
#Close port and show status
	try:
	    ser.close()
	except:
	    sys.exit ("Oops %s. Programma afgebroken." % ser.name )      
time.sleep(10)
