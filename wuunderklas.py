'''Class-based support for certain Weather Underground Data Features'''
import requests, json, os, re, pprint, pickle
from datetime import date

#Add zip and airport code functionality

class Location:
	def ll(self, lat, lon):
		'''Sets location via latitude and longitude'''
		self.loc="{},{}".format(lat, lon)
		
	def cc(self, city, country):
		'''Sets locaton via city and country'''
		locs=tuple(map(lambda s: s.replace(" ", "_"), [country, city]))
		self.loc="{}/{}".format(*locs)
		
	def us(self, city, us_state):
		'''Sets location via city and US state'''
		try:
			us_state=self.state_abbrevs[us_state]
		except KeyError:
			us_state=us_state
		locs=tuple(map(lambda s: s.replace(" ", "_"), [us_state, city]))
		self.loc="{}/{}".format(*locs)

class Almanac(Location):
	def __init__(self, api_key, auto_ip=True):
		self.base_url="{}/{}/".format("http://api.wunderground.com/api", api_key)
		with open(os.path.join(os.path.dirname(__file__), "abbrevs.pickle"), 'rb') as f:
			self.state_abbrevs = pickle.load(f) 
		
		if not auto_ip:
			self.loc=None
		else:
			'''Sets location via your ip address'''
			self.loc="autoip"
		
		self.almanac=None
	
	def __repr__(self):
		if not self.loc:
			return "Please provide a location, or set location to \"autoip\""
		else:
			if not self.almanac: 
				return "Please retrieve almanac via the self.get() method"
			else:
				return pprint.pformat(self.almanac)
			
	def __str__(self):
		if not self.loc:
			return "Please provide a location, or set location to \"autoip\""
		else:
			if not self.almanac: 
				return "Please retrieve almanac via the self.get() method"
			else:
				code=self.almanac["almanac"]["airport_code"]
				placedict={"url": self.base_url, "location": code, "condition": "geolookup"}
				place_info=requests.get("{url}/{condition}/q/{location}.json".format(**placedict)).json()
				city=place_info["location"]["city"]
				state, country=place_info["location"]["state"], place_info["location"]["country_name"]
				if not state:
					place=country
				else:
					place=state
				high, low=self.almanac["almanac"]["temp_high"], self.almanac["almanac"]["temp_low"]
				printdict={"date": date.today().strftime("%B %d"), "degree": u"\u00B0",
						   "highyear": high["recordyear"], "nhf": high["normal"]["F"],
						   "nhc": high["normal"]["C"], "rhf": high["record"]["F"],
						   "rhc": high["record"]["C"], "lowyear": low["recordyear"],
						   "nlf": low["normal"]["F"], "nlc": low["normal"]["C"],
						   "rlf": low["record"]["F"], "rlc": low["record"]["C"],
						   "city": city+" Airport", "place": place}
				return ("Almanac for {date} at {city}, {place}\nAverage High: {nhf:>3}{degree}F, {nhc:>3}{degree}C\n"
					"Record High: {rhf:>4}{degree}F, {rhc:>3}{degree}C ({highyear})\n\n"
					"Average Low: {nlf:>4}{degree}F, {nlc:>3}{degree}C\nRecord Low: {rlf:>5}{degree}F, "
					"{rlc:>3}{degree}C ({lowyear})".format(**printdict))
			
	def get(self):
		if not self.loc:
			print("Please provide a location, or set location to \"autoip\"")
		else:
			almadict={"url": self.base_url, "location": self.loc, "condition": "almanac"}
			self.almanac=requests.get("{url}/{condition}/q/{location}.json".format(**almadict)).json()
			
			#Make sure to add in step for dealing with city not found
			
			#Add in custom error class for such a situation?
				
		