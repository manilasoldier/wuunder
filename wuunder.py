'''A Weather Underground API wrapper'''
import requests, dateutil.parser, json, re, os, pickle
#4/2/15: Need to add functionality for automatically getting location

class Wunderground:
	def __init__(self, api_key, auto_ip=False):
		self.base_url="{}/{}/".format("http://api.wunderground.com/api", api_key)
		with open(os.path.join(os.path.dirname(__file__), "abbrevs.pickle"), 'rb') as f:
			self.state_abbrevs = pickle.load(f) 
		if auto_ip:
			self.loc="autoip"
	'''
	from wunderground import Wunderground
	###Figure out how location will work...
	wu=Wunderground("<INSERT_API_KEY>")
	wu.history('2014-01-23')['history']['dailysummary'][0]['maxtempi']
	Fahrenheit maximum temperature
	wu.history('2014-01-23')['history']['dailysummary'][0]['mintempi']
	Fahrenheit minimum temperature
	'''
	
	def coord(self, lat, lon):
		self.loc="{},{}".format(lat, lon)
	
	def us_loc(self, city, us_state):
		try:
			us_state=self.state_abbrevs[us_state]
		except KeyError:
			us_state=us_state
		locs=tuple(map(lambda s: s.replace(" ", "_"), [us_state, city]))
		self.loc="{}/{}".format(*locs)
	
	def station(self, personal_weather_station):
		self.loc="pws:{}".format(personal_weather_station)
		
	def country(self, city, country):
		locs=tuple(map(lambda s: s.replace(" ", "_"), [country, city]))
		self.loc="{}/{}".format(*locs)
	
	def conditions(self, fields=None, c_m=False):
		'''	1. 'fields' is an optional tuple parameter containing fields to be accessed in the json response
			2. 'nosj' is a boolean paraemter where True represents returning json values, defaults to False
			3. 'c_m' returns centigrade temperature values and metric measurements'''
		cdict={"url": self.base_url, "location": self.loc}
		self.cond=requests.get("{url}/conditions/q/{location}.json".format(**cdict)).json()
		cond_curr=self.cond['current_observation']
		if c_m:
			self.tnow=cond_curr['temp_c']
			wugex=re.compile(".+_(c|kph|km|metric|dir|mb)$|weather")
			good_keys=filter(lambda x: wugex.match(x), cond_curr)
			for key in good_keys:
				print("{}: {}".format(key.capitalize(), cond_curr[key]))
				
		else:
			self.tnow=cond_curr['temp_f']
			wugex=re.compile(".+_(in|f|mph|mi|dir)$|weather")
			good_keys=filter(lambda x: wugex.match(x), cond_curr)
			for key in good_keys:
				print("{}: {}".format(key.capitalize(), cond_curr[key]))
		
	def history(self, date, fields=None, c_m=False):
		'''	1. 'data' is a required field with year, month and day required.
			2. 'fields' is an optional tuple parameter containing fields to be accessed in the json response.
			3. 'nosj' is a boolean parameter where True represents returning json values, defaults to False.
			4. 'c_m' is a boolean parameter where True returns centigrade temperature values and metric measurements.'''
		d=dateutil.parser.parse(date)
		date="{}{:02d}{:02d}".format(d.year, d.month, d.day)
		hdict={"url": self.base_url, "date": date, "location": self.loc}
		self.hist=requests.get("{url}/history_{date}/q/{location}.json".format(**hdict)).json()
		if c_m:
			pass
			
		else:
			pass
	
	def custom(self, data_feature):
		pass
