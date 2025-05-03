import requests

# Put your CENT Ischool IoT Portal API KEY here.
APIKEY = "01ea68e73260ab354d9c32eb"

def get_google_place_details(google_place_id: str) -> dict:
     url = "https://cent.ischool-iot.net/api/google/places/details"
     header = {'X-API-KEY': APIKEY}
     params = {'place_id': google_place_id}
     response = requests.get(url, headers= header, params= params)
     response.raise_for_status()
     return response.json()
    
def get_azure_sentiment(text: str) -> dict:
     url = "https://cent.ischool-iot.net/api/azure/sentiment"
     header = {'X-API-KEY': APIKEY}
     data = {'text': text}
     response = requests.post(url, headers = header, data = data)
     response.raise_for_status()
     return response.json()

def get_azure_key_phrase_extraction(text: str) -> dict:
     url = "https://cent.ischool-iot.net/api/azure/keyphrasextraction"
     header = {'X-API-KEY': APIKEY}
     data = {'text': text}
     response = requests.post(url, headers = header, data = data)
     response.raise_for_status()
     return response.json()

def get_azure_named_entity_recognition(text: str) -> dict:
     url = "https://cent.ischool-iot.net/api/azure/entityrecognition"
     header = {'X-API-KEY': APIKEY}
     data = {'text': text}
     response = requests.post(url, headers = header, data = data)
     response.raise_for_status()
     return response.json()


def geocode(place:str) -> dict:
    '''
    Given a place name, return the latitude and longitude of the place.
    Written for example_etl.py
    '''
    header = { 'X-API-KEY': APIKEY }
    params = { 'location': place }
    url = "https://cent.ischool-iot.net/api/google/geocode"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary


def get_weather(lat: float, lon: float) -> dict:
    '''
    Given a latitude and longitude, return the current weather at that location.
    written for example_etl.py
    '''
    header = { 'X-API-KEY': APIKEY }
    params = { 'lat': lat, 'lon': lon, 'units': 'imperial' }
    url = "https://cent.ischool-iot.net/api/weather/current"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary