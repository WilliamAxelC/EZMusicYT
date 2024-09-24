from pytube import YouTube, Playlist
import FileHandling as fh

def get_video_info(video_url):
    try:
        video = YouTube(video_url)
        video_title = fh.clean_windows_file_name(video.title)
        video_author = video.author
        video_thumbnail = video.thumbnail_url
        return video_title, video_author, video_thumbnail
    except Exception as e:
        print(f"Failed to get video info: {e}")
        return None, None, None

def get_playlist_videos(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        return playlist.video_urls
    except Exception as e:
        print(f"Failed to get videos in playlist: {e}")
        return []
