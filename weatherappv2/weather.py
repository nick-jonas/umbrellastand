#!/usr/bin/python

import urllib2
import time
import math
import threading
import json
import os, sys
import forecastio # https://github.com/ZeevG/python-forecast.io
from dotstar import Adafruit_DotStar
from time import gmtime, strftime
from pprint import pprint
from firelog import firelog
from color import Color
from geopy.geocoders import GoogleV3

CONFIG = '/home/weather/config.json'
LED_COUNT = 7
API_TIMER = 60 * 10 # seconds
CONNECTIVITY_TIMER = 15 # seconds
PRECIP_PROBABILITY = 0.2
GLOBAL_BRIGHTNESS = 0.25

# color settings
clear_day = rain = Color(100, 100, 223)
clear_night = Color(0, 0, 255, 0.1)
fog = cloudy = Color(148, 151, 140)
snow = Color(255, 255, 255)

# setup LEDs
datapin   = 10
clockpin  = 11
strip     = Adafruit_DotStar(LED_COUNT, datapin, clockpin)
strip.begin()           # Initialize pins for output
strip.setBrightness(int(GLOBAL_BRIGHTNESS * 255.0)) # Limit brightness to ~1/4 duty cycle

precipHours = []
loopCount = 0
thread = None
connectThread = None
data = None
logger = None
active = False
isInit = False


def init():
  # logger = firelog(data['product_name'], data['guid'], data)
  internetOn(True)

def onInternetConnection():
  global isInit
  loadConfig()
  getCoord()
  updateWeather()
  isInit = True

def internetOn(loop=False):
  global active
  global isInit
  try:
    response=urllib2.urlopen('http://74.125.228.100',timeout=1)
    active = True
    if not isInit: onInternetConnection()
    if loop: startConnectTimer(loop)
    return True
  except urllib2.URLError as err: pass
  active = False
  if loop: startConnectTimer(loop)
  return False

# Load the config.json file
def loadConfig():
  global data
  with open(CONFIG) as data_file:
    data = json.load(data_file)
    print "Loaded config.json..."

# Check to see if coordinates have been geocoded from zip code
def getCoord():
  global data
  if data['lat'] == "" or data['lng'] == "":
    print "Geocoding from zip:", data['zip']
    geolocator = GoogleV3()
    location = geolocator.geocode("10003")
    data['lat'] = str(location.latitude)
    data['lng'] = str(location.longitude)
    print "Found lat/lng: ", data['lat'], data['lng'], "..."
    # write back to file
    with open(CONFIG, 'r+') as f:
      d = json.load(f)
      d['lat'] = data['lat']
      d['lng'] = data['lng']
      f.seek(0) # <--- reset file position to the beginning.
      json.dump(d, f, indent=4)
      print "Wrote lat/lng to file..."
  else:
    print "Lat/Lng exists, moving on..."

# -------------------
# TIMERS
# -------------------

def stopTimer():
  if thread is not None:
    thread.cancel()

def startTimer():
  global thread
  global API_TIMER
  stopTimer()
  thread = threading.Timer(API_TIMER, updateWeather)
  thread.setDaemon(True)
  thread.start()

def stopConnectTimer():
  if connectThread is not None:
    connectThread.cancel()

def startConnectTimer(isLoop):
  global connectThread
  global CONNECTIVITY_TIMER
  stopConnectTimer()
  connectThread = threading.Timer(CONNECTIVITY_TIMER, internetOn, [isLoop])
  connectThread.setDaemon(True)
  connectThread.start()


# -------------------
# GET WEATHER
# -------------------
def updateWeather():
  
  global loopCount
  global thread
  global API_TIMER
  global precipHours
  global data
  global active
  global strip

  try:
    # call forecast.io API to get weather
    forecast = forecastio.load_forecast(data['api_key'], float(data['lat']), float(data['lng']))
    byHour = forecast.hourly()
    
    loopCount += 1
    i = LED_COUNT - 1
    precipHours = []
    print 'Fetched Weather Data ' + str(loopCount) + 'x (' + str(i * API_TIMER) + 's): ' + strftime("%Y-%m-%d %H:%M:%S", gmtime())
    active = True

    # loop through data
    for hourlyData in byHour.data:
      if i > -1:
        # setup default vars
        color = Color(0, 0, 0)
        prob = 0
        type = None

        # get precip type and probability
        if hasattr(hourlyData, 'precipProbability'):
          prob = hourlyData.precipProbability
          print 'probability: ' + str(prob)
        if hasattr(hourlyData, 'precipType'):
          type = hourlyData.precipType

        # handle certain non-precipitation colors
        if hasattr(hourlyData, 'icon'):
          print 'Hour ' + str(LED_COUNT - i) + ': ' + hourlyData.icon
          if(hourlyData.icon == 'clear-day' or hourlyData.icon == 'partly-cloudy-day'):
            color = clear_day
          if(hourlyData.icon == 'clear-night' or hourlyData.icon == 'partly-cloudy-night'):
            color = clear_night
          if(hourlyData.icon == 'fog' or hourlyData.icon == 'cloudy'):
            color = fog

        # handle precipitation
        if prob >= PRECIP_PROBABILITY:
          if type == 'snow':
            print "adding snow, hour: " + str(i)
            precipHours.append(['s', i])
          if type == 'rain':
            print "adding rain, hour: " + str(i)
            color = rain
            precipHours.append(['r', i])
        else:
          if type == 'snow' or type == 'rain':
            color = fog

        print int(color.r), int(color.g), int(color.b)
        strip.setPixelColor(i, int(color.r), int(color.g), int(color.b))

      i -= 1

  except Exception as e:
    print e.__doc__
    print e.message
    active = False

  # call function again
  startTimer()



# initialize
init()

counter = 0
while True:
  counter += 1
  # flash one LED red if there is trouble connecting
  if not active:
    for num in range(1, LED_COUNT):
      strip.setPixelColor(num, 0, 0, 0)
    bri = math.fabs(math.sin(counter * 0.05))
    strip.setPixelColor(0, int(255 * bri), 0, 0)
  else:
    # smooth fade in & out
    for idx, hour in enumerate(precipHours): 
      bri = math.fabs(math.sin((counter + (idx * 25)) * 0.05))
      if hour[0] == 'r':
        precipColor = rain
      elif hour[0] == 's':
        precipColor = snow
      strip.setPixelColor(hour[1], int(precipColor.r * bri), int(precipColor.g * bri), int(precipColor.b * bri))
  strip.show()
  time.sleep(1.0 / 50)             # Pause 20 milliseconds (~50 fps)
