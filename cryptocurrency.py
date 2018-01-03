import requests, json

def getPrices():
	r = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0")
	symbols = {}
	names = {}
	if r.status_code == 200:
		data = json.loads(r.text)
		for d in data:
			symbols[d["symbol"].upper()] = d["price_usd"]
			names[d["id"].upper()] = d["price_usd"]
		return symbols,names


def read_input(message,config):
    messageSplit = message.lower().split()
    symbols,names = getPrices()
    if messageSplit[1] == "price":
    	symbol = messageSplit[2].upper()
    	if symbol in symbols:
    		return "$" + str(symbols[symbol])
    	elif symbol in names:
    		return "$" + str(names[symbol])
    	else:
    		return "I don't know that currency."
    if messageSplit[1] == "summary":
    	coins = config["crypto"]["coins"].split(",")
    	symbols,names = getPrices()
    	output = []
    	for coin in coins:
    		c = coin.upper()
    		if c in symbols:
    			output.append(c + ": $" + str(symbols[c]))
    		elif c in names:
    			output.append(c + ": $" + str(names[c]))
    		else:
    			output.append("I don't understand "+c)
    	return "\n".join(output)

if __name__ == "__main__":
	print(read_input("crypto price XRP",""))
	print(read_input("crypto price bitcoin",""))