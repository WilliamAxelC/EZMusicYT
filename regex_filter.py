import re

def parse_youtube_url(query):
    youtube_video_regex = r"(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)|.*[?&]v=)|youtu\.be/)([^\"&?/ ]{11})"
    youtube_playlist_regex = r"(?:youtube\.com/(?:playlist|watch).*[?&]list=)([a-zA-Z0-9_-]+)"
    video_match = re.search(youtube_video_regex, query)
    playlist_match = re.search(youtube_playlist_regex, query)
    return video_match, playlist_match
