import logging
import os

import requests
from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
# TODO: extract DB and model into own module?
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<City %r>' % self.name


if 'OPEN_WEATHER_API_KEY' not in os.environ:
    raise EnvironmentError("OPEN_WEATHER_API_KEY not set")

OPEN_WEATHER_API_KEY = os.environ['OPEN_WEATHER_API_KEY']


def convert_to_celsius(temp):
    celsius = (float(temp) - 32) * (5 / 9)
    return "{:0.0f}".format(celsius)


def get_current_weather(city):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid={}'
    r = requests.get(url.format(city, OPEN_WEATHER_API_KEY))
    r.raise_for_status()
    data = r.json()
    temp_in_celsius = convert_to_celsius(data['main']['temp'])
    feels_like_in_celsius = convert_to_celsius(data['main']['feels_like'])
    weather = {
        'city': city,
        'temp': temp_in_celsius,
        'main': data['weather'][0]['main'],
        'icon': data['weather'][0]['icon'],
        'feels_like': feels_like_in_celsius,
        'humidity': data['main']['humidity'],
        'wind_speed': "{:0.0f}".format(data['wind']['speed']),
    }
    return weather


def city_exists(city_name):
    cities = City.query.all()
    for city in cities:
        if city.name == city_name:
            return True
    return False


# TODO: convert to route
def add_city(name):
    city = City(name=name)
    try:
        db.session.add(city)
        db.session.commit()
    except Exception as e:
        msg = 'Unable to save city to database'
        logging.error(msg, e)
        flash(message=msg, category='error')


# TODO: extract routes into own module?
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_city = request.form['city']
        if new_city:
            if city_exists(new_city):
                flash(message=f'{new_city} already exists!', category='error')
            else:
                add_city(new_city)

    # TODO: extract into own 'get_weather_data' function
    weather_data = []
    cities = City.query.all()
    for city in cities:
        city_weather = get_current_weather(city.name)
        weather_data.append(city_weather)

    return render_template('index.html', weather_data=weather_data)


@app.route('/delete/<city_name>', methods=['GET'])
def delete(city_name):
    try:
        city_obj = City.query.filter_by(name=city_name).first()
        db.session.delete(city_obj)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        msg = 'Failed to delete city from database'
        logging.error(msg, e)
        flash(message=msg, category='error')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
