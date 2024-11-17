import yt_dlp as youtube_dl
import os
import urllib.request
import image_handler
import error_handler
import tagging
import file_handler

def download_image(image_url, save_path):
    try:
        directory_path = os.path.dirname(save_path)
        file_handler.create_directory_if_not_exists(directory_path)
        urllib.request.urlretrieve(image_url, save_path)
        image_handler.crop_to_square(save_path)
        print(f"Image downloaded to {save_path}")
        return save_path
    except Exception as e:
        error_handler.handle_error(f"Failed to download image: {e}, image_url: {image_url}")
        return None

def download_media(thumbnail_link, video_url, title, download_type, temp_path='./temp'):
    print(thumbnail_link, video_url, title, download_type)
    thumbnail_path = download_image(thumbnail_link, f"{temp_path}/{file_handler.clean_windows_file_name(title)}_thumbnail.jpg")
    ydl_opts = get_ydl_options(download_type, title, temp_path)
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            print(f"{download_type.capitalize()} downloaded successfully.")
    except Exception as e:
        error_handler.handle_error(f"Failed to download {download_type}: {e}")
    return thumbnail_path, f"{temp_path}/{title}.{download_type}"

def get_ydl_options(download_type, title, temp_path):
    if download_type == 'mp3':
        return {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
            'outtmpl': f'{temp_path}/{title}.%(ext)s'
        }
    elif download_type == 'mp4':
        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
            'outtmpl': f'{temp_path}/{title}.%(ext)s'
        }
    return {}

def start_download(download_type, video_title, video_thumbnail_link, video_link, video_author, output_path='./output'):
    thumbnail_path, directory = download_media(video_thumbnail_link, video_link, video_title, download_type)
    if download_type == 'mp3':
        tagging.tag_song(video_title, video_author, thumbnail_path, directory)
        file_handler.move_file(directory, f"{output_path}/{video_title}.{download_type}")
    elif download_type == 'mp4':
        file_handler.move_file(directory, f"{output_path}/{video_title}.{download_type}")

    # print(df)