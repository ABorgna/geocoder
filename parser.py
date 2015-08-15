""" Parses and geocodes a specific csv file """

import json
import csv
import time
import urllib.request
import urllib.parse

GOOGLE_API_KEY = "AIzaSyCxbKjzCtKgEx4JKXl7DNdWpXprXTc4AAY"
IN_CSV = "data.csv"
OUT_JSON = "data.json"

JSON_COLUMNS = ["listado","CODEM","socio","name","provincia","zona",
                "localidad","direccion","direccion2","codigo postal",
                "telefono","especialidad","email","encuestador"]

def main():
    # Get the data
    data = getCsv(IN_CSV)

    # Geocode all the points
    for row in data:
        row['address'] = ", ".join([ row[s].strip() for s in ["direccion","localidad","provincia"]]) \
                       + ", Argentina"

        # The google api has a limit of 5 request per second
        time.sleep(0.22)

        (lat,lng) = geocode(row["address"])
        if lat is not None:
            row['lat'] = lat
            row['lng'] = lng

    # Write the json
    writeJson(data,OUT_JSON)

# Parse the CSV data
def getCsv(filename):
    result = [];
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, JSON_COLUMNS)
        for row in reader:
            result.append(row)
    return result

# Google geocoding
def geocode(address):
    baseUrl = "https://maps.googleapis.com/maps/api/geocode/json?"
    params = []

    params.append(("key",GOOGLE_API_KEY))
    params.append(("region","ar"))
    params.append(("address",address))

    result = getJson(baseUrl + urllib.parse.urlencode(params))

    status = result['status']
    error = ". Error:"+result["error_message"] if "error_message" in result else ""
    location = (None,None)
    if(status == "ZERO_RESULTS"):
        print("No results for "+address + error)
    elif(status == "OVER_QUERY_LIMIT"):
        print("Query limit reached while processing "+address + error)
    elif(status == "REQUEST_DENIED"):
        print("The request was denied for "+address + error)
    elif(status == "INVALID_REQUEST"):
        print("The request was invalid for "+address + error)
    elif(status == "UNKNOWN_ERROR"):
        print("Got an unknown error for "+address + error)
    elif(status == "OK"):
        print("Got a location for "+address)
        loc = result["results"][0]["geometry"]["location"]
        location = (loc["lat"],loc["lng"])

    return location

# Write data to a json file
def writeJson(data,filename):
    with open(filename,'w') as outfile:
        json.dump(data,outfile)

# Utils

def getJson(url):
    resp = urllib.request.urlopen(url)
    return json.loads(resp.read().decode("utf-8"))

if __name__ == "__main__":
        main()
