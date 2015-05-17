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
			self.temp=cond_curr['temp_c']
			wugex=re.compile(".+_(c|kph|km|metric|dir|mb)$|weather")
			good_keys=filter(lambda x: wugex.match(x), cond_curr)
			for key in good_keys:
				#Add in regex to edit _ and other stuff
				print("{}: {}".format(key.capitalize(), cond_curr[key]))
				
		else:
			self.temp=cond_curr['temp_f']
			wugex=re.compile(".+_(in|f|mph|mi|dir)$|weather")
			good_keys=filter(lambda x: wugex.match(x), cond_curr)
			for key in good_keys:
				#Add in regex to edit _ and other stuff
				print("{}: {}".format(key.capitalize(), cond_curr[key]))
		
	def history(self, date, fields=None, c_m=False):
		'''	1. 'date' is a required field with year, month and day required.
			2. 'fields' is an optional tuple parameter containing fields to be accessed in the json response.
			3. 'c_m' is a boolean parameter where True returns centigrade temperature values and metric measurements.'''
		d=dateutil.parser.parse(date)
		date="{}{:02d}{:02d}".format(d.year, d.month, d.day)
		hdict={"url": self.base_url, "date": date, "location": self.loc}
		hist=requests.get("{url}/history_{date}/q/{location}.json".format(**hdict)).json()
		self.daycond={date: hist['history']['dailysummary']}
		if c_m:
			for item in self.daycond[date]:
				if not item.endswith("i"):
					print(item.capitalize(), self.daycond[date][item])
		else:
			for item in self.daycond[date]:
				if not item.endswith("m"):
					print(item.capitalize(), self.daycond[date][item])
	
	def custom(self, data_feature):
		features=["alerts", "almanac", "astronomy", "currenthurricane", "forecast", 
					"forecast10day", "geolookup", "hourly", "hourly10day",
					"rawtide", "satellite", "tide", "webcams", "yesterday"] # "planner", 
		my_feature=data_feature.lower()
		if my_feature in features:
			custdict={"url": self.base_url, "location": self.loc, "query": my_feature}
			self.cust=requests.get("{url}/{query}/q/{location}.json".format(**custdict)).json()
			
		else:
			print("Please use query one of the following features: ")
			for f in features: print(f)
			
		##planner needs two dates
		
		
		
