"""
This python script is main script.
"""
from typing import Type

from flask import Flask, render_template, request
from Openweathermap.weather import main as get_weather, Location, CurrentWeatherData, Formats
from utils.get_class_name import get_full_class_name

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    """

    :return:     render_template
    """
    location_data: Type[Location] | None = None
    current_weather_data: Type[CurrentWeatherData] | None = None
    formats_data: Type[Formats] | None = None
    try:
        if request.method == 'POST':
            print(request.form)
            city = request.form['cityName']
            state = request.form['stateName']
            country = request.form['countryName']
            location_data, current_weather_data, formats_data = get_weather(city, state, country)
    except (IndexError, ValueError, TypeError, KeyError) as e:
        print(f"{get_full_class_name(e)}: {e.args}")
    return render_template("home.html",
                           location_data=location_data,
                           current_weather_data=current_weather_data,
                           formats_data=formats_data)


if __name__ == '__main__':
    app.run(debug=True)
