from flask import Flask, render_template_string, request, jsonify
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

app = Flask(__name__)


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

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EasyMusic</title>
        <style>
            body {
                background-color: #002B36;
                font-family: Arial, sans-serif;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                width: 80%;
                max-width: 1200px;
                margin: auto;
                background-color: #073642;
                border-radius: 8px;
                padding: 20px;
            }
            .header, .footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .header {
                margin-bottom: 20px;
            }
            .header h1, .footer h1 {
                font-size: 24px;
            }
            .search-bar {
                display: flex;
                align-items: center;
            }
            .search-bar input {
                padding: 10px;
                font-size: 16px;
                border: none;
                border-radius: 4px;
                margin-right: 10px;
            }
            .search-bar button {
                padding: 10px 20px;
                font-size: 16px;
                border: none;
                border-radius: 4px;
                background-color: #2AA198;
                color: white;
                cursor: pointer;
            }
            .content {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
            }
            .results, .selected {
                width: 48%;
                background-color: #586e75;
                border-radius: 8px;
                padding: 20px;
                box-sizing: border-box;
            }
            .results h2, .selected h2 {
                font-size: 20px;
                margin-bottom: 10px;
            }
            .video-item {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }
            .video-item img {
                width: 80px;
                height: 80px;
                margin-right: 10px;
            }
            .video-item button {
                margin-left: auto;
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
                background-color: #dc322f;
                color: white;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>EasyMusic</h1>
                <div class="search-bar">
                    <input type="text" id="query" placeholder="Search Query">
                    <button onclick="searchVideos()">Search</button>
                </div>
            </div>
            <div class="content">
                <div class="results">
                    <h2>Results:</h2>
                    <div id="results-list"></div>
                </div>
                <div class="selected">
                    <h2>Selected</h2>
                    <div id="selected-list"></div>
                </div>
            </div>
            <div class="footer">
                <button onclick="downloadSelected()">Download</button>
            </div>
        </div>
    
        <script>
            const resultsList = document.getElementById('results-list');
            const selectedList = document.getElementById('selected-list');
            let selectedVideos = [];
    
            function searchVideos() {
                const query = document.getElementById('query').value;
                fetch('/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query }),
                })
                .then(response => response.json())
                .then(data => {
                    resultsList.innerHTML = '';
                    data.forEach(video => {
                        const videoItem = document.createElement('div');
                        videoItem.classList.add('video-item');
                        videoItem.innerHTML = `
                            <img src="${video.thumbnail}" alt="${video.title}">
                            <div>
                                <div>${video.title}</div>
                                <div>${video.author}</div>
                            </div>
                            <button onclick="selectVideo('${video.link}', '${video.title}', '${video.author}', '${video.thumbnail}')">Select</button>
                        `;
                        resultsList.appendChild(videoItem);
                    });
                });
            }
    
            function selectVideo(link, title, author, thumbnail) {
                const selectedVideo = { link, title, author, thumbnail };
                selectedVideos.push(selectedVideo);
                updateSelectedList();
            }
    
            function updateSelectedList() {
                selectedList.innerHTML = '';
                selectedVideos.forEach((video, index) => {
                    const videoItem = document.createElement('div');
                    videoItem.classList.add('video-item');
                    videoItem.innerHTML = `
                        <img src="${video.thumbnail}" alt="${video.title}">
                        <div>
                            <div>${video.title}</div>
                            <div>${video.author}</div>
                        </div>
                        <button onclick="removeVideo(${index})">Remove</button>
                    `;
                    selectedList.appendChild(videoItem);
                });
            }
    
            function removeVideo(index) {
                selectedVideos.splice(index, 1);
                updateSelectedList();
            }
    
            function downloadSelected() {
                const downloadType = prompt('Choose download type (mp3/mp4)').trim().toLowerCase();
                fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ selected_videos: selectedVideos, download_type: downloadType }),
                })
                .then(response => response.json())
                .then(data => {
                    alert('Download complete');
                    selectedVideos = [];
                    updateSelectedList();
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    video_urls = search_youtube(query)
    video_info_list = []

    for url in video_urls:
        title, author, thumbnail = get_video_info(url)
        video_info_list.append({'link': url, 'title': title, 'author': author, 'thumbnail': thumbnail})

    return jsonify(video_info_list)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    selected_videos = data.get('selected_videos', [])
    download_type = data.get('download_type')

    for video in selected_videos:
        execute_download(video['thumbnail'], video['title'], video['link'], download_type)
        if download_type == 'mp3':
            song_tag(video['title'], video['author'], video['thumbnail'])
        elif download_type == 'mp4':
            video_move(video['title'])

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
