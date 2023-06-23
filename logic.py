import urllib.request
from PIL import Image
import spotipy 
import os
import json
import time
import webbrowser
import tkinter
import tkinter.messagebox
import sched
from datetime import datetime
import customtkinter
from urllib.parse import urlparse, parse_qs
import lyricsgenius as genius
import re   
import random
import concurrent.futures

clientID = "PUT YOUR CLIENT ID HERE"
myClientSecretID = 'PUT YOUR CLIENT SECRET ID HERE'
redirect_uri = "https://www.google.com"
redirect_uri2 = "my-spotify-app://callback"
genius_token = 'PUT YOUR GENIUS TOKEN HERE'


spotify_client_id = os.getenv('SPOTIPY_CLIENT_ID',clientID)
spotify_secret_id = os.getenv('SPOTIPY_CLIENT_SECRET', myClientSecretID)
spotify_redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', redirect_uri)
genius_access_token = os.getenv('GENIUS_ACCESS_TOKEN', genius_token)


global spotify_object
global genius_object
global current_song
global previous_song
global artist_name
global song_name
global song_id

scope = 'user-read-currently-playing user-read-playback-state user-modify-playback-state user-read-recently-played'

def download_image(url, track_id):
    # Create the "images" folder if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")

    # Set the filename as "image.png"
    filename = track_id+".png"
    # Set the file path to the "images" folder
    if os.path.exists("images/"+track_id+".png"):
        os.remove("images/"+track_id+".png")
        
    filepath = os.path.join("images", filename)

    try:
        # Download the image from the URL
        urllib.request.urlretrieve(url, filepath)
    except urllib.error.URLError as e:
        print(f"Failed to download image: {e}")


def authenticate(button_2,app):
    global current_song, previous_song
    current_song = None
    previous_song = current_song
    
    oauth_object = spotipy.oauth2.SpotifyOAuth(client_id=spotify_client_id,
                                           client_secret=spotify_secret_id,
                                           redirect_uri=spotify_redirect_uri,
                                           scope=scope)

    #webbrowser.open(oauth_object.get_authorize_url())
    token_dict = oauth_object.get_access_token()   
    token = token_dict['access_token']
    global spotify_object
    spotify_object = spotipy.Spotify(auth=token)
    global genius_object
    genius_object = genius.Genius(genius_access_token)
    button_2.configure(state="normal")
    
    start_logging(spotify_object.current_user()['display_name'], app, period=15)
    
def current(textbox_buttons, button_3, button_4, button_5, frame_photo, textbox_lyrics, app, frame_features, freame_analysis):
    global spotify_object, artist_name, song_name, song_id, previous_song, current_song
    
    previous_song = current_song
    current_song = spotify_object.current_user_playing_track()
    if current_song == None:
        show_popup_no_song(app)
    else:
        update_song_data(current_song)
        textbox_buttons.delete("0.0", "end")
        textbox_buttons.insert("0.0", artist_name + " - " + song_name + "\n")
        download_image(get_photo_url(current_song),song_id)
        your_image = customtkinter.CTkImage(light_image=Image.open(os.path.join("images/"+song_id+".png")), size=(300, 300))
        label = customtkinter.CTkLabel(master=frame_photo, image=your_image, text='')
        label.grid(column=0, row=0)
        
        #enable rest of buttons
        button_3.configure(state="normal")
        button_4.configure(state="normal")
        button_5.configure(state="normal")
        textbox_lyrics.delete("0.0", "end")
        for widget in frame_features.winfo_children():
            widget.destroy()
        for widget in freame_analysis.winfo_children():
            widget.destroy()    
            
    
    
def start_logging(username, app, period):
    app.after(100, log_current_song( spotify_object.current_user()['display_name'], app, period=15))
    
