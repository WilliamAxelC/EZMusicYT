import yt_dlp as youtube_dl
import urllib
import FileHandling as fh
import ImageHandling as ih

def download_media(thumbnail_link, yt_url, title, download_type, temp_path='./temp'):
    thumbnail_path = download_thumbnail(thumbnail_link, title, temp_path)
    ydl_opts = get_ydl_options(download_type, title, temp_path)
    directory = f"{temp_path}/{download_type}"
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            fh.create_directory_if_not_exists(directory)
            ydl.download([yt_url])
            print(f"{download_type.capitalize()} downloaded successfully.")
    except Exception as e:
        print(f"Failed to download {download_type}: {e}")
    
    file_path = f"{directory}/{title}.{download_type}"

    return thumbnail_path, file_path

def get_ydl_options(download_type, title, temp_path):
    if download_type == 'mp3':
        return {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
            'outtmpl': f'{temp_path}/mp3/{title}.%(ext)s'
        }
    elif download_type == 'mp4':
        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
            'outtmpl': f'{temp_path}/mp4/{title}.%(ext)s'
        }
    return {}

def download_thumbnail(image_url, title, temp_path='./temp'):
    try:
        temp_path = f"{temp_path}/thumbnail/"
        fh.create_directory_if_not_exists(temp_path)
        thumbnail_path = f"{temp_path}{title}_thumbnail.jpg"
        urllib.request.urlretrieve(image_url, thumbnail_path)
        cropped_image = ih.crop_to_square(thumbnail_path)
        cropped_image.save(thumbnail_path)
        print(f"Thumbnail for '{title}' downloaded and cropped successfully.")
    except Exception as e:
        print(f"Failed to download thumbnail for '{title}': {e}")

    return thumbnail_path