import requests, json

def getTime(origin, destination, api_key):
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+("+".join(origin.split(" ")))+"&destinations="+("+".join(destination.split(" ")))+"&departure_time=now&key="+api_key
	r = requests.get(url)
	if r.status_code == 200:
		return json.loads(r.text)["rows"][0]["elements"][0]["duration_in_traffic"]
	else:
		return -1

def read_input(message, config):
	messageSplit = message.lower().split()
	if messageSplit[1] == "time":
		locations = " ".join(messageSplit[2:]).split(" to ")
		length = getTime(locations[0], locations[1], config["maps"]["api_key"]);
		locString = " ".join(message.split()[2:])
		return locString+": "+length["text"]

if __name__ == "__main__":
	import configparser
	origin = "Chapman University"
	destination = "Hollywood And Highland"
	config=configparser.ConfigParser()
	config.read("config.ini")
	api_key = config["maps"]["api_key"]
	print(getTime(origin, destination,api_key))

	print(read_input("traffic time Chapman University to Hollywood And Highland", config))