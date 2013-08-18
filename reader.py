#!/usr/bin/python

# Program written by Max Vernimmen
# This connects via bluetooth to the enymate reader and sends a 'read'
# command. After that it keeps on receiving data and printing it
# until you kill it.

# License: GPL v3 - details in LICENSE.txt

import serial
import string
import time
import bluetooth


##
## User configuration settings
##

ENYMATE_BLUETOOTH_MAC = '00:0B:CE:05:18:29'
#VERBOSE = True
VERBOSE = False
#OUTPUT_MYSQL = True

##
## End of user Configuration settings
##



def parseSensorsOutputLinux(output):
    return int(round(float(output) / 1000))

def connect():
    while(True):
        try:
            gaugeSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            gaugeSocket.connect((ENYMATE_BLUETOOTH_MAC, 1))
            break;
        except bluetooth.btcommon.BluetoothError as error:
            gaugeSocket.close()
            print "Could not connect: ", error, "; Retrying in 10s..."
            time.sleep(10)
    return gaugeSocket;

def analyse(receivedData):

	if VERBOSE:
	    print " Entering analyse"
	    if receivedData[0]:
		if receivedData[0] == b'\x00':
			print "1st byte was 0x00!"
		else:
			print "1st byte not recognised as 0x00: %s" % receivedData[0].encode('hex')

	if (receivedData[0] == b'\x00') and (receivedData[1] == b'\x0f') and (receivedData[2] == b'\x00') and ( (receivedData[9] == b'\x40') or (receivedData[9] == b'\x41') ) :
		type="ok"
	else:
		print "analysis says this was an invalid message. Ignoring"
		return
	
	if (type=="ok"):

		b_data=bytearray(receivedData)

		#clear bit 7 os MSB because it's reserved for energy export,
		# although the device can't measure that.
		if VERBOSE:
		    print "debug before: %s %s %s" % (b_data[6], b_data[7], b_data[8])
		b_data[6] = b_data[6] & 0b01111111
		if VERBOSE:
		    print "debug after: %s %s %s" % (b_data[6], b_data[7], b_data[8])

		impulsFactor = (256 * b_data[4] ) + b_data[5]
		if VERBOSE:
		    print "impulsfactor= %s" % impulsFactor

		timeInterval = 2.028 * ( (256 * 256 * b_data[6]) + ( 256 * b_data[7]) + b_data[8] )
		if VERBOSE:
		    print "timeinterval= %s" % timeInterval
		    print "sensor number is: %s" % receivedData[3].encode('hex')

		if ( b'\x41' <= receivedData[3] <= b'\x45' ):
			value = 3600000000 / ( impulsFactor * timeInterval * 60 )
			print "This is a water sensor. measurement value is: %s m3" % value
		elif ( b'\x81' <= receivedData[3] <= b'\x89' ):
			value = 3600000 / ( impulsFactor * timeInterval )
			print "This is a gas sensor. measurement value is: %s m3" % value
		elif ( b'\x01' <= receivedData[3] <= b'\xff' ):
			value = 3600000000 / ( impulsFactor * timeInterval )
			print "This is an electricity sensor. measurement value is: %s Watt" % value

	#when trailing byte is 40h instead of 41h, then the info is the 'timeout' info for where there were no measurements for that sensor
	print ""



## --------------------------- main program start -----------------------------


gaugeSocket = connect()

#make sure we close the connection when we get killed
import signal
import sys
def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
	if gaugeSocket:
		print ' sending termination to enymate'
		gaugeSocket.send(str("\xF6"))
		gaugeSocket.close()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

gaugeSocket.send(str("\xF9"))
print("The get usage command has been sent: F9h")

while(True):
    try:
        data = gaugeSocket.recv(512)
	if len(data) == 0: break
	print ""
	while(len(data) < 11):
		data +=gaugeSocket.recv(512)
		if VERBOSE:
		    print "waiting for more data"
	print "[%s] received packet of size %d" % (time.strftime('%Y-%m-%d %H:%M:%S'), len(data))
	if VERBOSE:
	    print " in hex: ",
	    for x in data:
	    	print ("%s" % x.encode('hex')),
	    print ""
	analyse(data)

    except bluetooth.btcommon.BluetoothError as error:
        print "Caught BluetoothError: ", error
	print " trying new connection in 5 seconds"
        time.sleep(5)
        gaugeSocket = connect()
        pass
    except:
	print "Unexpected error: ", sys.exc_info()[0], sys.exc_info()[1]
	gaugeSocket.send(str("\xF6"))
	gaugeSocket.close()

gaugeSocket.close()

