import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import requests
import vlc
import pafy
import os
os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
from PIL import ImageGrab, ImageTk, Image
from Player import Player
from NotePad import NotePad
from io import BytesIO

class Frames:
    def __init__(self, root, frame_name, controller, mainroot):
        self.parent = root
        self._frame = tk.Frame(root, width=1000, height=1000, bg="#BDEDFF")
        self._frame.pack(fill='both', expand=True)
        self._controller = controller

        self.exit = tk.Button(mainroot, text="Exit", command=mainroot.destroy, font=('Cooper', 10), bg="#000000", fg="#FFFFFF", width=10,relief='raised', borderwidth=3)
        self.exit.place(x=0, y=0)

        self.msg = " "
        self.helpButton = tk.Button(self._frame, text="About", font=('Cooper', 10), width=10,
                                    command=lambda:self.aboutInfo(self.msg), relief='raised', borderwidth=3)
        self.helpButton.place(x=0, y=0)
        root.add(self._frame, text=frame_name)

    #every frame has the About Button providing different information
    def aboutInfo(self, msg):
        msg = tk.messagebox.showinfo("About", msg)

#the home frame, containing the Logo and some information
class HomeFrame(Frames):
    def __init__(self, root, frame_name, controller, mainroot):
        super().__init__(root, frame_name, controller, mainroot)

        self.title = ttk.Label(self._frame, text="Welcome to your TravelPlanner App!", font=('Cooper Black', 22),background="#BDEDFF" )
        self.title.place(x=140, y=60)

        self.motto = tk.Label(self._frame, text='\tIt has never been easier to travel!\nFind all the needed information about your destination - all in one place!',
                               background="#BDEDFF",font=('Courier Black', 14), relief= "sunken")
        self.motto.place(x=120, y=550)

        image = Image.open('C:/Users/Vio/Downloads/TravelPlannerLogo.png')
        photo = ImageTk.PhotoImage(image)
        self.LabelPhoto = tk.Label(self._frame, image=photo, bg="#BDEDFF")
        self.LabelPhoto.image = photo
        self.LabelPhoto.place(x=250, y=200)

        self.msg="""\n    TravelPlanner App is a tool designed to provide various information about a destination for a traveller.\n\n    The app offers to the user up-to-date information about: CURRENCY, EXCHANGE RATE, TOURIST ATTRACTIONS AND WEATHER FORECAST for the searched destination city/country.
                """
        self.helpButton.configure(command=lambda: self.aboutInfo(self.msg))

        self.creditsLabel=tk.Label(self._frame, text="Created my free logo at LogoMakr.com", font=('Courier Black', 10))
        self.creditsLabel.place(x=300, y=650)

