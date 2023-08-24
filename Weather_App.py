import pandas as pd
import requests
import pgeocode
import folium

#--Temporary code--

def forecast_data(): # returns forecast and city data as json.

    nomi = pgeocode.Nominatim('us')

    town_or_zip = input("Please enter a City(e.g. City, State Initial) or Zipcode: ")

    # If the first character is numeric
    if town_or_zip[0].isnumeric():
        towndata = nomi.query_postal_code(town_or_zip)
    else:  
        # Split input into town and state initial using comma as separator
        town, state_initial = town_or_zip.split(',')
        # Only strip spaces from the state_initial
        state_initial = state_initial.strip()

        # Search for both town and state in the dataframe
        towndata = nomi.query_location(town)
        towndata = towndata[towndata['state_code'] == state_initial.upper()].squeeze()
        print(towndata.shape)
        # If there are multiple zip codes for the city
        if towndata.shape[0] > 12:
            print("Multiple zip codes found for the city. Please select one:")
            num = 0
            for index, row in towndata.iterrows():
                num += 1
                print(f"{num}: {row['postal_code']}")

            # Ask the user to specify the zip code
            selection = int(input("Enter the number corresponding to your desired zip code: "))
            towndata = towndata.iloc[selection - 1]

    print(towndata)

    latitude = towndata['latitude']
    longitude = towndata['longitude']
    location_url = f"https://api.weather.gov/points/{latitude},{longitude}"

    response = requests.get(location_url)
    data = response.json

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
    return forecast_data, data, towndata

def forecast(forecast_data, towndata): #Returns forcast, requires forecast_data, and city data.

        # Ensure the forecast_data contains the expected 'properties' and 'periods' keys
    if 'properties' in forecast_data and 'periods' in forecast_data['properties']:
        forecast_periods = forecast_data['properties']['periods']
        city = towndata['place_name']
        state = towndata['state_name']
        
        # Loop through the forecast periods and print out the first 20 periods (10 days, assuming 2 periods per day)
        print("-----------------------------------------------" *2 + \
              f"\nForecast for {city}, {state}:\n" + \
              "-----------------------------------------------" *2)
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

def create_weather_map(forecast_data, towndata):
    # Extract the latitude and longitude of the city
    latitude = towndata['latitude']
    longitude = towndata['longitude']
    
    # Create a map centered around the city
    m = folium.Map(location=[latitude, longitude], zoom_start=12)

    # Extract forecast details for tooltip
    first_forecast = forecast_data['properties']['periods'][0]
    detailed_forecast = first_forecast['detailedForecast']
    temperature = first_forecast['temperature']
    temperature_unit = first_forecast['temperatureUnit']

    tooltip_content = f"Temperature: {temperature} {temperature_unit}<br>{detailed_forecast}"

    # Add a marker for the city
    folium.Marker(
        [latitude, longitude],
        tooltip=tooltip_content
    ).add_to(m)

    # Save map to an HTML file or display inline in a Jupyter notebook
    m.save('weather_map.html')

forecastdata, data, towndata = forecast_data()
create_weather_map(forecastdata, towndata)


forecastdata, data, towndata = forecast_data()
forecast(forecastdata, towndata)
#--Temporary code--