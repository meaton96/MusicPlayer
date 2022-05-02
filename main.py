# Michael Eaton
# Music Player
# uses a GUI to display a folder of mp3 files and allow the user to play them
from PIL.Image import Resampling
from pygame import mixer
import tkinter as tk
import tkinter.filedialog
import os
from PIL import Image, ImageTk


# change the volume based on the slider value
def change_volume(vol):
    mixer.music.set_volume(int(vol) / 100)


class MusicGUI:

    def __init__(self):
        # initialize mixer and create main Tkinter window
        self.quit_button = None
        self.open_folder_button = None
        self.pause_button = None
        self.pause_text = None
        self.volume_slider = None
        self.shuffle_button = None
        self.back_button = None
        self.next_button = None
        self.repeat_button = None

        mixer.init()
        self.main_window = tk.Tk(className="Music Player")
        self.main_window.geometry("800x600")

        self.WIDTH = 800

        # initialize list and display variables
        self.directory = ""
        self.song_choice = ""
        self.song_labels = []
        self.song_list = []
        self.current_song = ""
        self.is_playing_song = False

        self.PAUSE = "Pause"
        self.PLAY = "Play"

        # create basic frames
        self.button_frame = tk.Frame(self.main_window, bg="#4596ed", width=self.WIDTH, height=150, padx=200, pady=20)
        self.song_list_frame = tk.Frame(self.main_window, width=80, height=self.main_window.winfo_height(),
                                        name="song_frame", bd=-2)

        self.button_canvas = tk.Canvas(self.main_window, width=self.WIDTH,
                                       height=60, bg="#4596ed", bd=-2)

        self.top_canvas = tk.Canvas(self.song_list_frame, width=self.WIDTH, height=30, bd=-2)

        self.create_buttons()

        # empty directory label
        self.empty_label_text = tk.StringVar()
        self.empty_label_text.set("Nothing is here\nOpen a Folder! (Bottom Left)")
        self.empty_label = tk.Label(self.song_list_frame, textvariable=self.empty_label_text)
        self.is_empty_dir = True

        # pack widgets

        # self.open_folder_button

        # pack frames
        self.button_canvas.pack(side="bottom")
        self.top_canvas.pack()
        self.empty_label.pack()
        self.song_list_frame.pack()
        # self.button_frame.pack(side="bottom")

        tk.mainloop()

    def create_buttons(self):
        # pause button
        # self.pause_text = tk.StringVar()
        # self.pause_text.set(self.PLAY)
        # self.pause_button = tk.Button(self.button_frame, textvariable=self.pause_text, command=self.pause_song,
        #                              width=15)
        center_x = self.WIDTH // 2

        path = os.path.abspath(os.path.dirname(__file__))
        icon_path = os.path.join(path, "icons\\open_folder_icon.png")

        self.open_folder_button = TransparentButton(self.button_canvas, 5, 15, 50, 50, image_path=icon_path,
                                                    command=self.open_dir, state=tk.NORMAL)

        icon_path = os.path.join(path, "icons\\quit_icon.png")

        self.quit_button = TransparentButton(self.top_canvas, 2, 2, 30, 30, image_path=icon_path,
                                             command=self.main_window.destroy)

        icon_path = os.path.join(path, "icons\\play_button_icon.png")

        self.play_button = TransparentButton(self.button_canvas, center_x - 25, 5, 50, 50,
                                             image_path=icon_path, command=self.pause_song)

        icon_path = os.path.join(path, "icons\\pause_button_icon.png")

        self.pause_button = TransparentButton(self.button_canvas, center_x - 25, 5, 50, 50,
                                              image_path=icon_path, command=self.pause_song, state=tk.HIDDEN)

        # volume slider
        self.volume_slider = tk.Scale(self.button_frame, from_=0, to=100, orient=tkinter.HORIZONTAL, width=10,
                                      command=change_volume)
        self.volume_slider.set(100)
        self.volume_slider.pack()

    # pause or play a song
    def pause_song(self):
        # path = os.path.abspath(os.path.dirname(__file__))
        # icon_path = os.path.join(path, "icons\\open_folder_icon.png")
        # if a song is currently playing then pause it
        """
        issue here with playing a new song also
        """
        if not self.is_empty_dir:
            if self.is_playing_song:
                mixer.music.pause()
                self.pause_button.set_state(tk.HIDDEN)
                self.play_button.set_state(tk.NORMAL)
                self.is_playing_song = False
            else:
                # if a song isnt playing and a new song isnt being chosen to play then unpause the song
                if self.current_song == self.song_choice:
                    mixer.music.unpause()
                # if a new song has been selected to play then load that song and play it
                else:
                    song_path = os.path.join(self.directory, self.song_choice)
                    mixer.music.load(song_path)
                    mixer.music.play()
                    self.current_song = self.song_choice
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
                int(str(widget).strip(".song_frame."))]


# Had a lot of issues trying to create transparent background buttons
# came across this solution from
# https://stackoverflow.com/questions/70996098/tkinter-button-over-transparent-background/71011331#71011331
# changed a bit to fit my needs
class TransparentButton:
    """ Create leftmost mouse button clickable canvas image object.

    The x, y coordinates are relative to the top-left corner of the canvas.
    """
    flash_delay = 100  # Milliseconds.

    def __init__(self, canvas, x, y, width, height, image_path, command, state=tk.NORMAL):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.command = command
        self.canvas = canvas
        self.image = Image.open(image_path)
        resized_image = self.image.resize((width, height), Resampling.LANCZOS)
        self.btn_image = ImageTk.PhotoImage(resized_image)
        self.canvas_btn_img_obj = canvas.create_image(x, y, anchor='nw', state=state,
                                                      image=self.btn_image)
        canvas.tag_bind(self.canvas_btn_img_obj, "<ButtonRelease-1>", lambda event: (self.flash(), command()))

    def change_icon(self, image_path):
        self.image = Image.open(image_path)
        resized_image = self.image.resize((self.width, self.height), Resampling.LANCZOS)
        self.btn_image = ImageTk.PhotoImage(resized_image)
        self.canvas_btn_img_obj.config(image=self.btn_image)

    def flash(self):
        self.set_state(tk.HIDDEN)
        self.canvas.after(self.flash_delay, self.set_state, tk.NORMAL)

    def set_state(self, state):
        """ Change canvas button image's state.

        Normally, image objects are created in state tk.NORMAL. Use value
        tk.DISABLED to make it unresponsive to the mouse, or use tk.HIDDEN to
        make it invisible.
        """
        self.canvas.itemconfigure(self.canvas_btn_img_obj, state=state)


if __name__ == '__main__':
    my_gui = MusicGUI()