#given the home currency and the destination country, information about the exchange rates between the currencies is shown
class CurrencyFrame(Frames):
    def __init__(self, root, frame_name, controller, mainroot):
        super().__init__(root, frame_name, controller, mainroot)

        self.title = ttk.Label(self._frame, text="Currency and exchange rate", font=('Cooper Black', 18))
        self.title.pack(side=tk.TOP)

        self.destination_variable = tk.StringVar(self._frame)
        self.destination_variable.set("Romania")

        self._destination_currency = []
        self.homeCurrency = ttk.LabelFrame(self._frame, text="Your home currency:")
        self.homeCurrency.pack(pady=10)

        self._curr_entry = ttk.Entry(self.homeCurrency, font=('Cooper Black', 16))
        self._curr_entry.pack(pady=10, padx=10)

        #choose the search option: by city or by country
        self.option_variable = tk.StringVar(self._frame)
        self.option_variable.set("City")

        self.optionLabel = ttk.LabelFrame(self._frame, text="Search destination by...")
        self.optionLabel.pack(pady=10)

        self.option = ttk.Combobox(self.optionLabel, textvariable=self.option_variable,
                                   values=['City', 'Country'],
                                   width=12, justify=tk.CENTER)
        self.option.pack(pady=10, padx=10)

        self.continueButton = tk.Button(self._frame, text="Continue", command=self.activateOption)
        self.continueButton.pack(pady=10, padx=10)

        #activate just after choosing the search option
        self.labelCountry = ttk.LabelFrame(self._frame, text="Your destination country:")
        self.labelCountry.pack_forget()

        self._destination_Country = ttk.Combobox(self.labelCountry, textvariable=self.destination_variable,
                                                  values=self._controller.get_countries(),
                                                    width=12, justify=tk.CENTER)
        self._destination_Country.pack_forget()


        self.labelCity = ttk.LabelFrame(self._frame, text = "Your destination city: ")
        self.labelCity.pack_forget()

        self.destinationCity = ttk.Entry(self.labelCity, font=('Cooper Black', 16))
        self.destinationCity.pack_forget()


        self._currency = ttk.LabelFrame(self._frame, text="")
        self._currency.pack_forget()

        self._res = tk.Label(self._currency, text="")
        self._res.pack_forget()

        self._change1 = ttk.LabelFrame(self._frame, text="")
        self._change1.pack_forget()

        self._val1 = tk.Label(self._change1, text="")
        self._val1.pack()

        self._change2 = ttk.LabelFrame(self._frame, text="")
        self._change2.pack_forget()

        self._val2 = tk.Label(self._change2, text="")
        self._val2.pack()


        self.getResult = tk.Button(self._frame, text="Get Currency", command=lambda: self.showResults(self._curr_entry.get()))
        self.getResult.pack_forget()


        self.printscreen=tk.Button(self._frame, text="Save information", command=self.printScreen)
        self.printscreen.place(x=600, y=200)


        self.msg="""\t\t! LIVE Exchange Rates !\n\n\n   The Currency Frame a tool designed to identify the local currency in the given city or country.\n\n  It also detects the current exchange rate between the home currency of the user and the currency identified in the destination city/country.
        \nFeatures: Save as a document of the displayed calculated data.
        """
        self.helpButton.configure(command=lambda:self.aboutInfo(self.msg))

    #switch between city/country search widgets
    #activating and deactivating widgets in order to show the proper display for city/country
    def activateOption(self):

            self._currency.pack_forget()
            self._res.pack_forget()
            self._change1.pack_forget()

            self._val1.configure(text="")
            self._val1.pack()

            self._change2.pack_forget()

            self._val2.configure(text="")
            self._val2.pack()

            self.getResult.pack_forget()

            if self.option_variable.get() == 'City':
                self.labelCountry.pack_forget()
                self._destination_Country.pack_forget()
                self.labelCity.pack(pady=10)
                self.destinationCity.pack(pady=10, padx=10)
                self.getResult.pack(pady=10, padx=10)
            else:
                self.labelCity.pack_forget()
                self.destinationCity.pack_forget()
                self.labelCountry.pack(pady=10)
                self._destination_Country.pack(pady=10, padx=10)
                self.getResult.pack(pady=10, padx=10)


    #print screen the Currency frame with the needed information
    def printScreen(self):
        file_name = filedialog.asksaveasfilename(defaultextension=".*", title="Save File", filetypes=(
            ("Png files", "*.png"), ("Jpg Files", "*.jpg"), ("All Files", "*.*")))

        x = self.parent.winfo_rootx() + self._frame.winfo_x()
        y = self.parent.winfo_rooty() + self._frame.winfo_y()
        x1 = x + self._frame.winfo_width()
        y1 = y + self._frame.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1-50)).save(file_name)

        confirm = tk.messagebox.showinfo(title="Info", message="Document saved successfully!")

    def showResults(self, home):

        if self.option_variable.get() == 'City':
            op = 1
            dest = self.destinationCity.get()
        else:
            op = 2
            dest = self._destination_Country.get()
        self._currency.configure(text="Currency in {0}:".format(dest))
        self._currency.pack(pady=20, fill="both", expand="yes")

        self._destination_currency = self._controller.getCurrency(dest, op)

        #if the introduced currency is invalid or if there are connection errors
        if self._destination_currency == None:
            self._res.configure(text='Invalid data. Please try again!', font=('Cooper Black', 16))
            self._res.pack()
        else:
            self._res.configure(text=self._destination_currency, font=('Cooper Black', 16))
            self._res.pack()

        self._change1.configure(text="1 {0} = ... {1} :".format(home, self._destination_currency))
        self._change1.pack(pady=20, fill="both", expand="yes")

        self._val1.configure(text=self._controller.homeTodest(home, self._destination_currency), font=('Cooper Black', 16))
        self._val1.pack()

        self._change2.configure(text="1 {0} = ... {1} :".format(self._destination_currency, home))
        self._change2.pack(pady=20, fill="both", expand="yes")

        self._val2.configure(text=self._controller.destTohome(home, self._destination_currency), font=('Cooper Black', 16))
        self._val2.pack()

