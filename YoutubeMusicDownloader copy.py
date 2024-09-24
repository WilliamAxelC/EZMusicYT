import os
import re
import urllib
import shutil
import requests
import pandas as pd
from PIL import Image
import yt_dlp as youtube_dl
from pytube import Playlist, YouTube
import eyed3
import customtkinter as ctk
from tkinter import messagebox, Listbox, MULTIPLE, END, StringVar

SCROLL_PAUSE_TIME = 3

def clean_windows_file_name(file_name):
    return re.sub(r'[\\/:"*?<>|]', '', file_name).strip()

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created successfully.")

def download_thumbnail(image_url, title):
    try:
        create_directory_if_not_exists("./temp/thumbnail")
        image_path = f"./temp/thumbnail/{title}_thumbnail.jpg"
        urllib.request.urlretrieve(image_url, image_path)
        cropped_image = crop_to_square(image_path)
        cropped_image.save(image_path)
        print(f"Thumbnail for '{title}' downloaded and cropped successfully.")
    except Exception as e:
        print(f"Failed to download thumbnail for '{title}': {e}")

def crop_to_square(image_path):
    try:
        image = Image.open(image_path)
        width, height = image.size
        size = min(width, height)
        left = (width - size) / 2
        top = (height - size) / 2
        right = (width + size) / 2
        bottom = (height + size) / 2
        return image.crop((left, top, right, bottom))
    except Exception as e:
        print(f"Failed to crop image: {e}")
        return Image.open(image_path)

def download_audio(yt_url, title):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': f'./temp/audio/{title}.%(ext)s',
        'N': 8
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            create_directory_if_not_exists("./temp/audio")
            ydl.download([yt_url])
            print("Audio downloaded successfully.")
    except Exception as e:
        print(f"Failed to download audio: {e}")

def download_video(yt_url, title):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'./temp/video/{title}.%(ext)s',
        'N': 8
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            create_directory_if_not_exists("./temp/video")
            ydl.download([yt_url])
            print("Video downloaded successfully.")
    except Exception as e:
        print(f"Failed to download video: {e}")

def execute_download(temp_thumbnail, temp_title, temp_link, download_type):
    download_thumbnail(temp_thumbnail, temp_title)
    if download_type == 'mp3':
        download_audio(temp_link, temp_title)
    elif download_type == 'mp4':
        download_video(temp_link, temp_title)
    print("Download Completed.")

def song_tag(temp_title, temp_author, temp_thumbnail):
    try:
        audiofile = eyed3.load(f"./temp/audio/{temp_title}.mp3")

        with open(f"./temp/thumbnail/{temp_title}_thumbnail.jpg", "rb") as image_file:
            imagedata = image_file.read()

        #remove preexisting images
        audioImageDescriptions = [audioImage.description for audioImage in audiofile.tag.images]
        for description in audioImageDescriptions:
            audiofile.tag.images.remove(description)

        audiofile.tag.images.set(3, imagedata, "image/jpeg", u"Cover")
        audiofile.tag.artist = temp_author
        audiofile.tag.title = temp_title
        audiofile.tag.save(max_padding=1)
        create_directory_if_not_exists("./output")
        shutil.move(f"./temp/audio/{temp_title}.mp3", f"./output/{temp_title}.mp3")
        print("Song Tagged and Moved to output folder.")
    except Exception as e:
        print(f"Failed to tag song: {e}")

def video_move(temp_title):
    try:
        create_directory_if_not_exists("./output")
        shutil.move(f"./temp/video/{temp_title}.mp4", f"./output/{temp_title}.mp4")
        print("Video moved to output folder.")
    except Exception as e:
        print(f"Failed to move video: {e}")

def get_video_info(video_url):
    try:
        video = YouTube(video_url)
        video_title = clean_windows_file_name(video.title)
        video_author = video.author
        video_thumbnail = video.thumbnail_url
        return video_title, video_author, video_thumbnail
    except Exception as e:
        print(f"Failed to get video info: {e}")
        return None, None, None