def log_current_song(username, app, period):
    
    global previous_song, current_song
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"logs/{username}.txt"
    current_song = get_current_song_info()
    if current_song is not None:
        update_song_data(current_song)


    if ((current_song is not None and previous_song is None) or 
        (current_song is not None and previous_song is not None and current_song['item']['id']!= previous_song['item']['id'])):
        # Log the current song information
        #print(current_song)
        #print(previous_song) ##debug
        log_entry = {
            'song_name': song_name,
            'artist_name': artist_name,
            'song_id': song_id,
            'timestamp': timestamp
        }

        # Append the log entry to the log file
        append_log_entry(log_entry, log_filename)

    # Schedule the next logging iteration
    previous_song = current_song
    app.after(period * 1000, log_current_song, username, app, period)
    
def append_log_entry(log_entry, log_filename):
    # Append the log entry to the log file
    with open(log_filename, "a", encoding='utf-16') as log_file:
        log_file.write(str(log_entry) + "\n")

def update_song_data(song):
    global artist_name, song_name, song_id
    artist_name  = get_artist_name(current_song)
    song_name = get_song_name(current_song)
    song_id = get_song_id(current_song)
    
def get_artist_name(song):
    artist_name = song['item']['artists'][0]['name']
    return artist_name

def get_song_name(song):
    song_name = song['item']['name']
    return song_name

def get_song_id(song):
    song_id = song['item']['id']
    return song_id

def get_photo_url(song):    
    photourl = song['item']['album']['images'][0]['url']
    return photourl

def get_current_song_info():
    previous_song = current_song
    return spotify_object.current_user_playing_track()


        
    
def show_popup_no_song(app):
    popup = customtkinter.CTkToplevel(master=app)
    popup.title("No song playing")
    popup.geometry("300x200")
    popup_label = customtkinter.CTkLabel(master=popup, text="There is no song playing at the moment.")
    popup_label.pack(pady=10)
    popup.focus()
    
def show_popup_no_lyrics(app):
    popup = customtkinter.CTkToplevel(master=app)
    popup.title("No lyrics found")
    popup.geometry("300x200")
    popup_label = customtkinter.CTkLabel(master=popup, text="No lyrics found for this song.")
    popup_label.pack(pady=10)
    popup.focus()
    
        
def get_lyrics(textbox_lyrics,app):
    if current_song == None:
        show_popup_no_song(app)
    else:
        song = genius_object.search_song(song_name, artist_name)
        
        if song==None or song.lyrics==None:
            show_popup_no_lyrics(app)
        else:
            lyrics = delete_first_line(song.lyrics)
            textbox_lyrics.delete("0.0", "end")
            textbox_lyrics.insert("0.0", lyrics)
    
def audio_features(app, frame):
    if current_song == None:
        show_popup_no_song(app)
    else:
        features = spotify_object.audio_features(song_id)
        put_features_into_frame(frame, analise_features(features))
        
def analise_features(features):
    features_dict = {}

    for key, value in features[0].items():
        if key == 'mode':
            features_dict[key] = 'minor' if value == 0 else 'major'
        elif key == 'tempo':
            features_dict[key] = value
            break
        else:
            features_dict[key] = value
    return features_dict



def put_features_into_frame(frame, features):
    for widget in frame.winfo_children():
        widget.destroy()
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    row = 0

    # Display 'tempo' and 'loudness' as values
    if 'tempo' in features:
        tempo_label = customtkinter.CTkLabel(master=frame, text='Tempo (BPM)')
        tempo_label.grid(row=row, column=0, padx=10, pady=3,sticky="w")
        tempo_value = customtkinter.CTkLabel(master=frame, text=str(features['tempo']))
        tempo_value.grid(row=row, column=1, padx=10, pady=3,sticky="w")
        row += 1

    if 'loudness' in features:
        loudness_label = customtkinter.CTkLabel(master=frame, text='Loudness (dB)')
        loudness_label.grid(row=row, column=0, padx=10, pady=3,sticky="w")
        loudness_value = customtkinter.CTkLabel(master=frame, text=str(features['loudness']))
        loudness_value.grid(row=row, column=1, padx=10, pady=3, sticky="w")
        row += 1

    # Define color mapping for feature names
    color_mapping = {
        'danceability': 'green',
        'energy': 'blue',
        'speechiness': 'orange',
        'acousticness': 'lightblue',
        'instrumentalness': 'purple',
        'liveness': 'red',
        'valence': 'pink'
    }

    # Display other feature bars with corresponding colors
    for feature_name, feature_value in features.items():
        if feature_name in ['mode', 'key', 'tempo', 'loudness']:
            continue  # Skip 'mode', 'key', 'tempo', and 'loudness' features
        else:
            label = customtkinter.CTkLabel(master=frame, text=feature_name)
            label.grid(row=row, column=0, padx=10, pady=3, sticky="w")
            progressbar = customtkinter.CTkProgressBar(master=frame, orientation='horizontal', width=100, height=10)
            progressbar.grid(row=row, column=1, padx=10, pady=3, sticky="w")
            progressbar.set(feature_value)
            color = color_mapping.get(feature_name, 'gray')  # Default to gray if no color mapping is found
            progressbar.configure(progress_color=color)
            row += 1

    
    