#choosing the two currencies and the amount of money, the converted amount is shown
class ConvertFrame(Frames):
    def __init__(self, root, frame_name, controller, mainroot):
        super().__init__(root, frame_name, controller, mainroot)

        self.title = ttk.Label(self._frame, text="Convert currency", font=('Cooper Black', 18))
        self.title.pack(side=tk.TOP)

        self.amount_field = tk.Entry(self._frame, bd=3, relief=tk.RIDGE, justify=tk.CENTER)
        self.converted_amount_field_label = tk.Label(self._frame, text='', fg='black', bg='white', relief=tk.RIDGE, justify=tk.CENTER, width=17, borderwidth=3)

        self.from_currency_variable = tk.StringVar(self._frame)
        self.from_currency_variable.set("INR")  # default value
        self.to_currency_variable = tk.StringVar(self._frame)
        self.to_currency_variable.set("USD")  # default value

        self.from_currency_dropdown = ttk.Combobox(self._frame, textvariable=self.from_currency_variable, values=list(self._controller.get_currencies().keys()),
                                                   state='readonly', width=12, justify=tk.CENTER)
        self.to_currency_dropdown = ttk.Combobox(self._frame, textvariable=self.to_currency_variable, values=list(self._controller.get_currencies().keys()),
                                                 state='readonly', width=12, justify=tk.CENTER)

        self.from_currency_dropdown.place(x=200, y=120)
        self.amount_field.place(x=200, y=150)
        self.to_currency_dropdown.place(x=510, y=120)
        self.converted_amount_field_label.place(x=510, y=150)

        self.convert_button = tk.Button(self._frame, text="Convert", fg="black", command=self.convert_action)
        self.convert_button.config(font=('Courier', 10, 'bold'))
        self.convert_button.place(x=385, y=135)

        self.msg = """\t\t! LIVE Exchange Rates !\n\n\n\nThe Convert Frame is a tool designed to convert an amount from one currency in another.
                """
        self.helpButton.configure(command=lambda: self.aboutInfo(self.msg))

    def convert_action(self):
        amount = float(self.amount_field.get())
        from_curr = self.from_currency_variable.get()
        to_curr = self.to_currency_variable.get()

        converted_amount = self._controller.convert(from_curr, to_curr, amount)
        converted_amount = round(converted_amount, 2)

        self.converted_amount_field_label.config(text=str(converted_amount))

#given a country, a vlc player is playing a yt video with places to visit
#options: download yt video, take notes and save the document
class TravelFrame(Frames):
    def __init__(self, root, frame_name, controller, mainroot):
        super().__init__(root, frame_name, controller, mainroot)

        self.country=" "

        self.title=ttk.Label(self._frame, text="Top 10 places to visit in ... ", font=('Cooper Black', 18))
        self.title.pack(side=tk.TOP)

        self.labelCountry = ttk.LabelFrame(self._frame, text="The city/country you want to visit:")
        self.labelCountry.pack(pady=40)

        self._country_entry = ttk.Entry(self.labelCountry, font=('Cooper Black', 16))
        self._country_entry.pack(pady=10, padx=10)

        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()

        self._searchButton = tk.Button(self._frame, text="Search", fg="black", command=lambda:self.searchPlaces(self._country_entry.get()))
        self._searchButton.pack()

        self.noteButton = tk.Button(self._frame, text="Take notes during the video", fg="black", command=self.takeNotes)
        self.noteButton.pack(side=tk.RIGHT)


        self.msg = """\tThe Travel Frame containes an integrated video player that plays the most relevant Youtube video with tourist attractions in the city/country given by the user.\n
        \tFeatures while playing video: download video and take notes in a built-in notepad, that can be saved in the user's computer.
                """
        self.helpButton.configure(command=lambda: self.aboutInfo(self.msg))

    #open the Notepad frame
    def takeNotes(self):

        note_root = tk.Toplevel(self._frame)
        note_root.title('NotePad')
        note_root.geometry('400x400+800+200')

        my_notepad = NotePad(note_root)
        note_root.mainloop()

    #open player frame
    def searchPlaces(self, country):
        link = self._controller.getYtLink(country)
        self.country = country
        video = pafy.new(link)
        best = video.getbest()
        playurl = best.url
        root = tk.Tk()
        root.lift()
        root.attributes('-topmost', True)
        player = Player(root, link, playurl, self.country)
        root.protocol("WM_DELETE_WINDOW", player.OnClose)  # XXX unnecessary (on macOS)
        root.mainloop()

