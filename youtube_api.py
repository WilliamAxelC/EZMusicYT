import os
import yt_dlp
import requests
import urllib
from ytmusicapi import YTMusic
from dotenv import load_dotenv
import error_handler
import file_handler

# Load environment variables
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

ytmusic = YTMusic()

# Add fallback to YOUTUBE_API_KEY2 if API_KEY is invalid
YOUTUBE_API_KEY2 = os.getenv("YOUTUBE_API_KEY2")

def fetch_video_details_with_api(video_url):
    """Fetches video details using the YouTube API as a fallback."""
    video_id = video_url.split("v=")[-1]
    video_info_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet&id={video_id}&key={API_KEY}"
    )

    try:
        response = requests.get(video_info_url)
        response.raise_for_status()
        items = response.json().get('items', [])
        if items:
            snippet = items[0]['snippet']
            title = file_handler.clean_windows_file_name(snippet['title'])
            author = snippet['channelTitle']
            thumbnail_url = snippet['thumbnails']['high']['url']
            return title, author, thumbnail_url
        else:
            error_handler.handle_error("No video details found in YouTube API response.")
            return None, None, None
    except requests.exceptions.RequestException as api_error:
        error_handler.log_error(api_error, "fetch_video_details_with_api - using API_KEY")
        # Fallback to the secondary API key
        print("Invalid API key detected. Falling back to YOUTUBE_API_KEY2.")
        return fetch_video_details_with_backup_key(video_id)

def fetch_video_details_with_backup_key(video_id):
    """Fetches video details using the backup YouTube API key."""
    video_info_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet&id={video_id}&key={YOUTUBE_API_KEY2}"
    )

    try:
        response = requests.get(video_info_url)
        response.raise_for_status()
        items = response.json().get('items', [])
        if items:
            snippet = items[0]['snippet']
            title = file_handler.clean_windows_file_name(snippet['title'])
            author = snippet['channelTitle']
            thumbnail_url = snippet['thumbnails']['high']['url']
            return title, author, thumbnail_url
        else:
            error_handler.handle_error("No video details found in YouTube API response using backup key.")
            return None, None, None
    except requests.exceptions.RequestException as api_error:
        error_handler.log_error(api_error, "fetch_video_details_with_backup_key")
        return None, None, None

def fetch_playlist_video_urls_with_api(playlist_url):
    """Fetches playlist video URLs using the YouTube API as a fallback."""
    playlist_id = playlist_url.split("list=")[-1]
    playlist_items_url = (
        f"https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=snippet&maxResults=50&playlistId={playlist_id}&key={API_KEY}"
    )
    video_urls = []
    try:
        while playlist_items_url:
            response = requests.get(playlist_items_url)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            video_urls.extend(
                [f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}" for item in items]
            )
            playlist_items_url = data.get('nextPageToken')
            if playlist_items_url:
                playlist_items_url = (
                    f"https://www.googleapis.com/youtube/v3/playlistItems"
                    f"?part=snippet&maxResults=50&pageToken={playlist_items_url}&playlistId={playlist_id}&key={API_KEY}"
                )
        return video_urls
    except requests.exceptions.RequestException as api_error:
        error_handler.log_error(api_error, "fetch_playlist_video_urls_with_api - using API_KEY")
        # Fallback to the secondary API key
        print("Invalid API key detected. Falling back to YOUTUBE_API_KEY2.")
        return fetch_playlist_video_urls_with_backup_key(playlist_id)

def fetch_playlist_video_urls_with_backup_key(playlist_id):
    """Fetches playlist video URLs using the backup YouTube API key."""
    playlist_items_url = (
        f"https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=snippet&maxResults=50&playlistId={playlist_id}&key={YOUTUBE_API_KEY2}"
    )
    video_urls = []
    try:
        while playlist_items_url:
            response = requests.get(playlist_items_url)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            video_urls.extend(
                [f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}" for item in items]
            )
            playlist_items_url = data.get('nextPageToken')
            if playlist_items_url:
                playlist_items_url = (
                    f"https://www.googleapis.com/youtube/v3/playlistItems"
                    f"?part=snippet&maxResults=50&pageToken={playlist_items_url}&playlistId={playlist_id}&key={YOUTUBE_API_KEY2}"
                )
        return video_urls
    except requests.exceptions.RequestException as api_error:
        error_handler.log_error(api_error, "fetch_playlist_video_urls_with_backup_key")
        return []


def search_on_youtube(query, api_key=API_KEY, max_results=10):
    """Searches for YouTube videos based on a query."""
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&maxResults={max_results}&q={urllib.parse.quote(query)}&type=video&key={api_key}"
    )
    try:
        response = requests.get(search_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        items = response.json().get('items', [])
        return [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in items]
    except requests.exceptions.RequestException as error:
        error_message = f"Error searching YouTube for '{query}': {error}"
        error_handler.handle_error(error_message)
        return []

def find_song_release(video_title, video_author, api_key=API_KEY, max_results=1):
    """Finds the official song release based on the video title and author."""
    query = f"{video_title} {video_author} official audio"
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&maxResults={max_results}&q={urllib.parse.quote(query)}"
        f"&type=video&videoCategoryId=10&key={api_key}"
    )
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        items = response.json().get('items', [])
        if items:
            return f"https://www.youtube.com/watch?v={items[0]['id']['videoId']}"
        else:
            error_handler.handle_error("No results found for the official audio.")
            return None
    except requests.exceptions.RequestException as error:
        error_message = f"Error searching for official song release: {error}"
        error_handler.handle_error(error_message)
        return None

def search_on_youtube_music(video_title, video_author, fallback_link, max_results=1):
    """Finds a song on YouTube Music based on the video title and author."""
    query = f"{video_title} {video_author} official audio"
    try:
        search_results = ytmusic.search(query=query, filter="songs", limit=max_results)
        if search_results:
            song = search_results[0]
            if 'videoId' in song:
                music_url = f"https://music.youtube.com/watch?v={song['videoId']}"
                print(f"Found song: {song['title']} by {song['artists'][0]['name']}")
                return music_url
            else:
                error_handler.handle_error(f"Video ID not found for '{video_title}' by {video_author}.")
        else:
            error_handler.handle_error(f"No results found for '{video_title}' by {video_author}.")
        return fallback_link
    except Exception as error:
        error_message = f"Error searching YouTube Music for '{video_title}': {error}"
        error_handler.log_error(error, context="search_on_youtube_music")
        # Fallback to YouTube search if YTMusic fails
        return search_on_youtube(video_title, api_key=API_KEY, max_results=max_results)
