"""
This python script gets the current weather from the openweather API.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Type
from urllib.error import HTTPError
import os
import requests
from dotenv import load_dotenv

from requests import Response

from utils.get_class_name import get_full_class_name
from utils.property_conversions import visibility_in_km

# Get configuration information
load_dotenv()
api_key: str | None = os.getenv("API_KEY")
owm_geo_url: str | None = os.getenv("OWM_GEO_URL")
owm_cur_weather_url: str | None = os.getenv("OWM_CUR_WEATHER_URL")
language: str | None = os.getenv("LANGUAGE")
units_of_measure: str | None = os.getenv("UNITS_OF_MEASURE")


@dataclass
class Location:
    """Class representing a location"""
    city: str | None = None
    state: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    code: int = 0
    message: str | None = None


# pylint: disable=too-many-instance-attributes
# Sixteen is reasonable in this case.
@dataclass
class CurrentWeatherData:
    """Class representing the current weather data"""
    cloud_main: str | None = None
    cloud_description: str | None = None
    cloud_icon: str | None = None
    temperature: float = -999999.0
    feels_like: float = -999999.0
    minimum: float = -999999.0
    maximum: float = -999999.0
    pressure: float = -999999.0
    pressure_ground_level: float = -999999.0
    humidity: float = -999999.0
    visibility: float = -999999.0
    wind_speed: float = -999999.0
    wind_direction: int = -999999
    wind_gust: float = -999999.0
    sunrise: datetime = datetime.fromtimestamp(18000)  # Set to 01/01/1970
    sunset: datetime = datetime.fromtimestamp(18000)  # Set to 01/01/1970
    code: int = 0
    message: str | None = None


@dataclass
class Formats:
    """Class representing the current weather formats"""
    if units_of_measure == "metric":
        temperature_format: str | None = os.getenv("METRIC_TEMPERATURE")
    elif units_of_measure == "imperial":
        temperature_format: str | None = os.getenv("IMPERIAL_TEMPERATURE")
    else:
        temperature_format: str | None = os.getenv("STANDARD_TEMPERATURE")
    pressure_format: str | None = os.getenv("PRESSURE")
    humidity_format: str | None = os.getenv("HUMIDITY")
    if units_of_measure == "imperial":
        wind_speed_format: str | None = os.getenv("IMPERIAL_WIND_SPEED")
    else:
        wind_speed_format: str | None = os.getenv("STANDARD_WIND_SPEED")
    wind_direction_format: str | None = os.getenv("WIND_DIRECTION")
    visibility_format: str | None = os.getenv("VISIBILITY")


# help(CurrentWeatherData)

# def postgres_close(p_connection: Connection) -> None:
def get_lan_lon(city_name: str, state_code: str, country_code: str, limit: int = 1) -> Location:
    """
    :param city_name:      The city name to get the latitude and longitude from.
    :param state_code:     The state code to get the latitude and longitude from.
    :param country_code:   The country code to get the latitude and longitude from.
    :param limit:          The number of latitude and longitude combinations to retrieve.

    :return:               Location dataclass representing the location.
    """
    try:
        resp: Response = requests.get(
            f"{owm_geo_url}{city_name},{state_code},{country_code}&limit={limit}&appid={api_key}",
            timeout=5)
        print(f"get_lan_lon response: {resp.status_code}")
        print(resp.json())
        print(type(resp.json()))
        if resp.status_code == 200 and resp.json():
            if resp.json()[0].get("state") is not None:
                state = resp.json()[0].get("state")
            else:
                state = None
            data = Location(
                city=resp.json()[0].get("name"),    #.get("local_names").get("en"),
                state=state,
                country=resp.json()[0].get("country"),
                latitude=resp.json()[0].get("lat"),
                longitude=resp.json()[0].get("lon"),
                code=resp.json()[0].get("cod"),
                message=None
            )
        else:
            data = Location(
                city=None,
                state=None,
                country=None,
                latitude=None,
                longitude=None,
                code=resp.json()[0].get("cod") if resp.json() else -1,
                message=resp.json()[0].get("message") if resp.json() else None
            )
    except HTTPError as e:
        print(f"{get_full_class_name(e)}: {e.read().decode()}")
        data = Location(
            city=None,
            state=None,
            country=None,
            latitude=None,
            longitude=None,
            code=-1,
            message=None
        )
    except (IndexError, ValueError, TypeError, AttributeError) as e:
        print(f"{get_full_class_name(e)}: {e.args}")
        # data = None
        data = Location(
            city=None,
            state=None,
            country=None,
            latitude=None,
            longitude=None,
            code=-1,
            message=None
        )

    return data


def get_current_weather(lat: float, lon: float) -> CurrentWeatherData:
    """
    :param lat:      The latitude to get the current weather from.
    :param lon:      The longitude to get the current weather from.

    :return:         CurrentWeatherData dataclass representing the current weather.
    """
    try:
        resp: Response = requests.get(
            f"{owm_cur_weather_url}{lat}&lon={lon}&lang={language}&appid={api_key}"
            f"&units={units_of_measure}", timeout=5)
        print(f"get_current_weather response: {resp.status_code}")
        print(resp.json())
        print(type(resp.json()))
        if resp.status_code == 200:
            data = CurrentWeatherData(
                cloud_main=resp.json().get("weather")[0].get("main"),
                cloud_description=resp.json().get("weather")[0].get("description"),
                cloud_icon=resp.json().get("weather")[0].get("icon"),
                temperature=resp.json().get("main").get("temp"),
                feels_like=resp.json().get("main").get("feels_like"),
                minimum=resp.json().get("main").get("temp_min"),
                maximum=resp.json().get("main").get("temp_max"),
                pressure=resp.json().get("main").get("pressure"),  #
                pressure_ground_level=resp.json().get("main").get("grnd_level"),
                humidity=resp.json().get("main").get("humidity"),
                visibility=visibility_in_km(resp.json().get("visibility")),
                wind_speed=resp.json().get("wind").get("speed"),
                wind_direction=resp.json().get("wind").get("deg"),
                wind_gust=resp.json().get("wind").get("gust")
                if resp.json().get("wind").get("gust") is not None else -999999.0,
                sunrise=datetime.fromtimestamp(resp.json().get("sys").get("sunrise")),
                sunset=datetime.fromtimestamp(resp.json().get("sys").get("sunset")),
                code=resp.json().get("cod"),
                message=None
            )
        else:
            data = CurrentWeatherData(
                cloud_main=None,
                cloud_description=None,
                cloud_icon=None,
                temperature=-999999.0,
                feels_like=-999999.0,
                minimum=-999999.0,
                maximum=-999999.0,
                pressure=-999999.0,
                pressure_ground_level=-999999.0,
                humidity=-999999.0,
                visibility=-999999.0,
                wind_speed=-999999.0,
                wind_direction=-999999,
                wind_gust=-999999.0,
                sunrise=datetime.fromtimestamp(18000),  # Set to 01/01/1970
                sunset=datetime.fromtimestamp(18000),  # Set to 01/01/1970
                code=resp.json().get("cod"),
                message=resp.json().get("message")
            )
    except HTTPError as e:
        print(f"{get_full_class_name(e)}: {e.read().decode()}")
        data = CurrentWeatherData(
            cloud_main=None,
            cloud_description=None,
            cloud_icon=None,
            temperature=-999999.0,
            feels_like=-999999.0,
            minimum=-999999.0,
            maximum=-999999.0,
            pressure=-999999.0,
            pressure_ground_level=-999999.0,
            humidity=-999999.0,
            visibility=-999999.0,
            wind_speed=-999999.0,
            wind_direction=-999999,
            wind_gust=-999999.0,
            sunrise=datetime.fromtimestamp(18000),  # Set to 01/01/1970
            sunset=datetime.fromtimestamp(18000),  # Set to 01/01/1970
            code=-1,
            message=None
        )
    except (IndexError, ValueError, TypeError, AttributeError) as e:
        print(f"{get_full_class_name(e)}: {e.args}")
        data = CurrentWeatherData(
            cloud_main=None,
            cloud_description=None,
            cloud_icon=None,
            temperature=-999999.0,
            feels_like=-999999.0,
            minimum=-999999.0,
            maximum=-999999.0,
            pressure=-999999.0,
            pressure_ground_level=-999999.0,
            humidity=-999999.0,
            visibility=-999999.0,
            wind_speed=-999999.0,
            wind_direction=-999999,
            wind_gust=-999999.0,
            sunrise=datetime.fromtimestamp(18000),  # Set to 01/01/1970
            sunset=datetime.fromtimestamp(18000),  # Set to 01/01/1970
            code=-1,
            message=None
        )

    return data


def main(city_name: str, state_code: str, country_code: str) -> \
        (tuple[Type[Location], Type[CurrentWeatherData], Type[Formats]] | tuple):
    """
    :param city_name:      The city name to get the latitude and longitude from.
    :param state_code:     The state code to get the latitude and longitude from.
    :param country_code:   The country code to get the latitude and longitude from.

    :return:               Tuple of the Location and the CurrentWeatherData dataclasses.
    """
    # Run configure
    # api_key, units_of_measure = configure()
    location_data: Location = get_lan_lon(city_name, state_code, country_code)
    print(f"In main Location.city: {location_data.city}")
    # lat type: <class 'float'>
    print(f"lat type: {type(location_data.latitude)}")
    # lon type: <class 'float'>
    print(f"lon type: {type(location_data.longitude)}")
    current_weather_data: CurrentWeatherData = get_current_weather(location_data.latitude,
                                                                   location_data.longitude)
    print(f"In main CurrentWeatherData.temperature: {current_weather_data.temperature}")

    print(f"In main location_data: {location_data}")
    print(f"In main current_weather_data: {current_weather_data}")

    return location_data, current_weather_data, Formats


if __name__ == '__main__':
    main('Atlanta', 'GA', country_code='US')
    # main('Toronto', '', country_code='CA')
    # main('Dublin', '', country_code = 'IE')
    # main('London', '', country_code='GB')
