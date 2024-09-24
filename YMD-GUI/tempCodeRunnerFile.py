import customtkinter as ctk
from tkinter import messagebox
import YoutubeInformation as yi
import Process as pr
import SongTagging as st
import SearchFunc as sf
from CTkListbox import *

API_KEY = "AIzaSyDPObuRmFk_q_FLCFrDl_OESjbJ28hl63o"

class YouTubeDownloaderApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("600x400")

        # Set the color theme of CustomTkinter
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Create search frame
        self.search_frame = ctk.CTkFrame(self, corner_radius=10)
        self.search_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Search input and button (side by side)
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search YouTube or input URL")
        self.search_entry.grid(pady=10, padx=(10, 5), row=0, column=0, columnspan=1, sticky="ew")  # Adjust padding for spacing

        self.search_button = ctk.CTkButton(self.search_frame, text="Search", command=self.search_video)
        self.search_button.grid(pady=10, padx=(5, 10), row=0, column=1)  # Adjust padding for spacing

        # Configure the grid layout for the frame to allow column resizing
        self.search_frame.grid_columnconfigure(0, weight=1)  # Ensure the entry box resizes with the window
        self.search_frame.grid_columnconfigure(1, weight=0)  # The button will remain the same size

        # Search results display (listbox for multiple results)
        self.result_listbox = CTkListbox(self.search_frame, height=10, multiple_selection=True)
        self.result_listbox.grid(pady=10, padx=10, row=1, column=0, columnspan=2, sticky="nsew")  # Using grid

        # Configure row and column resizing for the result_listbox
        self.search_frame.grid_rowconfigure(1, weight=1)  # Allow the listbox to expand

        # Download type option
        self.download_type_var = ctk.StringVar(value="mp3")
        self.download_type_option = ctk.CTkOptionMenu(self.search_frame, variable=self.download_type_var, values=["mp3", "mp4"])
        self.download_type_option.grid(pady=10, padx=(10, 5), row=2, column=1, columnspan=1, sticky="ew")  # Using grid

        # Allow the column where download_type_option is located to expand more
        # self.search_frame.grid_columnconfigure(0, weight=2)  # Allow more space for the download_type_option
        # self.search_frame.grid_columnconfigure(1, weight=1)  # Keep the download button smaller

        # Download button
        self.download_button = ctk.CTkButton(self.search_frame, text="Download", command=self.download_selected)
        self.download_button.grid(pady=10, padx=(5, 10), row=3, column=0, columnspan=2, sticky="ew")  # Using grid

    def search_video(self):
        query = self.search_entry.get()
        if not query:
            return

        # Clear previous results
        self.result_listbox.delete(0, ctk.END)

        if "youtube.com" in query:  # It's a URL
            if "playlist?list=" in query:
                video_urls = yi.get_playlist_videos(query)
                if not video_urls:
                    print("No videos found in playlist.")
                video_info = pr.process_videos([video_urls])
                self.show_search_results(video_info['title'])
            else:
                video_title, video_author, _ = yi.get_video_info(query)
                if video_title:
                    self.result_listbox.insert(ctk.END, f"{video_title} by {video_author}")
                    self.result_listbox.insert(ctk.END, query)
        else:  # It's a search query
            video_urls = sf.search_youtube(query, api_key=API_KEY)
            self.show_search_results(video_urls)

    def show_search_results(self, video_urls):
        for url in video_urls:
            video_title, video_author, _ = yi.get_video_info(url)
            if video_title:
                self.result_listbox.insert(ctk.END, f"{video_title} by {video_author}")
                self.result_listbox.insert(ctk.END, url)

    def download_selected(self):
        try:
            selected = self.result_listbox.get(ctk.ACTIVE)  # Get the selected item
            print(selected)

            # Check if the selected item is a URL
            if "youtube.com" in selected:
                url = selected
            else:
                # If the current selection isn't a URL, try getting the next item (URL)
                current_selection_index = self.result_listbox.curselection()
                if current_selection_index:
                    next_index = current_selection_index[0] + 1  # Assume the URL is in the next line
                    url = self.result_listbox.get(next_index)
                else:
                    raise ValueError("No valid video selected.")

            download_type = self.download_type_var.get()
            pr.process_videos([url], download_type)

            messagebox.showinfo(title="Download", message=f"{download_type.upper()} download completed!")  # Show success message
        except Exception as e:
            messagebox.showerror(title="Error", message=f"Failed to download: {e}")  # Show error message


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
