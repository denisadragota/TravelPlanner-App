import tkinter as tk
from tkinter import ttk
from Frames import HomeFrame, CurrencyFrame, ConvertFrame, TravelFrame, WeatherFrame
from Controller import Controller
from PIL import ImageTk, Image


#root window

my_root = tk.Tk()

max_height = my_root.winfo_screenheight()
max_width = my_root.winfo_screenwidth()
my_root.geometry('{0}x{1}'.format(max_width, max_height))
my_root.title('TravelPlanner')
my_root.configure(bg="#A0CFEC")
image = Image.open('C:/Users/Vio/Downloads/TravelPlannerIconLogo.png')
photo = ImageTk.PhotoImage(image)
my_root.iconphoto(False, photo)
s = ttk.Style()
s.theme_use('default')
s.configure('TNotebook.Tab', background="#A0CFEC")
s.map("TNotebook", background= [("selected", "#A0CFEC")])
#notebook
notebook = ttk.Notebook(my_root, width=800, height=800)
notebook.pack()

controller = Controller()
home_frame = HomeFrame(notebook, 'Home', controller, my_root)
currency_frame = CurrencyFrame(notebook, 'Exchange rate', controller, my_root)
convert_frame = ConvertFrame(notebook, 'Convert', controller, my_root)
travel_frame = TravelFrame(notebook, 'Travel', controller, my_root)
weather_frame = WeatherFrame(notebook, 'Weather', controller, my_root)

my_root.mainloop()
