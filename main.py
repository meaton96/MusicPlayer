# Michael Eaton
# Music Player
# uses a GUI to display a folder of mp3 files and allow the user to play them
from PIL.Image import Resampling
from pygame import mixer
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import time


def configure_frame(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))


def display_info_box():
    info = "Use the Folder button (Bottom Left) To open a folder\n" \
           "Click a song to select, Play to play the song\n" \
           "Can also play a song by double clicking it\n" \
           "Next and Previous buttons function as well as mute button and volume slider\n" \
           "Hitting the play button when a new song has been selected will auto play the new song"
    messagebox.showinfo("Info", info)


class MusicGUI:

    def __init__(self):
        # init buttons variables
        self.mute_button = None
        self.button_frame = None
        self.next_button = None
        self.previous_button = None
        self.play_button = None
        self.quit_button = None
        self.open_folder_button = None
        self.pause_button = None
        self.volume_slider = None
        self.info_button = None
        self.cur_vol = 100
        self.previous_vol = 0

        # initialize mixer and create main Tkinter window
        mixer.init()
        self.main_window = tk.Tk(className="Music Player")
        self.main_window.geometry("800x600")
        self.main_window.resizable(False, False)

        self.WIDTH = 800

        # initialize list and display variables
        self.directory = ""
        self.song_choice = ""
        self.song_labels = []
        self.song_list = []
        self.current_song = ""
        self.is_playing_song = False
        self.paused = False

        self.PAUSE = "Pause"
        self.PLAY = "Play"

        # create basic frames
        self.song_canvas = tk.Canvas(self.main_window, bd=-2, background="#FFFFFF", name="song_canvas")
        self.song_list_frame = tk.Frame(self.song_canvas,
                                        name="song_frame", pady=2, padx=2, bg="#FFFFFF")

        self.button_frame = tk.Frame(self.main_window, bg="#33964e", width=100, height=60)
        self.button_canvas = tk.Canvas(self.button_frame, width=self.WIDTH - 100,
                                       height=60, bg="#33964e", bd=-2)
        # create bottom and top Canvas
        self.button_canvas.grid(row=0, column=0)
        self.top_canvas = tk.Canvas(self.main_window, width=self.WIDTH, height=30, bd=-2)

        self.create_buttons()

        self.song_scroll = ttk.Scrollbar(self.main_window, orient="vertical", command=self.song_canvas.yview)
        self.song_canvas.configure(yscrollcommand=self.song_scroll.set)

        # empty directory label
        self.empty_label_text = tk.StringVar()
        self.empty_label_text.set("Nothing is here\nOpen a Folder! (Bottom Left)")
        self.empty_label = tk.Label(self.song_list_frame, textvariable=self.empty_label_text, bg="#FFFFFF", padx=300,
                                    pady=200)
        self.is_empty_dir = True

        # create song info bar
        self.song_length = tk.StringVar()
        self.info_bar = tk.Label(self.main_window, textvariable=self.song_length, bd=1, bg="#33964e", anchor=tk.E)
        self.info_bar.pack(fill="x", side="bottom")

        # pack widgets
        self.top_canvas.pack()
        self.empty_label.pack()
        self.song_list_frame.pack()
        self.button_frame.pack(side="bottom")
        self.song_scroll.pack(side="right", fill="y")
        self.song_canvas.pack(side="left", fill="both", expand=True)
        self.song_canvas.create_window((0, 0), window=self.song_list_frame, anchor="nw")

        # bind the scroll bar to the song canvas
        self.song_list_frame.bind("<Configure>", lambda e, canvas=self.song_canvas: configure_frame(self.song_canvas))

        tk.mainloop()

    def create_buttons(self):
        center_x = self.WIDTH // 2

        # create a style to remove the background of the volume slider
        style = ttk.Style()
        style.configure('TScale', background="#33964e")

        # volume slider
        self.volume_slider = ttk.Scale(self.button_frame, from_=0, to=100, orient=tkinter.HORIZONTAL,
                                       command=self.change_volume, style="TScale")
        self.volume_slider.set(100)
        self.volume_slider.grid(row=0, column=1)

        path = os.path.abspath(os.path.dirname(__file__))

        # create TransparentButton instances with the correct icon
        icon_path = os.path.join(path, "icons\\open_folder_icon.png")
        self.open_folder_button = TransparentButton(self.button_canvas, 5, 15, 50, 50, image_path=icon_path,
                                                    command=self.open_dir, state=tk.NORMAL)

        icon_path = os.path.join(path, "icons\\quit_icon.png")
        self.quit_button = TransparentButton(self.top_canvas, 2, 2, 30, 30, image_path=icon_path,
                                             command=self.main_window.destroy, state=tk.NORMAL)

        icon_path = os.path.join(path, "icons\\play_button_icon.png")
        self.play_button = TransparentButton(self.button_canvas, center_x - 25, 5, 50, 50,
                                             image_path=icon_path, command=self.pause_song, state=tk.NORMAL)

        icon_path = os.path.join(path, "icons\\pause_button_icon.png")
        self.pause_button = TransparentButton(self.button_canvas, center_x - 25, 5, 50, 50,
                                              image_path=icon_path, command=self.pause_song, state=tk.HIDDEN)

        icon_path = os.path.join(path, "icons\\previous_button_icon.png")
        self.previous_button = TransparentButton(self.button_canvas, center_x - 60, 19, 30, 30, image_path=icon_path,
                                                 command=self.prev_song, state=tk.NORMAL)

        icon_path = os.path.join(path, "icons\\next_button_icon.png")
        self.next_button = TransparentButton(self.button_canvas, center_x + 35, 19, 30, 30, image_path=icon_path,
                                             command=self.next_song, state=tk.NORMAL)

        icon_path = os.path.join(path, "icons\\volume_icon.png")
        self.mute_button = TransparentButton(self.button_canvas, 660, 19, 30, 30,
                                             image_path=icon_path, command=self.mute, state=tk.NORMAL)

        icon_path = os.path.join(path, "icons\\info_icon.png")
        self.info_button = TransparentButton(self.top_canvas, 750, 2, 25, 25, image_path=icon_path,
                                             command=display_info_box, state=tk.NORMAL)

    def get_song_length(self):
        # get song time
        current_time = mixer.music.get_pos() / 1000

        # convert to time format
        time_text = time.strftime("%M:%S", time.gmtime(current_time))

        # output to screen
        self.song_length.set(time_text)

        # update time
        self.info_bar.after(500, self.get_song_length)

        # play next song if this one is finished
        if not self.paused and not mixer.music.get_busy():
            self.next_song()

    # change the volume based on the slider value
    def change_volume(self, vol):
        mixer.music.set_volume(float(vol) / 100)
        self.cur_vol = float(vol) / 100

    # mute or unmute the volume
    def mute(self):
        if self.cur_vol != 0:
            self.previous_vol = self.cur_vol
            self.volume_slider.set(0)
        else:
            self.cur_vol = self.previous_vol
            self.volume_slider.set(self.cur_vol * 100)

    # move the current playing song in the specified direction
    def skip_song(self, direction):
        # change song list index
        current_song = self.song_list.index(self.song_choice)
        current_song += direction

        # make sure its in bounds
        if current_song >= len(self.song_list):
            current_song = 0
        elif current_song < 0:
            current_song = len(self.song_list) - 1

        # set the current song choice to the new song
        # generate an event as if that song was clicked on to easily move song hi-light indicator
        # call pause_song() to begin playing the new song
        self.song_choice = self.song_list[current_song]
        self.song_labels[current_song].event_generate("<Button-1>")
        self.is_playing_song = False
        self.paused = False
        self.pause_song()

    # play the next song in the queue
    def next_song(self):
        self.skip_song(1)

    # play the previous song in the queue
    def prev_song(self):
        self.skip_song(-1)

    # pause or play a song
    def pause_song(self):
        if not self.is_empty_dir:
            if self.is_playing_song:
                mixer.music.pause()
                self.paused = True
                self.pause_button.set_state(tk.HIDDEN)
                self.play_button.set_state(tk.NORMAL)
                self.is_playing_song = False
            else:
                # if a song isn't playing and a new song isn't being chosen to play then unpause the song
                if self.current_song == self.song_choice:
                    mixer.music.unpause()
                # if a new song has been selected to play then load that song and play it
                else:
                    song_path = os.path.join(self.directory, self.song_choice)
                    mixer.music.load(song_path)
                    mixer.music.play()
                    self.get_song_length()
                    self.current_song = self.song_choice
                self.paused = False
                self.pause_button.set_state(tk.NORMAL)
                self.play_button.set_state(tk.HIDDEN)
                self.is_playing_song = True

    # open a directory to play music from
    def open_dir(self):
        # ask the user for the folder and init file list
        self.directory = tkinter.filedialog.askdirectory()
        files = []
        try:
            # create the list of files from the folder
            files = os.listdir(self.directory)
            # set directory as not empty and remove the open directory buttons and label text
            self.is_empty_dir = False
            self.empty_label.destroy()
            # print an error message if the opened folder was empty
        except FileNotFoundError:
            self.empty_label_text.set("Directory not found please try again")

        # create labels and add each file to the song list
        count = 0
        self.song_list = []
        self.song_labels = []
        for fileName in files:
            self.song_list.append(fileName)
            self.song_labels.append(
                tk.Label(self.song_list_frame, text=fileName, cursor="hand2", name=str(count), width=80,
                         bg="white"))
            count += 1
        # iterate the list of songs and assign tkinter event binds to them for selecting/playing
        for label in self.song_labels:
            label.pack()
            label.bind("<Button-1>", self.set_song)
            label.bind("<Double-Button-1>", self.quick_play_song)

    # instantly play a new song by double-clicking on it
    def quick_play_song(self, event):
        self.set_song(event)
        self.is_playing_song = False
        self.pause_song()

    # allows for single clicking on a song in the list in order to play it
    def set_song(self, event):
        # check if the directory is empty to prevent errors
        if not self.is_empty_dir:
            # get the number of the widget from the passed in event
            widget = event.widget
            # set the background of the widget blue and the color of the text to white
            widget.configure(bg="blue", fg="white")

            # set all other songs in the list to white background with black text to deselect them
            for label in self.song_labels:
                if label != event.widget:
                    label.configure(bg="white", fg="black")

            # remove the name of the frame to isolate the song number
            # set the song choice to the song from the song list based on the number
            self.song_choice = self.song_list[
                int(str(widget).strip("canvas.song_frame."))]


# draws a button on a canvas, used to create an icon button that can be clicked on
class TransparentButton:

    def __init__(self, canvas, x, y, width, height, image_path, command, state):
        self.canvas = canvas
        self.image = Image.open(image_path)
        resized_image = self.image.resize((width, height), Resampling.LANCZOS)
        self.btn_image = ImageTk.PhotoImage(resized_image)
        self.button = canvas.create_image(x, y, anchor='nw', state=state,
                                          image=self.btn_image)
        canvas.tag_bind(self.button, "<ButtonRelease-1>", lambda e: command())

    # used to hide or show the button
    def set_state(self, state):
        self.canvas.itemconfigure(self.button, state=state)


if __name__ == '__main__':
    my_gui = MusicGUI()
