# documentation I used for integrating the vcl player with tkinter:
# http://git.videolan.org/?p=vlc/bindings/python.git;a=blob;f=examples/tkvlc.py;h=55314cab09948fc2b7c84f14a76c6d1a7cbba127;hb=HEAD

from __future__ import unicode_literals
import vlc
import sys
from pytube import YouTube
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showerror
from os.path import join as joined
import time

_isMacOS = sys.platform.startswith('darwin')
_isWindows = sys.platform.startswith('win')
_isLinux = sys.platform.startswith('linux')

if _isMacOS:
    from ctypes import c_void_p, cdll
    # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
    # returns the tk library /usr/lib/libtk.dylib from macOS,
    # but we need the tkX.Y library bundled with Python 3+,
    # to match the version number of tkinter, _tkinter, etc.
    try:
        libtk = 'libtk%s.dylib' % (tk.TkVersion,)
        prefix = getattr(sys, 'base_prefix', sys.prefix)
        libtk = joined(prefix, 'lib', libtk)
        dylib = cdll.LoadLibrary(libtk)
        _GetNSView = dylib.TkMacOSXGetRootControl
        _GetNSView.restype = c_void_p
        _GetNSView.argtypes = c_void_p,
        del dylib

    except (NameError, OSError):  # image or symbol not found
        def _GetNSView(unused):
            return None
        libtk = "N/A"

    C_Key = "Command-"  # shortcut key modifier

else:  

    libtk = "N/A"
    C_Key = "Control-"  # shortcut key modifier

