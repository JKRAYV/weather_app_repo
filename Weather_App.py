import pandas as pd
import requests
import pgeocode

#--Temporary code--

df = pd.read_csv('us_zip_codes_to_longitude_and_latitude.csv')
town_or_zip = input("Please enter a zipcode: ")

# If the first character is numeric
if town_or_zip[0].isnumeric():
    towndata = df[df['Zip'] == int(town_or_zip)]
else:  # Treat the input as a town name
    towndata = df[df['City'].str.contains(town_or_zip, case=False, na=False)]

latitude = towndata['Latitude'].values[0]
longitude = towndata['Longitude'].values[0]
location_url = f"https://api.weather.gov/points/{latitude},{longitude}"

response = requests.get(location_url)
data = response.json
print(response.text)
if response.status_code == 200:
    data = response.json()
    
    # Make sure data contains the required keys
    if 'properties' in data and 'gridX' in data['properties'] and 'gridY' in data['properties']:
        gridX = data['properties']['gridX']
        gridY = data['properties']['gridY']
        office = data['properties']['cwa']
        
        forecast_url = f"https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast"
    else:
        print("The response JSON does not contain the expected keys.")
else:
    print(f"Request failed with status code: {response.status_code}")

requests.get(forecast_url).json()
#--Temporary code--