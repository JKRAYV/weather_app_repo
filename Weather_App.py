from flask import Flask, jsonify, request, render_template, redirect, session
from flask_pymongo import PyMongo
import os
import re
import pandas as pd
import requests
import pgeocode
import folium
import math

app = Flask(__name__)

try:
    app = Flask(__name__)
    app.config["MONGO_URI"] = "mongodb://localhost:27017/mock_Weather"
    mongo = PyMongo(app)
except:
        print("ERROR- cannot connect to db")

@app.route('/', methods=["GET", "POST"])
def login():
    app.secret_key = os.urandom(24)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Make a POST request to the Java Spring Boot backend
        response = requests.post('http://localhost:8080/api/user/auth', json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            user_data = response.json()
            session['username'] = username
            session['user_data'] = user_data
            return redirect("/home")
        elif response.status_code == 404:
            return render_template("login.html", error="User not found")
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_data = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }

        # Check for existing user by making a GET request to the Java backend
        response = requests.get(f'http://localhost:8080/api/user/{user_data["username"]}')
        
        if response.status_code == 200:
            return render_template("register.html", error="Username already taken.")
        
        # Create new user by making a POST request to the Java backend
        response = requests.post('http://localhost:8080/api/user', json=user_data)
        
        if response.status_code == 201:
            session['username'] = request.form.get("username")
            return redirect("/home")
        else:
            return render_template("register.html", error="Could not register user. Try again.")
    return render_template("register.html")

@app.route('/home', methods=["GET","POST","PUT"])
def home():
    if 'username' not in session:
        return redirect("/")
    
    # Fetch the user data directly from the Java backend
    response = requests.get(f'http://localhost:8080/api/user/name/{session["username"]}')
    if response.status_code != 200:
        return redirect("/"), 401
    user_data = response.json()

    # Existing logic for weather data
    home_forecast = {"error": "Home ZIP code not set."} if 'home' not in user_data else forecast(*forecast_data(user_data['home']['zip']))

    if request.method == "POST":
        towndata = request.form.get("town_or_zip")

        if validate_location(towndata):
            weather_data, _ = forecast_data(towndata)

            if weather_data is not None:
                update_response = requests.patch(f'http://localhost:8080/api/user/{session["username"]}', json={
                    'home': {'zip': towndata}
                })
                
                if update_response.status_code == 200:
                    updated_user_data = update_response.json()
                    session['user_data'] = updated_user_data
                    return render_template("userpage.html", user_data=updated_user_data, weather_data=weather_data, towndata=towndata)
                else:
                    return render_template("userpage.html", user_data=user_data, weather_data=weather_data, error="Could not update home location.")
            else:
                return render_template("userpage.html", user_data=user_data, error="Could not fetch weather data.")

    return render_template("userpage.html", user_data=user_data, home_forecast=home_forecast)

@app.route('/modify_favorites', methods=["POST"])
def modify_favorites():
    if 'username' not in session:
        return redirect("/"), 401
    
    username = session['username']

    action = request.form.get("action")
    zip_data = request.form.get("zip_data")

    if action == "add":
        raw_data, towndata = forecast_data(str(zip_data))
        display_data = forecast(raw_data, towndata)
        
        if display_data is not None:
            new_favorite = {
                "zip": int(zip_data),
                "town": f"{towndata.get('place_name')}, {towndata.get('state_code')}"
            }
            
            update_response = requests.post(f'http://localhost:8080/api/user/location/{username}', json=new_favorite)
            
            if update_response.status_code != 200:
                return redirect("/home"), 400

    elif action == "remove":
        update_response = requests.delete(f'http://localhost:8080/api/user/{username}/{zip_data}')
        
        if update_response.status_code != 200:
            return redirect("/home"), 400

    else:
        return redirect("/home"), 400

    # Re-fetch the updated user data from the Java backend
    response = requests.get(f'http://localhost:8080/api/user/{username}')
    if response.status_code == 200:
        updated_user_data = response.json()
        session['user_data'] = updated_user_data  # Store the updated user data in the session

    return redirect("/home")

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect("/")
    
    username = session['username']
    user_data = session.get('user_data')
    avatar = os.listdir('static/profileimages')

    if request.method == 'POST':
        action = request.form.get("action")

        if action == "delete":
            # Delete user by making a DELETE request to the Java backend
            delete_response = requests.delete(f'http://localhost:8080/api/user/{username}')
            if delete_response.status_code == 200:
                session.pop('username', None)
                session.pop('user_data', None)
                return redirect("/")
            else:
                return render_template("options.html", user_data=user_data, avatar=avatar, error="Could not delete user.")
        
        elif action == "update profile":
            # Logic for updating all profile details except username
            new_home = request.form.get("home")
            if validate_location(new_home):
                weather_data, towndata = forecast_data(new_home)
                display_data = forecast(weather_data, towndata)

                if display_data is not None:
                    structured_home = {
                        "zip": towndata['postal_code'],
                        "town": f"{towndata['place_name']}, {towndata['state_code']}"
                    }
                    
                    updated_user_data = {
                        "password": request.form.get("password"),
                        "home": structured_home,
                        "profile_image": request.form.get("avatar")
                    }

                    update_response = requests.patch(f'http://localhost:8080/api/user/{username}', json=updated_user_data)
                    
                    if update_response.status_code == 200:
                        updated_user_data = update_response.json()
                        session['user_data'] = updated_user_data
                        return redirect("/home")
                    else:
                        return render_template("options.html", user_data=user_data, avatar=avatar, error="Could not update user.")
                else:
                    return render_template("options.html", user_data=user_data, avatar=avatar, home_error="Could not fetch weather data for new home.")
            else:
                return render_template("options.html", user_data=user_data, avatar=avatar, home_error="Invalid new home location.")
        
        elif action  == "update username":
            # Logic for updating only the username
            new_username = request.form.get("new_username")
            update_response = requests.patch(f'http://localhost:8080/api/user/{username}', json={"username": new_username})
            
            if update_response.status_code == 200:
                updated_user_data = update_response.json()
                session['user_data'] = updated_user_data
                session['username'] = new_username  # update the username in the session
                return redirect("/home")
            else:
                return render_template("options.html", user_data=user_data, avatar=avatar, name_error="Username already exists or could not be updated.")

        elif action == "logout":
            session['username'] = None
            return redirect("/")

    return render_template("options.html", user_data=user_data, avatar=avatar)


