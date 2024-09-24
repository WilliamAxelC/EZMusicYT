import requests
import urllib

def search_youtube(query, api_key, max_results=10):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults={max_results}&q={urllib.parse.quote(query)}&type=video&key={api_key}"
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get('items', [])
        return [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in results]
    else:
        print(f"Failed to fetch search results: {response.status_code}")
        return []