class Player(tk.Frame):
    """The main window has to deal with events.
    """
    _geometry = ''
    _stopped  = None

    def __init__(self, parent, link, url, country, title=None):
        tk.Frame.__init__(self, parent)

        self.parent = parent  # == root
        self.parent.title(title or "tkVLCplayer")
        self.link = link
        self.url = url
        self.video = ''
        self.folderName = " "
        self.yt_opts = {'ignore errors':True}
        self.country=country

        # Menu Bar
        # File Menu
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = tk.Menu(menubar)

        fileMenu.add_command(label="Start", command= self.OnStart)
        fileMenu.add_command(label="Play", command=self.OnPlay)  # Play/Pause
        fileMenu.add_command(label="Stop", command=self.OnStop)
        fileMenu.add_separator()
        fileMenu.add_command(label="Mute", command=self.OnMute)
        fileMenu.add_separator()
        fileMenu.add_command(label="Close", command=self.OnClose)
        fileMenu.add_separator()
        fileMenu.add_command(label="Download", command=self.DownloadVideo)

        menubar.add_cascade(label="File", menu=fileMenu)
        self.fileMenu = fileMenu
        self.playIndex = fileMenu.index("Play")
        self.muteIndex = fileMenu.index("Mute")

        # first, top panel shows video

        self.videopanel = ttk.Frame(self.parent)
        videoLabel1 = tk.Label(self.videopanel, text="Play Video: ",font=('Cooper Black', 18))
        videoLabel2 = tk.Label(self.videopanel, text="Top 10 places to visit in {0}".format(self.country), font=('Cooper Black', 20))
        videoLabel1.pack(side=tk.TOP)
        videoLabel2.pack()
        self.canvas = tk.Canvas(self.videopanel)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.videopanel.pack(fill=tk.BOTH, expand=1)

        # panel to hold buttons
        self.buttons_panel = tk.Toplevel(self.parent)
        self.buttons_panel.title("")
        self.buttons_panel.lift()
        self.buttons_panel.attributes('-topmost', True)
        self.is_buttons_panel_anchor_active = False


        buttons = ttk.Frame(self.buttons_panel)
        self.startButton = ttk.Button(buttons, text="Start", command=self.OnStart)
        self.playButton = ttk.Button(buttons, text="Play", command=self.OnPlay)
        stop            = ttk.Button(buttons, text="Stop", command=self.OnStop)
        self.muteButton = ttk.Button(buttons, text="Mute", command=self.OnMute)
        self.startButton.pack(side=tk.LEFT)
        self.playButton.pack(side=tk.LEFT)
        stop.pack(side=tk.LEFT)
        self.muteButton.pack(side=tk.LEFT)


        self.volMuted = False
        self.volSlider = tk.Scale(buttons,from_=0, to=100, orient=tk.HORIZONTAL,tickinterval=25, length=200,
                                  label='Volume')
        self.volSlider.bind("<B1-Motion>", self.OnVolume)
        self.volSlider.set(50)
        self.volSlider.pack(side=tk.RIGHT)
        buttons.pack(side=tk.BOTTOM, fill=tk.X)


        # panel to hold player time slider
        timers = ttk.Frame(self.buttons_panel)
        self.timeVar = tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = tk.Scale(timers, variable=self.timeVar, command=self.OnTime,
                                   from_=0, to=1000, orient=tk.HORIZONTAL, length=500,
                                   showvalue=0)  # label='Time',
        self.timeSlider.pack(side=tk.BOTTOM, fill=tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        timers.pack(side=tk.BOTTOM, fill=tk.X)


        # VLC player
        args = []
        if _isLinux:
            args.append('--no-xlib')
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()

        self.parent.bind("<Configure>", self.OnConfigure)  # catch window resize, etc.
        self.parent.update()

        # After parent.update() otherwise panel is ignored.
        self.buttons_panel.overrideredirect(True)

        # Estetic, to keep our video panel at least as wide as our buttons panel.
        self.parent.minsize(width=502, height=0)

        if _isMacOS:
            self.is_buttons_panel_anchor_active = True

            # Detect dragging of the buttons panel.
            self.buttons_panel.bind("<Button-1>", lambda event: setattr(self, "has_clicked_on_buttons_panel", event.y < 0))
            self.buttons_panel.bind("<B1-Motion>", self._DetectButtonsPanelDragging)
            self.buttons_panel.bind("<ButtonRelease-1>", lambda _: setattr(self, "has_clicked_on_buttons_panel", False))
            self.has_clicked_on_buttons_panel = False
        else:
            self.is_buttons_panel_anchor_active = False

        self._AnchorButtonsPanel()

        self.OnTick()  # set the timer up

        self.player.audio_set_mute(False)

    #select folder for downloading
    def openLocation(self):
        self.parent.attributes('-topmost', 0)
        self.buttons_panel.attributes('-topmost', 0)
        self.folderName = filedialog.askdirectory()
        if (len(self.folderName) > 1):
            self.yt_opts = {'outtmpl': '{}/%(title)s.%(ext)s'.format(self.folderName)}


    # download video
    def DownloadVideo(self):
        self.openLocation()
        self.parent.attributes('-topmost', 1)
        self.buttons_panel.attributes('-topmost', 1)
        url = 'https://youtu.be/'+self.link[32:]
        #using the pytube library for downloading a yooutube video
        yt = YouTube(url)
        select = yt.streams.filter(progressive=True, file_extension='mp4').first()
        select.download(self.folderName)
        msg = tk.messagebox.showinfo(title="Info", message="Video downloaded successfully!")


    def OnClose(self, *unused):
        """Closes the window and quit.
        """
        self.player.audio_set_mute(True)
        self.parent.quit()
        self.parent.destroy()


    def _DetectButtonsPanelDragging(self, _):
        """If our last click was on the boarder
           we disable the anchor.
        """
        if self.has_clicked_on_buttons_panel:
            self.is_buttons_panel_anchor_active = False
            self.buttons_panel.unbind("<Button-1>")
            self.buttons_panel.unbind("<B1-Motion>")
            self.buttons_panel.unbind("<ButtonRelease-1>")

    def _AnchorButtonsPanel(self):
        video_height = self.parent.winfo_height()
        panel_x = self.parent.winfo_x()
        panel_y = self.parent.winfo_y() + video_height + 40 # 23 seems to put the panel just below our video.
        panel_height = self.buttons_panel.winfo_height()
        panel_width = self.parent.winfo_width()+120
        self.buttons_panel.geometry("%sx%s+%s+%s" % (panel_width, panel_height, panel_x, panel_y))

    def OnConfigure(self, *unused):
        """Some widget configuration changed.
        """
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M12>
        self._geometry = ''  # force .OnResize in .OnTick, recursive?

        if self.is_buttons_panel_anchor_active:
            self._AnchorButtonsPanel()


    def OnMute(self, *unused):
        """Mute/Unmute audio.
        """

        self.volMuted = m = not self.volMuted
        self.player.audio_set_mute(m)
        u = "Unmute" if m else "Mute"
        self.fileMenu.entryconfig(self.muteIndex, label=u)

        self.muteButton.config(text=u)
        # update the volume slider text
        self.OnVolume()

    def OnStart(self, *unused):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        # if a file is already running, then stop it.
        self.OnStop()

        self._Play()

    def _Pause_Play(self, playing):
        # re-label menu item and button, adjust callbacks
        p = 'Pause' if playing else 'Play'
        c = self.OnPlay if playing is None else self.OnPause
        self.fileMenu.entryconfig(self.playIndex, label=p, command=c)
        self.playButton.config(text=p, command=c)
        self._stopped = False

    def _Play(self):
        # helper for OnOpen and OnPlay

        self.video = self.Instance.media_new(self.url)  # Path, unicode
        self.video.get_mrl()
        self.player.set_media(self.video)

        # set the window id where to render VLC's video output
        h = self.videopanel.winfo_id()
        if _isWindows:
            self.player.set_hwnd(h)
        elif _isMacOS:

            v = _GetNSView(h)
            if v:
                self.player.set_nsobject(v)
            else:
                self.player.set_xwindow(h)  # plays audio, no video
        else:
            self.player.set_xwindow(h)  # fails on Windows

        self.OnPlay()

    def OnPause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media():
            self._Pause_Play(not self.player.is_playing())
            self.player.pause()  # toggles

    def OnPlay(self, *unused):
        """Play video, if none is loaded, open the dialog window.
        """

        if not self.player.get_media():
            if self.video:
                self._Play()
                self.video = ''
            else:
                self.OnStart()
        # Try to play, if this fails display an error message
        elif self.player.play():  # == -1
            self.showError("Unable to play the video.")
        else:

            self._Pause_Play(True)
            # set volume slider to audio level
            vol = self.player.audio_get_volume()
            if vol > 0:
                self.volSlider.set(vol)


    def OnResize(self, *unused):
        """Adjust the window/frame to the video aspect ratio.
        """
        g = self.parent.geometry()
        if g != self._geometry and self.player:
            u, v = self.player.video_get_size()  # often (0, 0)
            if v > 0 and u > 0:
                # get window size and position
                g, x, y = g.split('+')
                w, h = g.split('x')

                if u > v:  # ... for landscape
                    # adjust the window height
                    h = round(float(w) * v / u)
                else:
                    # adjust the window width
                    w = round(float(h) * u / v)
                self.parent.geometry("%sx%s+%s+%s" % (w, h, x, y))
                self._geometry = self.parent.geometry()  # actual

    def OnStop(self, *unused):
        """Stop the player, resets media.
        """
        if self.player:
            self.player.stop()
            self._Pause_Play(None)
            # reset the time slider
            self.timeSlider.set(0)
            self._stopped = True

    def OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
        if self.player:
            # since the self.player.get_length may change while
            # playing, re-set the timeSlider to the correct range
            t = self.player.get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_time() * 1e-3  # to seconds
                # don't change slider while user is messing with it
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())
        # start the 1 second timer again
        self.parent.after(1000, self.OnTick)
        # adjust window to video aspect ratio, done periodically
        # on purpose since the player.video_get_size() only
        # returns non-zero sizes after playing for a while
        if not self._geometry:
            self.OnResize()

    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                self.player.set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()

    def OnVolume(self, *unused):
        """Volume slider changed, adjust the audio volume.
        """
        vol = self.volSlider.get()
        v_M = "%d%s" % (vol, " (Muted)" if self.volMuted else '')
        self.volSlider.config(label="Volume " + v_M)
        if self.player and not self._stopped:
            # .audio_set_volume returns 0 if success, -1 otherwise,
            if self.player.audio_set_volume(vol):  # and self.player.get_media():
                self.showError("Failed to set the volume: %s." % (v_M,))
            self.player.audio_set_volume(vol)

    def showError(self, message):
        #Display a simple error dialog.
        self.OnStop()
        showerror(self.parent.title(), message)