@app.route('/town', methods=['GET'])
def town():
    searched_town = request.args.get('searched_town', None)
    if validate_location(searched_town):
        raw_data, towndata = forecast_data(searched_town)
        display_data = forecast(raw_data, towndata)

        if display_data and towndata is not None:
            return render_template("town.html", display_data=display_data, towndata=towndata.to_dict())
        return render_template("town.html", display_data=display_data, towndata=towndata.to_dict(), error="Likely an invalid zip code.")
    
    return render_template("town.html", display_data="Nothing to display.", towndata="Nothing to display.", error="Invalid town or zip.")


def validate_location(town_or_zip):
    nomi = pgeocode.Nominatim('us')

    if town_or_zip[0].isnumeric():
        towndata = nomi.query_postal_code(town_or_zip)
        if towndata.shape[0] >= 1:
            return True
        else:
            return False
    else:
        if "," not in town_or_zip:
            return False

        town, state_initial = town_or_zip.split(',')
        state_initial = state_initial.strip()

        towndata = nomi.query_location(town)
        towndata = towndata[towndata['state_code'] == state_initial.upper()]

        if towndata.shape[0] >= 1:
            return True
        else:
            return False

def forecast_data(town_or_zip): # returns forecast and city data as json.

    nomi = pgeocode.Nominatim('us')

    town_or_zip = str(town_or_zip)

    # If the first character is numeric
    if town_or_zip[0].isnumeric():
        towndata = nomi.query_postal_code(town_or_zip)
    else:  
        if("," not in town_or_zip):
            print("Invalid City String.")
            return None, None
        
        # Split input into town and state initial using comma as separator
        town, state_initial = town_or_zip.split(',')
        # Only strip spaces from the state_initial
        state_initial = state_initial.strip()

        # Search for both town and state in the dataframe
        towndata = nomi.query_location(town)
        towndata = towndata[towndata['state_code'] == state_initial.upper()]

        # If there's only one row, convert to DataFrame for consistency
        if isinstance(towndata, pd.Series):
            towndata = pd.DataFrame([towndata])

        # If there are multiple zip codes for the city
        if towndata.shape[0] >= 1:
            towndata = towndata.iloc[0]
        elif towndata.shape[0] < 1:
            return None, None

    if(not (towndata["place_name"] != towndata["place_name"])):
        
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
            
                forecast_data = f"https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast"
            else:
                print("The response JSON does not contain the expected keys.")
                forecast_data, data = None, None
        else:
            print(f"Request failed with status code: {response.status_code}")
            forecast_data, data = None, None
    else:
        print(f"Invalid City, State Initial, or Zipcode.")
        forecast_data, data = None, None

    if(forecast_data != None and data != None):
        forecast_data = requests.get(forecast_data).json()
    return forecast_data, towndata

def forecast(forecast_data, towndata):
    # Initialize an empty dictionary to hold the processed forecast
    processed_forecast = {}
    
    # Check if forecast_data contains the expected keys
    if forecast_data and 'properties' in forecast_data and 'periods' in forecast_data['properties']:
        forecast_periods = forecast_data['properties']['periods']
        
        # Add city and state information to the processed forecast
        processed_forecast['city'] = towndata['place_name']
        processed_forecast['state'] = towndata['state_name']
        
        # Process the first 14 periods (7 days, assuming 2 periods per day)
        processed_forecast['forecast'] = forecast_periods[:14]
        
        return processed_forecast
    else:
        return None

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)