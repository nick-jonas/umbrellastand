#! /usr/bin/python

import socket
import fcntl
import struct
import RPi.GPIO as GPIO
import time

class conn:

  pinNum = 8

  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM) #numbering scheme that corresponds to breakout board and pin layout
  GPIO.setup(pinNum,GPIO.OUT) #replace pinNum with whatever pin you used, this sets up that pin as an output
  #set LED to flash forever

  @staticmethod
  def check_connection():

    print 'Connectivity ---------------'
    ifaces = ['eth0','wlan0']
    connected = []

    i = 0
    for ifname in ifaces:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      try:
        socket.inet_ntoa(fcntl.ioctl(
          s.fileno(),
          0x8915,  # SIOCGIFADDR
          struct.pack('256s', ifname[:15])
        )[20:24])
        connected.append(ifname)
        print "%s is connected" % ifname 
        while True:
          GPIO.output(pinNum,GPIO.HIGH)
          time.sleep(0.5)
          GPIO.output(pinNum,GPIO.LOW)
          time.sleep(0.5)
          GPIO.output(pinNum,GPIO.LOW)
          time.sleep(2.0)
      
      except:
        print "%s is not connected" % ifname

      i += 1
    print '-----------------------------'
    return connected
