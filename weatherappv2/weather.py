import forecastio # https://github.com/ZeevG/python-forecast.io
from dotstar import Adafruit_DotStar
import time
from time import gmtime, strftime
from pprint import pprint
from firelog import firelog
from color import Color
import math
import threading
import json
import os, sys

LED_COUNT = 7
API_TIMER = 60 * 1 # seconds
PRECIP_PROBABILITY = 0.2
GLOBAL_BRIGHTNESS = 0.25

# color settings
clear_day = rain = Color(116, 127, 223)
clear_night = Color(35, 45, 171, 0.2)
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
data = None
logger = None
active = False

def init():
  global data, logger, lat, lng
  # load config file
  try:
    with open('/home/pi/weatherappv2/config.json') as data_file:    
      data = json.load(data_file)
      logger = firelog(data['product_name'], data['guid'], data)
      logger.log_status('Initialized.')
      updateWeather()
  except:
    print "Error: Could not load config.json file", sys.exc_info()[0]


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

def updateWeather():
  
  global loopCount
  global thread
  global API_TIMER
  global precipHours
  global data
  global active
  global strip

  print data['api_key']
  print data['lat']
  print data['lng']
  print "----"

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
