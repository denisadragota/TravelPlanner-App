import requests
import time
"""
import python_weather


async def getweather():
    # declare the client. format defaults to metric system (celcius, km/h, etc.)
    client = python_weather.Client(format=python_weather.METRIC)

    # fetch a weather forecast from a city
    weather = await client.find("Medias")

    # returns the current day's forecast temperature (int)
    print(weather.current.temperature)

    # get the weather forecast for a few days
    for forecast in weather.forecasts:
        print(str(forecast.date), forecast.sky_text, forecast.temperature)

    # close the wrapper once done
    await client.close()

"""

def getWeather(c):
    city = c
    api = "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid=***"

    data = requests.get(api).json()
    description = data['weather'][0]['description']
    temp = int(data['main']['temp']-273.15)
    country = data['sys']['country']
    pressure = data['main']['pressure']
    humidity = data['main']['humidity']
    wind = data['wind']['speed'] * 3.6
    sunrise = time.strftime("%I:%M:%S", time.gmtime(data['sys']['sunrise'] + int(data['timezone'])))
    sunset = time.strftime("%I:%M:%S", time.gmtime(data['sys']['sunset'] + int(data['timezone'])))
    icon_id = data['weather'][0]['icon']
    """
    print(
        "Country: " + str(country) + "\n",
        "Temperature: " + str(temp) + " °C\n",
        "Description: " + description + "\n",
        "Pressure: " + str(pressure) + " hPa \n",
        "Humidity: " + str(humidity) + "% \n",
        "Wind: " + str(wind) + " km/h \n",
        "Sunrise: " + sunrise + " AM \n",
        "Sunset: " + sunset + " PM \n",
    """
    icon1 = requests.get(f'http://openweathermap.org/img/wn/{icon_id}.png'.format(icon=icon_id))
    icon_Data = icon1.content
    icon_detail = ImageTk.PhotoImage(Image.open(BytesIO(icon_Data)))



