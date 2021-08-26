# Weather App

A simple Python Flask app that allows you to view weather conditions in any city.

The application uses the [Open Weather Map API](https://openweathermap.org/api) to pull current weather information for the cities stored in the database, and renders the information on cards displayed on the page.

## Running the application

```
pipenv install
export OPEN_WEATHER_API_KEY=<API KEY>
pipenv run weather_app/init_db.py
FLASK_APP=weather_app/app.py pipenv run flask run
```

The application will be accessible at http://localhost:5000
