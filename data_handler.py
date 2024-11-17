import pandas as pd
import youtube_api
import tagging
import file_handler
import download
from concurrent.futures import ThreadPoolExecutor

def process_videos(video_urls):
    """Processes video details concurrently and returns a DataFrame."""
    df = pd.DataFrame(columns=['link', 'title', 'author', 'thumbnail'])

    def fetch_details(url):
        """Helper function to fetch video details."""
        video_title, video_author, video_thumbnail = youtube_api.fetch_video_details(url)
        # print(video_title, video_author, video_thumbnail)
        if video_title:
            return {
                "link": url,
                "title": video_title,
                "author": video_author,
                "thumbnail": video_thumbnail,
            }
        return None

    # Use ThreadPoolExecutor to fetch video details concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_details, video_urls))

    # Filter out None results and append them to the DataFrame
    valid_results = [res for res in results if res is not None]
    if valid_results:
        df = pd.DataFrame(valid_results)

    df.head()
    return df

def convert_df_to_song_release(video_info, api_key):
    """Converts DataFrame of video details to song release links and returns updated DataFrame."""
    new_links = []
    for index, row in video_info.iterrows():
        new_link = youtube_api.search_on_youtube_music(row['title'], row['author'], row['link'])
        if new_link:
            print(f"New link found: {new_link}")
            new_links.append(new_link)
        else:
            print(f"No song release found for {row['title']} by {row['author']}. Skipping.")

    # If there are valid links, process them; otherwise, return the original video_info
    if new_links:
        return process_videos(new_links)
    else:
        print("No new song releases found.")
        return video_info  # Return the original DataFrame if no new song releases are found
