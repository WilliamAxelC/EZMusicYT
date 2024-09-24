import YoutubeInformation as yi
import Process as pr
import SongTagging as st
import SearchFunc as sf
import os
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_valid_download_type():
    """
    Prompts user to choose a valid download type (mp3 or mp4).
    """
    while True:
        download_type = input("Choose download type (mp3/mp4): ").strip().lower()
        if download_type in ["mp3", "mp4"]:
            return download_type
        elif download_type in ["0", 0]:
            break;
        else:
            print("Invalid choice. Please choose 'mp3' or 'mp4'.")

def choose_video(video_urls):
    print("\nTop 10 Search Results:")
    for i, url in enumerate(video_urls, start=1):
        video_title, video_author, _ = yi.get_video_info(url)
        if not video_title:
            continue
        print(f"{i}. {video_title} by {video_author}")

    while True:
        try:
            input_choice = int(input("\nChoose a video to download (1-10): "))
            if 1 <= input_choice <= len(video_urls):
                selected_url = video_urls[input_choice - 1]
                download_type = get_valid_download_type()  # Get valid download type
                video_info = pr.process_videos([selected_url])
                pr.start_download(download_type, video_info)
            elif input_choice == 0:
                break
            else:
                print("Please choose a valid number.")
        except ValueError:
            print("Please enter a valid number.")

def input_url(video_link):
    while True:
        if video_link in ['0', 0]:
            break
        try:
            video_title = yi.get_video_info(video_link)
            if not video_title:
                print("Failed to fetch video info. Try again.")
                continue
            download_type = get_valid_download_type()  # Get valid download type
            video_info = pr.process_videos([video_link])
            pr.start_download(download_type, video_info)
        except Exception as e:
            print(f"Invalid URL or error fetching video info: {e}. Try again.")
        
        break

def input_playlist(playlist_link):
    while True:
        if playlist_link in ["0", 0]:
            break
        if "youtube.com/playlist?list=" in playlist_link:
            try:
                video_urls = yi.get_playlist_videos(playlist_link)
                if not video_urls:
                    print("No videos found in playlist.")
                    continue
                download_type = get_valid_download_type()  # Get valid download type
                video_info = pr.process_videos([video_urls])
                pr.start_download(download_type, video_info)
                break
            except Exception as e:
                print(f"Error fetching playlist info: {e}. Try again.")
        else:
            print("Invalid YouTube Playlist URL. Try again.")

def main():
    while True:
        print("1. Search by Query\n2. Input a URL\n3. Input a Playlist\n0. Exit")
        choice = input(">> ")

        if choice == '0':
            break
        elif choice == '1':
            video_links = sf.search_youtube(input("Input Query: "), api_key=API_KEY)
            choose_video(video_links)
        elif choice == '2':
            input_url(input('Input YouTube link: '))
        elif choice == '3':
            input_playlist(input('Input Playlist link: '))

main()
