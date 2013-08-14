#!/usr/bin/python

# Program written by Max Vernimmen
# This connects via bluetooth to the enymate reader and sends a 'read'
# command. After that it keeps on receiving data and printing it
# until you kill it.

import serial
import string
import time
import bluetooth
import binascii

def parseSensorsOutputLinux(output):
    return int(round(float(output) / 1000))

def connect():
    while(True):    
        try:
            gaugeSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            gaugeSocket.connect(('00:0B:CE:05:18:29', 1))
            break;
        except bluetooth.btcommon.BluetoothError as error:
            gaugeSocket.close()
            print "Could not connect: ", error, "; Retrying in 10s..."
            time.sleep(10)
    return gaugeSocket;

def analyse(receivedData):
	#so we've received some data... what does it mean?
	#als de eerste 3 bytes x00 x0f x00 zijn dan is het een meter uitput
	#byte 4: sensor nr
	#bytes 5-9 data
	#byte 10: altijd x41
	#byte 11: status byte. onbekend wat we daar mee moeten.

	print " Entering analyse"
	#for x in receivedData:
	#	print x

	#if receivedData[0]:
	#	if receivedData[0] == b'\x00':
	#		print "1st byte was 0x00!"
	#	else:
	#		print "1st byte not recognised as 0x00: %s" % receivedData[0].encode('hex')
	#if receivedData[1]:
	#	if receivedData[1] == b'\x0f':
	#		print "1st byte was 0x0f!"
	#	else:
	#		print "1st byte not recognised as 0x0f: %s" % receivedData[0].encode('hex')
	if (receivedData[0] == b'\x00') and (receivedData[1] == b'\x0f') and (receivedData[2] == b'\x00') and ( (receivedData[9] == b'\x40') or (receivedData[9] == b'\x41') ) :
		type="ok"
		#probably need to add a base value to get the ascii representation of 1-4 here
	else:
		print "analysis says this was an invalid message"
		return
	
	if (type=="ok"):
		print "sensor number is: %s" % receivedData[3].encode('hex')
		if ( b'\x41' <= receivedData[3] <= b'\x45' ):
			print "this is a water sensor"
		elif ( b'\x81' <= receivedData[3] <= b'\x89' ):
			print "this is a gas sensor"
		elif ( b'\x01' <= receivedData[3] <= b'\xff' ):
			print "this is an electricity sensor"



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
	while(len(data) < 11):
		data +=gaugeSocket.recv(512)
		print "waiting for more data"
	print "[%s] received packet of size %d" % (time.strftime('%Y-%m-%d %H:%M:%S'), len(data))
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

