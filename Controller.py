import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import time

class Controller:

    def __init__(self):
        #api for countries
        self.currencies_url = "https://wft-geo-db.p.rapidapi.com/v1/geo/countries"
        #api for current exchanges
        self.exchanges_url = "https://api.exchangerate-api.com/v4/latest"
        self.headers = {
        'x-rapidapi-host': "wft-geo-db.p.rapidapi.com",
        'x-rapidapi-key': "***"
        }

        # dictionary of all currencies
        self._currencies = requests.get('https://api.exchangerate-api.com/v4/latest/USD').json()["rates"]

    #using this api to extract the country code of a given city
    def getCountryofCity(self, city):
        api = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=***"
        data = requests.get(api).json()
        try:
            countryCode = data['sys']['country']
        except KeyError:
            return None

        return countryCode

    #identifies and returns the currency of the given destination country
    def getCurrency(self, destination, op):
        #op is the option meaning if the search is based on the entered city or by the entered country
        if op == 2: #search by given country

            parameters = {'namePrefix': destination }
            response = requests.request("GET", self.currencies_url, headers=self.headers, params=parameters)
            countries = json.loads(response.text)

            for country in countries['data']:
                if country['name'] == destination:
                    return country['currencyCodes'][0]
            return None

        else: #search by given city
            countryCode = self.getCountryofCity(destination)

            if countryCode == None:
                return None
            else:

                url = "https://wft-geo-db.p.rapidapi.com/v1/locale/currencies"

                querystring = {"countryId": countryCode}

                headers = {
                    'x-rapidapi-host': "wft-geo-db.p.rapidapi.com",
                    'x-rapidapi-key': "64a2c28d91mshc14956eb7591bdep14ba72jsn15cf4ed73a93"
                }

                response = requests.request("GET", url, headers=headers, params=querystring)

                currency = response.json()['data'][0]['code']
                return currency

    #returns the exchange rate between 2 currencies
    def homeTodest(self, home, dest):
        url = self.exchanges_url+'/{0}'.format(home)
        try:
            r = requests.get(url)
            data = r.json()
            currencies = data["rates"]
        #possible errors: connection, invalid currency, ...
        except requests.exceptions.RequestException:
            return ['---']
        except json.decoder.JSONDecodeError:
            return ['---']
        except KeyError:
            return ['---']

        if dest in currencies:
            return currencies[dest]
        else:
            return '---'

    # returns the exchange rate between 2 currencies (reverse)
    def destTohome(self, home, dest):
        url = self.exchanges_url + '/{0}'.format(dest)
        try:
            r = requests.get(url)
            data = r.json()
            currencies = data["rates"]
        # possible errors: connection, invalid currency, ...
        except requests.exceptions.RequestException:
            return ['---']
        except json.decoder.JSONDecodeError:  # This is the correct syntax
            return ['---']
        except KeyError:
            return ['---']

        if home in currencies:
            return currencies[home]
        else:
            return '---'

    #returns a converted amount of money
    def convert(self, from_currency, to_currency, amount):
        # first convert it into USD if it is not in USD.
        # because our base currency is USD
        if from_currency != 'USD':
            amount = amount / self._currencies[from_currency]
            # limiting the precision to 4 decimal places
        amount = round(amount * self._currencies[to_currency], 4)
        return amount

    #returns a list of all currencies worldwide
    def get_currencies(self):
        return self._currencies

    def get_countries(self):
        #using a csv file saved in computer for the complete list of countries in the world
        df = pd.read_csv('list-countries-wolrd.csv')
        #using pandas to extract just the column with countries
        countries = df['Country (or dependent territory)'].dropna().tolist()
        c = countries[1:]
        return c

    # using webscraping to find the link of the first youtube video named: Top 10 places to visit in ... (placeholder for the given country)
    def getYtLink(self, country):
        #url to search on Google the Top 10 places to visit in ... (placeholder for the given country)
        url='https://www.google.com/search?q=top+10+places+to+visit+in+{0}+youtube&biw=596&bih=833&tbm=vid&sxsrf=AOaemvInlPvhgIQB7OCblKizzGEt_QohEQ%3A1630154237650&ei=_S0qYdX3JrOPxc8PzNCJsA0&oq=top+10+places+to+visit+in+{0}+youtube&gs_l=psy-ab-video.3...187823.192270.0.192663.10.10.0.0.0.0.399.1570.0j5j0j2.7.0....0...1c.1.64.psy-ab-video..3.3.519...33i10k1.0.McLorq7iBbE'.format(country, country)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        #extracting the first youtube video link in the google results
        webSearch = soup.find('div', class_='yuRUbf')
        item=webSearch.find('a', href=True)
        ytlink=item['href']
        return ytlink

    #returns a list of all weather information on the current day
    #search based by city
    def getWeatherForecast(self, c):
        city = c
        api = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=***"

        data = requests.get(api).json()
        try:

            description = data['weather'][0]['description']
            temp = int(data['main']['temp'] - 273.15) #converted in Celsius degree
            country = data['sys']['country']
            pressure = data['main']['pressure']
            humidity = data['main']['humidity']
            wind = data['wind']['speed'] * 3.6 #converted in km/h
            sunrise = time.strftime("%I:%M:%S", time.gmtime(data['sys']['sunrise'] + int(data['timezone'])))
            sunset = time.strftime("%I:%M:%S", time.gmtime(data['sys']['sunset'] + int(data['timezone'])))
            icon_id = data['weather'][0]['icon']
        except KeyError: #if city is invalid, there is no data retrieved
            return None

        weather = []
        weather.append(temp)
        weather.append(description)
        weather.append(country)
        weather.append(pressure)
        weather.append(humidity)
        weather.append(wind)
        weather.append(sunrise)
        weather.append(sunset)
        weather.append(icon_id)

        return weather

