blupy-enymate
=============

What is it? A python script to read the enymate sensor device through bluetooth.
Purpose: get data from enymate device and store it into a mysql database for
 later processing and visualisation. A python learning project for its creater.

# details:
The enymate is a device that was sold in the Netherlands in 2009. It allows up
to 3 sensors to be connected to it which can read electricity, gas and water
usage using optical sensors. The creater of enymate provides windows and mac
software, but nothing for linux. It seems enymate is now an empty shell and
is being replaced by sparqle. This program allows owners of the enymate to
take matters into their own hands ;)
I'm developing this python program on a raspberry pi, which I've added a
bluetooth usb device to. This is one of my very first python scripts.
Feedback is appreciated.

# Installation:
get python 2.7, install bluetooth drivers, software, etc
edit this script and fill in the mac address of your enymate (you can find it
with bluetooth scanning tools). pair your enymate with the machine you intend
to run this script on. Then run this script.

Currently (20130813) it receives only realtime data from the enymate but it doesn't
yet interpret it nor does it store anything yet.

