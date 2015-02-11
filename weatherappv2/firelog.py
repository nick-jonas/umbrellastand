#! /usr/bin/python


# Example Usage ----------------------------

# from firelog import firelog
# product_name = 'lightbox'
# guid = 'njonas-v1'
# metadata = {
# 	'latitude': 40.7127,
# 	'longitude': -74.0059,
# 	'city': 'New York, NY',
# 	'version': 0.1
# }
# logger = firelog(product_name, guid, metadata)
# logger.log_status('All good!')

# -------------------------------------------

# http://ozgur.github.io/python-firebase/
from firebase import firebase
from time import gmtime, strftime

class firelog:

	HOST = 'https://intense-inferno-8852.firebaseio.com'

	def __init__(self, product, id, metadata = None):
		self.product = product
		self.id = id
		self.metadata = metadata
		self.firebase = firebase.FirebaseApplication(self.HOST, None)
		
	def log_status(self, msg):
		time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		obj = {'message': msg, 'time': time, 'metadata': self.metadata}
		result = self.firebase.post('/status/' + self.product + '/' + self.id, obj)
		return result
		
	def log_error(self, msg):
		time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		obj = {'message': msg, 'time': time, 'metadata': self.metadata}
		result = self.firebase.post('/error/' + self.product + '/' + self.id, obj)
		return result

# Handle Error Messages
# 404 Not Found	A request made over HTTP instead of HTTPS
# 400 Bad Request	Unable to parse PUT or POST data, Missing PUT or POST data, Attempting to PUT or POST data which is too large, A REST API call that contains invalid child names as part of the path
# 417 Expectation Failed	A REST API call that doesn't specify a namespace
# 403 Forbidden	A request that violates Security and Firebase Rules