def audio_analysis(app,frame):
    for widget in frame.winfo_children():
        widget.destroy()
        
    if current_song == None:
        show_popup_no_song(app)
    else:
        analysis = spotify_object.audio_analysis(song_id)
        put_results_into_frame(frame,analyze_audio_analysis(analysis))
        
def analyze_audio_analysis(audio_analysis):
    results = {}
    
    # Extract relevant information
    sections = audio_analysis['sections']
    bars = audio_analysis['bars']
    beats = audio_analysis['beats']
    segments = audio_analysis['segments']
    tempo = audio_analysis['track']['tempo']
    key = audio_analysis['track']['key']
    mode = audio_analysis['track']['mode']
    
    # Analyze sections
    num_sections = len(sections)
    average_section_duration = sum(section['duration'] for section in sections) / num_sections
    
    # Analyze bars
    num_bars = len(bars)
    average_bars_duration = sum(bar['duration'] for bar in bars) / num_bars
    
    # Analyze beats
    num_beats = len(beats)
    average_beats_duration = sum(beat['duration'] for beat in beats) / num_beats
    
    # Analyze segments
    num_segments = len(segments)
    average_segment_loudness = sum(segment['loudness_max'] for segment in segments) / num_segments
    
    # Analyze key and mode
    key_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][key]
    mode_name = 'Major' if mode == 1 else 'Minor'
    
    # Populate the results dictionary
    results['Number of Sections'] = num_sections
    results['Average Section Duration'] = f"{average_section_duration:.2f} seconds"
    results['Number of Bars'] = num_bars
    results['Average Bar Duration'] = f"{average_bars_duration:.2f} seconds"
    results['Number of Beats'] = num_beats
    results['Average Beat Duration'] = f"{average_beats_duration:.2f} seconds"
    results['Number of Segments'] = num_segments
    results['Key'] = key_name
    results['Mode'] = mode_name
    
    return results

def put_results_into_frame(frame, results):
    for widget in frame.winfo_children():
        widget.destroy()

    row = 0
    for key, value in results.items():
        label = customtkinter.CTkLabel(master=frame, text=key)
        label.grid(row=row, column=0, padx=10, pady=3, sticky="w")

        value_label = customtkinter.CTkLabel(master=frame, text=value)
        value_label.grid(row=row, column=1, padx=10, pady=3, sticky="w")

        row += 1
    
def delete_first_line(text):
    lines = text.splitlines()
    if len(lines) > 1:
        # Remove the first line
        lines = lines[1:]
    # Join the remaining lines back into a string
    result = '\n'.join(lines)
    result = re.sub(r'\d+Embed$', '', result)
    return result.strip()

def recommendations(app,frame):
    for widget in frame.winfo_children():
        widget.destroy()
    
    #recently_played()    
    recs = spotify_object.recommendations(seed_tracks=recently_played())
    print (recs)
    print(recommendations = recs['tracks']['title']['artist'])
        
def recently_played():
    recent_tracks = spotify_object.current_user_recently_played(5)
    recent_tracks_ids = [track['track']['id'] for track in recent_tracks['items']]
    #print (recent_tracks_ids)
    
