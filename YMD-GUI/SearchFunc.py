import requests
import urllib
from ytmusicapi import YTMusic

ytmusic = YTMusic()

def search_youtube(query, api_key, max_results=10):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults={max_results}&q={urllib.parse.quote(query)}&type=video&key={api_key}"
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get('items', [])
        return [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in results]
    else:
        print(f"Failed to fetch search results: {response.status_code}")
        return []

def get_song_release(video_title, video_author, api_key, max_results=1):
    # Create a query string that is URL safe
    query = f"{video_title} {video_author} official audio"
    safe_query = urllib.parse.quote(query)  # URL-encode the query
    
    # Construct the search URL
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults={max_results}&q={safe_query}&type=video&videoCategoryId=10&key={api_key}"
    
    # Make the request to the YouTube API
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get('items', [])
        # Return the first link if found, otherwise None
        if results:
            return f"https://www.youtube.com/watch?v={results[0]['id']['videoId']}"
        else:
            print("No results found.")
            return None
    else:
        print(f"Failed to fetch search results: {response.status_code}")
        return None
    
from ytmusicapi import YTMusic
import urllib

ytmusic = YTMusic()

def get_song_release_ytm(video_title, video_author, max_results=1):
    # Create a query string with the video title and author
    query = f"{video_title} {video_author} official audio"
    
    # Search on YouTube Music using the YTMusic API
    search_results = ytmusic.search(query=query, filter="songs", limit=max_results)
    
    if search_results:
        # Filter to get the first result
        song = search_results[0]
        video_id = song['videoId']
        
        # Construct the YouTube Music link
        music_url = f"https://music.youtube.com/watch?v={video_id}"
        
        print(f"Found song: {song['title']} by {song['artists'][0]['name']}")
        return music_url
    else:
        print(f"No results found for {video_title} by {video_author}")
        return None

    



