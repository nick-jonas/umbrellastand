#!/usr/bin/python

from dotstar import Adafruit_DotStar

LED_COUNT = 7
datapin   = 10
clockpin  = 11
strip     = Adafruit_DotStar(LED_COUNT, datapin, clockpin)
strip.begin()

for num in range(1, LED_COUNT):
	strip.setPixelColor(num, 0, 0, 0)
strip.show()