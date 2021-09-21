from __future__ import unicode_literals
import youtube_dl
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tube_dl import Youtube

import pytube


Folder_Name = ""
ydl_opts={'ignore errors':True}
#file location
def openLocation():
    global Folder_Name
    global ydl_opts
    Folder_Name = filedialog.askdirectory()
    if(len(Folder_Name) > 1):
        ydl_opts = {'outtmpl': '{}/%(title)s.%(ext)s'.format(Folder_Name)}
        locationError.config(text=Folder_Name,fg="green")

    else:
        locationError.config(text="Please Choose Folder!!",fg="red")

#donwload video
def DownloadVideo():
    choice = ytdchoices.get()
    url = ytdEntry.get()

    if(len(url)>1):

        if(choice == choices[0]):
            #select = yt.streams.filter(progressive=True).first()
            #ydl_opts['format']= 'bestaudio/best'
            #with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                #ydl.download([url])
            Youtube(url).formats.first().download()

        elif(choice == choices[1]):
            #with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                #ydl.download([url])
            Youtube(url).formats.last().download()

        elif(choice == choices[2]):
            '''
            ydl_opts['format']= 'bestaudio/best'
            ydl_opts['postprocessors']= [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            ydl_opts['quiet']= False

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            '''

            Youtube(url).formats.filter_by(only_audio=True)[0].download(convert='mp3')


        else:
            ytdError.config(text="Paste Link again!!",fg="red")


    #download function
    #select.download(Folder_Name)
    ytdError.config(text="Download Completed!!")



root = Tk()
root.title("YTD Downloader")
root.geometry("350x400") #set window
root.columnconfigure(0,weight=1)#set all content in center.

#Ytd Link Label
ytdLabel = Label(root,text="Enter the URL of the Video",font=("jost",15))
ytdLabel.grid()

#Entry Box
ytdEntryVar = StringVar()
ytdEntry = Entry(root,width=50,textvariable=ytdEntryVar)
ytdEntry.grid()

#Error Msg
ytdError = Label(root,text="Error Msg",fg="red",font=("jost",10))
ytdError.grid()

#Asking save file label
saveLabel = Label(root,text="Save the Video File",font=("jost",15,"bold"))
saveLabel.grid()

#btn of save file
saveEntry = Button(root,width=10,bg="red",fg="white",text="Choose Path",command=openLocation)
saveEntry.grid()

#Error Msg location
locationError = Label(root,text="Error Msg of Path",fg="red",font=("jost",10))
locationError.grid()

#Download Quality
ytdQuality = Label(root,text="Select Quality",font=("jost",15))
ytdQuality.grid()

#combobox
choices = ["720p","144p","Only Audio"]
ytdchoices = ttk.Combobox(root,values=choices)
ytdchoices.grid()

#donwload btn
downloadbtn = Button(root,text="Donwload",width=10,bg="red",fg="white",command=DownloadVideo)
downloadbtn.grid()