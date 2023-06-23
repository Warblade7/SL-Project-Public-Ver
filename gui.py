from typing import Optional, Tuple, Union
import urllib.request
from PIL import Image
import spotipy 
import os
import json
import time
from datetime import datetime
import webbrowser
import tkinter
import tkinter.messagebox
import customtkinter
from urllib.parse import urlparse, parse_qs
import lyricsgenius as genius
import re
import logic

    
customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x700")
        self.title("DawlebFM - Spotify tool")

        self.grid_columnconfigure((0,1,2), weight=1)

        self.frame_buttons = customtkinter.CTkFrame(master=self)
        self.frame_buttons.grid(row=0, column=0, padx=20, pady=(20,10), sticky="nw")

        self.button_1 = customtkinter.CTkButton(master=self.frame_buttons, text="Authenticate")
        self.button_1.pack(pady=(10,0), padx=10)

        self.button_2 = customtkinter.CTkButton(master=self.frame_buttons, text="Current song", state="disabled")
        self.button_2.pack(pady=(10,0), padx=10)

        self.button_3 = customtkinter.CTkButton(master=self.frame_buttons, text="Get lyrics", state="disabled")
        self.button_3.pack(pady=(10,0), padx=10)

        self.button_4 = customtkinter.CTkButton(master=self.frame_buttons, text="Audio features", state="disabled")
        self.button_4.pack(pady=(10,0), padx=10)

        self.button_5 = customtkinter.CTkButton(master=self.frame_buttons, text="Audio analysis", state="disabled")
        self.button_5.pack(pady=(10,0), padx=10)

        self.button_6 = customtkinter.CTkButton(master=self.frame_buttons, text="Exit", command=self.destroy)
        self.button_6.pack(pady=(10,0), padx=10)
        
        #self.button_7 = customtkinter.CTkButton(master=self.frame_buttons, text="Recommendations",state="disabled", command=lambda: logic.recommendations(self, self.frame_features))
        #self.button_7.pack(pady=10, padx=10)

        self.frame_lyrics = customtkinter.CTkFrame(master=self)
        self.frame_lyrics.grid(row=0, column=2, rowspan=2, padx=10, pady=20, sticky="n")

        self.textbox_title = customtkinter.CTkTextbox(master=self.frame_lyrics, height=50, width=300, wrap="word")
        self.textbox_title.insert("0.0", "SET YOUR ENVVARS BEFORE USE\n")
        self.textbox_title.pack(pady=10, padx=10)

        self.textbox_lyrics = customtkinter.CTkTextbox(master=self.frame_lyrics, height=543, width=300, wrap="word")
        self.textbox_lyrics.insert("0.0", "IF YOU ARE LOGGING IN FOR THE FIRST TIME, AFTER AUTHENTICATION PUT RETURNED URL INTO TERMINAL\n")
        self.textbox_lyrics.pack(pady=10, padx=10)

        self.frame_picture = customtkinter.CTkFrame(master=self, height=300, width=300)
        self.frame_picture.grid(row=0, column=1, padx=10, pady=(23,0), sticky="n")

        self.frame_features = customtkinter.CTkFrame(master=self, height=330, width=300)
        self.frame_features.grid(row=1, column=0, columnspan=1, padx=(10,0), pady=23, sticky="s")

        self.frame_analysis = customtkinter.CTkFrame(master=self, height=330, width=300)
        self.frame_analysis.grid(row=1, column=1, padx=10, pady=23, sticky="s")

        self.button_1.configure(command=lambda: logic.authenticate(self.button_2, self))
        self.button_2.configure(command=lambda: logic.current(self.textbox_title, self.button_3, self.button_4, self.button_5, self.frame_picture, self.textbox_lyrics,self, self.frame_features, self.frame_analysis))
        self.button_3.configure(command=lambda: logic.get_lyrics(self.textbox_lyrics, self))
        self.button_4.configure(command=lambda: logic.audio_features(self,self.frame_features))
        self.button_5.configure(command=lambda: logic.audio_analysis(self,self.frame_analysis))

if __name__ == "__main__":
    app = App()
    app.mainloop()