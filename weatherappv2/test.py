from geopy.geocoders import GoogleV3

geolocator = GoogleV3()
location = geolocator.geocode("10003")
print(location.address)
print((location.latitude, location.longitude))