#given a city, the weather condition on the current moment are displayed
#information displayed: country, temperature, weather condition description, pressure, humidity, wind, sunrise, sunset
class WeatherFrame(Frames):
    def __init__(self, root, frame_name, controller, mainroot):
        super().__init__(root, frame_name, controller, mainroot)

        self.title = ttk.Label(self._frame, text="Weather forecast", font=('Cooper Black', 18))
        self.title.pack(side=tk.TOP)

        self.labelCity = ttk.LabelFrame(self._frame, text="City:")
        self.labelCity.pack(pady=20)

        self._city_entry = ttk.Entry(self.labelCity, font=('Cooper Black', 16))
        self._city_entry.pack(pady=10, padx=10)

        self._country = ttk.LabelFrame(self._frame, text="Country: ")
        self._country.pack_forget()

        self._count = tk.Label(self._country, text="")
        self._count.pack_forget()

        self._temperature = ttk.LabelFrame(self._frame, text="Temperature: ")
        self._temperature.pack_forget()

        self._temp = tk.Label(self._temperature, text="")
        self._temp.pack_forget()

        self._description = ttk.LabelFrame(self._frame, text="Conditions: ")
        self._description.pack_forget()

        self._desc = tk.Label(self._description, text="")
        self._desc.pack_forget()

        self._pressure = ttk.LabelFrame(self._frame, text="Pressure: ")
        self._pressure.pack_forget()

        self._press = tk.Label(self._pressure, text="")
        self._press.pack_forget()

        self._humidity = ttk.LabelFrame(self._frame, text="Humidity: ")
        self._humidity.pack_forget()

        self._hum = tk.Label(self._humidity, text="")
        self._hum.pack_forget()

        self._windspeed = ttk.LabelFrame(self._frame, text="Wind: ")
        self._windspeed.pack_forget()

        self._speed= tk.Label(self._windspeed, text="")
        self._speed.pack_forget()

        self._sunrise = ttk.LabelFrame(self._frame, text="Sunrise: ")
        self._sunrise.pack_forget()

        self._rise = tk.Label(self._sunrise, text="")
        self._rise.pack_forget()

        self._sunset = ttk.LabelFrame(self._frame, text="Sunset: ")
        self._sunset.pack_forget()

        self._set = tk.Label(self._sunset, text="")
        self._set.pack_forget()

        self.getResult = tk.Button(self._frame, text="Get Weather Forecast", command=self.getWeather)
        self.getResult.pack(pady=10, padx=10)

        self.printscreen = tk.Button(self._frame, text="Save information", command=self.printWeather)
        self.printscreen.pack()

        self.msg = """        The Weather Frame provides the current weather conditions in a specific city given by the user.\n
        Features: Save as a document of the displayed calculated data.
                       """
        self.helpButton.configure(command=lambda: self.aboutInfo(self.msg))


    def getWeather(self):

        weather = self._controller.getWeatherForecast(self._city_entry.get())
        if weather == None: #if no data was retrieved
            error = tk.messagebox.showinfo(title="Error", message="Invalid city! Try again...")
        else:
            temp = weather[0]
            description = weather[1]
            country = weather[2]
            pressure = weather[3]
            humidity = weather[4]
            wind = weather[5]
            sunrise = weather[6]
            sunset = weather[7]
            icon_id = weather[8]

            self._temp.configure(text=str(temp)+" °C")
            self._desc.configure(text=description)
            self._count.configure(text=country)
            self._press.configure(text=str(pressure)+" hPa")
            self._hum.configure(text=str(humidity)+"%")
            self._speed.configure(text=str(wind)+" km/h")
            self._rise.configure(text=sunrise+" AM")
            self._set.configure(text=sunset+ " PM")

            self._temp.pack(padx=0)
            self._desc.pack(padx=0)
            self._count.pack(padx=0)
            self._press.pack(padx=0)
            self._hum.pack(padx=0)
            self._speed.pack(padx=0)
            self._rise.pack(padx=0)
            self._set.pack(padx=0)

            self._temperature.pack(pady=10,fill="both")
            self._description.pack(pady=10,fill="both")
            self._country.pack(pady=10,fill="both")
            self._pressure.pack(pady=10,fill="both")
            self._humidity.pack(pady=10,fill="both")
            self._windspeed.pack(pady=10,fill="both")
            self._sunrise.pack(pady=10,fill="both")
            self._sunset.pack(pady=10,fill="both")

            url = requests.get("http://openweathermap.org/img/wn/{0}.png".format(icon_id), stream=True)
            weather_icon = url.content

            #display current weather icon
            photo = ImageTk.PhotoImage(Image.open(BytesIO(weather_icon)))
            weatherLabel = tk.Label(self._frame, image=photo, bg="#BDEDFF", borderwidth=2, relief="groove", highlightcolor="white")
            weatherLabel.image=photo
            weatherLabel.place(x=600, y=100)

    #print screen for the Weather frame
    def printWeather(self):
        file_name = filedialog.asksaveasfilename(defaultextension=".*", title="Save File", filetypes=(
            ("Png files", "*.png"), ("Jpg Files", "*.jpg"), ("All Files", "*.*")))

        x = self.parent.winfo_rootx() + self._frame.winfo_x()
        y = self.parent.winfo_rooty() + self._frame.winfo_y()
        x1 = x + self._frame.winfo_width()
        y1 = y + self._frame.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1-50)).save(file_name)

        confirm = tk.messagebox.showinfo(title="Info", message="Document saved successfully!")

