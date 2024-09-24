import customtkinter as ctk
from tkinter import messagebox
import YoutubeInformation as yi
import Process as pr
import SearchFunc as sf
from CTkListbox import *
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

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
        self.search_entry.grid(pady=10, padx=(10, 5), row=0, column=0, columnspan=1, sticky="ew")

        self.search_button = ctk.CTkButton(self.search_frame, text="Search", command=self.search_video)
        self.search_button.grid(pady=10, padx=(5, 10), row=0, column=1)

        # Configure the grid layout for the frame to allow column resizing
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_frame.grid_columnconfigure(1, weight=0)

        # Search results display (listbox for multiple results)
        self.result_listbox = CTkListbox(self.search_frame, height=10, multiple_selection=True)
        self.result_listbox.grid(pady=10, padx=10, row=1, column=0, columnspan=2, sticky="nsew")

        # Configure row and column resizing for the result_listbox
        self.search_frame.grid_rowconfigure(1, weight=1)

        # Download type option
        self.download_type_var = ctk.StringVar(value="mp3")
        self.download_type_option = ctk.CTkOptionMenu(self.search_frame, variable=self.download_type_var, values=["mp3", "mp4"])
        self.download_type_option.grid(pady=10, padx=(10, 5), row=2, column=1, columnspan=1, sticky="ew")

        # Download button
        self.download_button = ctk.CTkButton(self.search_frame, text="Download", command=self.download_selected)
        self.download_button.grid(pady=10, padx=(5, 10), row=3, column=0, columnspan=2, sticky="ew")

        # Class attribute to store video_info DataFrame
        self.video_info = None


    def show_search_results(self):
        self.current_page = 0
        self.total_pages = (len(self.video_info) // self.page_size) + 1
        self.display_page(self.current_page)

    def display_page(self, page_num):
        self.result_listbox.delete(0, ctk.END)  # Clear the listbox
        start_idx = page_num * self.page_size
        end_idx = start_idx + self.page_size

        for index, row in self.video_info.iloc[start_idx:end_idx].iterrows():
            self.result_listbox.insert(ctk.END, f"{row['title']} by {row['author']}")

        self.update_buttons()

    def update_buttons(self):
        self.prev_button.configure(state=ctk.NORMAL if self.current_page > 0 else ctk.DISABLED)
        self.next_button.configure(state=ctk.NORMAL if self.current_page < self.total_pages - 1 else ctk.DISABLED)

    def show_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page(self.current_page)

    def show_next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page(self.current_page)

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
                self.video_info = pr.process_videos(video_urls)
                self.show_search_results()
            else:
                self.video_info = pr.process_videos([query])
                self.show_search_results()
        else:  # It's a search query
            video_urls = sf.search_youtube(query, api_key=API_KEY)
            self.video_info = pr.process_videos(video_urls)
            self.show_search_results()

    def show_search_results(self):
        if self.video_info is not None and not self.video_info.empty:
            for index, row in self.video_info.iterrows():
                # Insert title and author in the listbox
                self.result_listbox.insert(ctk.END, f"{row['title']} by {row['author']}")

    def download_selected(self):
        try:
            selected_indices = self.result_listbox.curselection()  # Get all selected item indices
            if not selected_indices:
                raise ValueError("No videos selected.")

            # Extract selected rows from video_info DataFrame based on selected indices
            selected_rows = self.video_info.iloc[list(selected_indices)]  # Select rows with multiple indices

            download_type = self.download_type_var.get()

            # Start download for all selected URLs
            pr.start_download(download_type, selected_rows)

            messagebox.showinfo(title="Download", message=f"{download_type.upper()} download completed!")  # Show success message
        except Exception as e:
            messagebox.showerror(title="Error", message=f"Failed to download: {e}")  # Show error message



if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
