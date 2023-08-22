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

forecast_data = requests.get(forecast_url).json()

def forecast(forecast_data):
        # Ensure the forecast_data contains the expected 'properties' and 'periods' keys
    if 'properties' in forecast_data and 'periods' in forecast_data['properties']:
        forecast_periods = forecast_data['properties']['periods']
        
        # Loop through the forecast periods and print out the first 20 periods (10 days, assuming 2 periods per day)
        for period in forecast_periods[:14]:
            name = period['name']
            detailed_forecast = period['detailedForecast']
            temperature = period['temperature']
            temperature_unit = period['temperatureUnit']
            wind_speed = period['windSpeed']
            wind_direction = period['windDirection']
            
            print(f"{name}:")
            print(f"Temperature: {temperature} {temperature_unit}")
            print(f"Wind: {wind_speed} {wind_direction}")
            print(f"Forecast: {detailed_forecast}")
            print("-----------------------------------------------")  # Separator for clarity
    else:
        print("Forecast data doesn't contain the expected structure.")

forecast(forecast_data)
#--Temporary code--