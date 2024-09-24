import pandas as pd
import DownloadHandling as dh
import SongTagging as st
import FileHandling as fh
import YoutubeInformation as yi

def process_videos(video_urls):
    df = pd.DataFrame(columns=['link', 'title', 'author', 'thumbnail'])
    for url in video_urls:
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


