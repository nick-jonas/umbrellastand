import forecastio # https://github.com/ZeevG/python-forecast.io
from raspledstrip.ledstrip import *
from time import gmtime, strftime
import math
import threading
from check_connection import conn

LED_COUNT = 8
API_TIMER = 60 * 5 # seconds
CONNECTION_ATTEMPTS = 10
PRECIP_PROBABILITY = 0.2
GLOBAL_BRIGHTNESS = 1

api_key = "8bfc0a79dcda808034c294cf2c89e879"
# New York, NY
lat = 40.7275
lng = -73.9858

# Salt Lake City, UT
#lat = 40.75
#lng = -111.8833

# Great Falls, MT
# lat = 47.5036
# lng = -111.2864

# color settings
clear_day = rain = Color(116, 127, 223, 1)
clear_night = Color(35, 45, 171, 0.2)
fog = cloudy = Color(148, 151, 140, 1)
snow = Color(255, 255, 255, 1)

# setup LED s
led = LEDStrip(LED_COUNT, True)
led.setMasterBrightness(GLOBAL_BRIGHTNESS)
led.all_off()

precipHours = []
loopCount = 0
connectionInterruptCount = 0
thread = None

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

def onConnectionInterrupt():
  global connectionInterruptCount
  connectionInterruptCount += 1
  print 'Trouble connecting to the internet.  Trying again...'
  startTimer()


def updateWeather():
  
  global loopCount
  global thread
  global API_TIMER
  global precipHours
  global connectionInterruptCount

  connections = conn.check_connection()
  if len(connections) == 0:
    onConnectionInterrupt()
    return
  else:
    connectionInterruptCount = 0

  # call forecast.io API to get weather
  forecast = forecastio.load_forecast(api_key, lat, lng)
  byHour = forecast.hourly()
  
  loopCount += 1
  i = LED_COUNT - 1
  precipHours = []
  print 'Fetched Weather Data ' + str(loopCount) + 'x (' + str(i * API_TIMER) + 's): ' + strftime("%Y-%m-%d %H:%M:%S", gmtime())


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

      print color
      print '----'
      led.fill(color, i, i)    
    i -= 1
    led.update()

  # call function again
  startTimer()

# get weather
updateWeather()

counter = 0
while True:
  counter += 1
  # flash one LED red if there is trouble connecting
  if connectionInterruptCount > CONNECTION_ATTEMPTS:
    strength = math.fabs(math.sin(counter * 0.002))
    led.fillRGB(0, 0, 0)
    led.fill(Color(255, 0, 0, strength), 0, 0)
  else:
    # smooth fade in & out
    for idx, hour in enumerate(precipHours): 
      strength = math.fabs(math.sin((counter + (idx * 50)) * 0.005))
      if hour[0] == 'r':
        precipColor = rain
      elif hour[0] == 's':
        precipColor = snow
      led.fill(Color(precipColor.r, precipColor.g, precipColor.b, strength), hour[1], hour[1])
    led.update()

