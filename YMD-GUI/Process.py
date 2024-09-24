import pandas as pd
import DownloadHandling as dh
import SongTagging as st
import FileHandling as fh
import YoutubeInformation as yi
import SearchFunc as sf

def process_videos(video_urls):
    df = pd.DataFrame(columns=['link', 'title', 'author', 'thumbnail'])
    for url in  video_urls:
        video_title, video_author, video_thumbnail = yi.get_video_info(url)
        if not video_title:
            continue
        video_data = pd.DataFrame({
            "link": [url],
            "title": [video_title],
            "author": [video_author],
            "thumbnail_link": [video_thumbnail],
        })
        
        df = pd.concat([df, video_data], ignore_index=True)

    
    return df

def start_download(download_type, video_title, video_thumbnail_link, video_link, video_author, output_path='./output'):
    thumbnail_path, directory = dh.download_media(video_thumbnail_link, video_link, video_title, download_type)
    if download_type == 'mp3':
        st.tag_song(video_title, video_author, thumbnail_path, directory)
        fh.move_file(directory, f"{output_path}/{video_title}.{download_type}")
    elif download_type == 'mp4':
        fh.move_file(directory, f"{output_path}/{video_title}.{download_type}")

    # print(df)

def convert_df_to_song_release(video_info, api_key):
    new_links = []
    for index, row in video_info.iterrows():
        new_link = sf.get_song_release_ytm(row['title'], row['author'])
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

        


