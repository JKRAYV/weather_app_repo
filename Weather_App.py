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
        user = mongo.db.users.find_one({"username": username})

        if user and user["password"] == password:
            session['username'] = username
            return redirect("/home")
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
            "favorites": [],
            "home": ""
        }
        existing_user = mongo.db.users.find_one({"username": user_data["username"]})
        existing_email = mongo.db.users.find_one({"email": user_data["email"]})

        if existing_user:
            return render_template("register.html", error="Username already taken.")
        
        if existing_email:
            return render_template("register.html", error="Email already in use.")
        mongo.db.Users.insert_one(user_data)

        session['username'] = user_data["username"]
        return redirect("/home")
    return render_template("register.html")

@app.route('/home', methods=["GET","POST","PUT"])
def home():
    if 'username' not in session:
        return redirect("/")
    logged_in_username = session['username']
    user_data = mongo.db.users.find_one({"username": logged_in_username})
    home_forecast = {"error": "Home ZIP code not set."} if 'home' not in user_data else forecast(*forecast_data(user_data['home']['zip']))
    
    if request.method == "POST":
        
        town_or_zip = request.form.get("town_or_zip")

        if validate_location(user_data['home']['zip']) == True:
            weather_data, towndata = forecast_data(town_or_zip)

            if weather_data and towndata is not None:
                return render_template("userpage.html", user_data=user_data, weather_data=weather_data, towndata=towndata.to_dict())
            else:
                return render_template("userpage.html", user_data=user_data, error="Could not fetch weather data.")
    
    return render_template("userpage.html", user_data=user_data, home_forecast=home_forecast)

@app.route('/modify_favorites', methods=["POST"])
def modify_favorites():
    if 'username' not in session:
        return redirect("/"), 401
    
    username = session['username']
    user_data = mongo.db.users.find_one({"username": username})

    # Check if the user exists in the database
    if not user_data:
        return redirect("/"), 404

    # Retrieve data from client form
    action = request.form.get("action")
    zip_data = request.form.get("zip_data")

    if action == "add":
        # Use pgeocode to get additional information
        nomi = pgeocode.Nominatim('us')
        town_or_zip = nomi.query_postal_code(zip_data)
        raw_data, towndata = forecast_data(town_or_zip)
        display_data = forecast(raw_data, towndata)
        print(towndata)
        if display_data is not None:
            if towndata.get('place_name') is not None and towndata.get('place_name').strip() != '' and towndata.get('state_code') is not None and towndata.get('state_code').strip() != '' and towndata.get('place_name') != 'NaN' and towndata.get('state_code') != 'NaN' and zip_data.isnumeric():
                new_favorite = {
                    "zip": zip_data,
                    "town": f"{towndata['place_name']}, {towndata['state_code']}"
                }
                mongo.db.users.update_one({"username": username}, {"$addToSet": {"favorites": new_favorite}})
    elif action == "remove":
        # Remove from favorites
        favorite_to_remove = {"zip": zip_data}
        mongo.db.users.update_one({"username": username}, {"$pull": {"favorites": favorite_to_remove}})
    else:
        return redirect("/home"), 400

    return redirect("/home")

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect("/")
    
    username = session['username']
    user_data = mongo.db.users.find_one({"username": username})
    avatar = os.listdir('static/profileimages')

    if request.method == 'POST':
        if 'delete' in request.form:
            mongo.db.users.delete_one({"username": username})
            session.pop('username', None)
            return redirect("/")
        
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        new_home = request.form.get("home")
        new_avatar = request.form.get("avatar")
        try:
            if new_username == username or new_username != mongo.db.users.find_one({"username": new_username})['username']:
                new_username == new_username
            else:
                return render_template("options.html", user_data=user_data, avatar=avatar, name_error = "Invalid username")
        except:
            new_username = new_username
        
        if new_password == user_data['password'] or new_password != '':
            new_password == new_password
        else:
            return render_template("options.html", user_data=user_data, avatar=avatar, password_error = "Invalid Password")
        
        if validate_location(new_home):
            weatherdata, towndata = forecast_data(new_home)
            display_data = forecast(weatherdata, towndata)

            if display_data is not None:
                new_home_zip = towndata['postal_code']
                new_home_name = towndata['place_name']
                new_home_state = towndata['state_code']
                structured_home = {"zip": new_home_zip,
                                   "town": f"{new_home_name}, {new_home_state}"
                                   }
            else:
                return render_template("options.html", user_data=user_data, avatar=avatar, home_error = "Invalid Zipcode")
        else:
                return render_template("options.html", user_data=user_data, avatar=avatar, home_error = "Invalid Town")

        if new_avatar != new_avatar:
            return render_template("options.html", user_data=user_data, avatar=avatar, avatar_error = "Please chose an avatar")

        mongo.db.users.update_one({"username": username}, {"$set": {"username": new_username, "home": structured_home, "profile_image": new_avatar}})
        session['username'] = new_username
        return redirect("/home")

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

#--Temporary code--

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

        print(towndata.shape)

        # If there are multiple zip codes for the city
        if towndata.shape[0] >= 1:
            towndata = towndata.iloc[0]
        elif towndata.shape[0] < 1:
            print("Invalid City String.")
            return None, None
#---------------------------------------------------------------------------------------------
    
    print(towndata)

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
#--Temporary code--

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)