def get_videos_in_playlist(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        return playlist.video_urls
    except Exception as e:
        print(f"Failed to get videos in playlist: {e}")
        return []

def process_videos(video_urls, download_type):
    df = pd.DataFrame(columns=['link', 'title', 'author', 'thumbnail'])
    for url in video_urls:
        video_title, video_author, video_thumbnail = get_video_info(url)
        if not video_title:
            continue
        video_data = pd.DataFrame({
            "link": [url],
            "title": [video_title],
            "author": [video_author],
            "thumbnail": [video_thumbnail]
        })
        df = pd.concat([df, video_data], ignore_index=True)

    for index, row in df.iterrows():
        execute_download(row["thumbnail"], row["title"], row['link'], download_type)
        if download_type == 'mp3':
            song_tag(row["title"], row["author"], row["thumbnail"])
        elif download_type == 'mp4':
            video_move(row["title"])

    print(df)

def search_youtube(query):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=10&q={urllib.parse.quote(query)}&type=video&key={API_KEY}"
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get('items', [])
        video_urls = [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in results]
        return video_urls
    else:
        print(f"Failed to fetch search results: {response.status_code}")
        return []

def search_by_query(qu):
    query = input('Input your query: ')
    video_urls = search_youtube(query)
    if not video_urls:
        print("No videos found.")
        return

    print("\nTop 10 Search Results:")
    for i, url in enumerate(video_urls, start=1):
        video_title, video_author, _ = get_video_info(url)
        if not video_title:
            continue
        print(f"{i}. {video_title} by {video_author}")

    while True:
        try:
            input_choice = int(input("\nChoose a video to download (1-10): "))
            if 1 <= input_choice <= 10:
                selected_url = video_urls[input_choice - 1]
                download_type = input("Choose download type (mp3/mp4): ").strip().lower()
                process_videos([selected_url], download_type)
                break
            else:
                print("Please choose a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")

def input_url():
    while True:
        query = input('Input your URL: ')
        if query in ['0', 0]:
            break
        try:
            video_title, video_author, video_thumbnail = get_video_info(query)
            if not video_title:
                print("Failed to fetch video info. Try again.")
                continue
            download_type = input("Choose download type (mp3/mp4): ").strip().lower()
            process_videos([query], download_type)
            if download_type == 'mp3':
                song_tag(video_title, video_author, video_thumbnail)
            break
        except Exception as e:
            print(f"Invalid URL or error fetching video info: {e}. Try again.")

def input_playlist():
    while True:
        query = input("Input your Playlist's URL: ")
        if query in ["0", 0]:
            break
        if "youtube.com/playlist?list=" in query:
            try:
                video_urls = get_videos_in_playlist(query)
                if not video_urls:
                    print("No videos found in playlist.")
                    continue
                download_type = input("Choose download type (mp3/mp4): ").strip().lower()
                process_videos(video_urls, download_type)
                break
            except Exception as e:
                print(f"Error fetching playlist info: {e}. Try again.")
        else:
            print("Invalid Youtube Playlist URL. Try again.")

def main():
    while True:
        print("1. Search by Query\n2. Input a URL\n3. Input a Playlist\n0. Exit")
        choice = input(">> ")

        if choice == '0':
            break
        elif choice == '1':
            search_by_query()
        elif choice == '2':
            input_url()
        elif choice == '3':
            input_playlist()



class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("YouTube Music Downloader")
        self.geometry("600x400")
        
        # Define StringVar for entries
        self.query_var = StringVar()
        self.url_var = StringVar()
        self.playlist_var = StringVar()
        
        # Combobox for choosing input style
        self.input_style_var = StringVar(value="Search by Query")
        self.input_style_combobox = ctk.CTkComboBox(self, values=["Search by Query", "Input URL", "Input Playlist"], variable=self.input_style_var, command=self.combobox_callback)
        self.input_style_combobox.pack(pady=10)
        
        # Search by Query section
        self.query_label = ctk.CTkLabel(self, text="Search by Query:")
        self.query_entry = ctk.CTkEntry(self, textvariable=self.query_var)
        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_by_query)
        
        # Input a URL section
        self.url_label = ctk.CTkLabel(self, text="Input a URL:")
        self.url_entry = ctk.CTkEntry(self, textvariable=self.url_var)
        self.url_button = ctk.CTkButton(self, text="Download", command=self.input_url)
        
        # Input a Playlist section
        self.playlist_label = ctk.CTkLabel(self, text="Input a Playlist URL:")
        self.playlist_entry = ctk.CTkEntry(self, textvariable=self.playlist_var)
        self.playlist_button = ctk.CTkButton(self, text="Download", command=self.input_playlist)
        
        # Listbox to display search results
        self.result_listbox = Listbox(self, selectmode=MULTIPLE)
        
        # Initialize with the default input style
        self.update_input_style("Search by Query")

    def combobox_callback(self, choice):
        self.update_input_style(choice)
    
    def update_input_style(self, style):
        # Hide all input sections
        self.query_label.pack_forget()
        self.query_entry.pack_forget() 
        self.search_button.pack_forget()
        self.url_label.pack_forget()
        self.url_entry.pack_forget()
        self.url_button.pack_forget()
        self.playlist_label.pack_forget()
        self.playlist_entry.pack_forget()
        self.playlist_button.pack_forget()
        self.result_listbox.pack_forget()
        
        # Show the input section based on selected style
        if style == "Search by Query":
            self.query_label.pack(pady=5)
            self.query_entry.pack(pady=5)
            self.search_button.pack(pady=5)
        elif style == "Input URL":
            self.url_label.pack(pady=5)
            self.url_entry.pack(pady=5)
            self.url_button.pack(pady=5)
        elif style == "Input Playlist":
            self.playlist_label.pack(pady=5)
            self.playlist_entry.pack(pady=5)
            self.playlist_button.pack(pady=5)
        
        # Pack the result listbox
        self.result_listbox.pack(fill="both", expand=True, pady=5)

    def search_by_query(self, query):
        video_urls = search_youtube(query)
        if not video_urls:
            print("No videos found.")
            return

        print("\nTop 10 Search Results:")
        for i, url in enumerate(video_urls, start=1):
            video_title, video_author, _ = get_video_info(url)
            if not video_title:
                continue
            print(f"{i}. {video_title} by {video_author}")

        while True:
            try:
                input_choice = int(input("\nChoose a video to download (1-10): "))
                if 1 <= input_choice <= 10:
                    selected_url = video_urls[input_choice - 1]
                    download_type = input("Choose download type (mp3/mp4): ").strip().lower()
                    process_videos([selected_url], download_type)
                    break
                else:
                    print("Please choose a number between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")        
            pass

    def input_url(self):
        # Implementation of input_url method
        pass

    def input_playlist(self):
        # Implementation of input_playlist method
        pass

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
