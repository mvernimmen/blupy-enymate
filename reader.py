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

gaugeSocket = connect()

#make sure we close the connection when we get killed
import signal
import sys
#def signal_handler(signal, frame):
#        print 'You pressed Ctrl+C!'
#	if gaugeSocket:
#		print ' sending termination to enymate'
#		gaugeSocket.send(str("\xF6"))
#		gaugeSocket.close()
#        sys.exit(0)
#signal.signal(signal.SIGINT, signal_handler)

gaugeSocket.send(str("\xF9"))
print("The get usage command has been sent: " + str("\xF9"))

while(True):
    try:
        data = gaugeSocket.recv(512)
	if len(data) == 0: break
#	if len(data) != 11: data.append(gaugeSocket.recv(512))
	print "[%s] received packet of size %d" % (time.strftime('%Y-%m-%d %H:%M:%S'), len(data))
	print " in hex: "
	for x in data:
		print ("%s" % x.encode('hex')),
	print ""
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
