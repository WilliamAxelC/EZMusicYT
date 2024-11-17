import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
import os
from customtkinter import filedialog
from CTkListbox import *
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import youtube_api
import progress
import error_handler
import regex_filter
import data_handler
import download

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

class YouTubeDownloaderApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("600x400")

        self.output_directory = './output'
        self.song_release_var = ctk.StringVar(value="True")

        # Set the color theme of CustomTkinter
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        # Create search frame
        self.search_frame = ctk.CTkFrame(self, corner_radius=10)
        self.search_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Search input and button (side by side)
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search YouTube or input URL")
        self.search_entry.grid(pady=10, padx=(10, 5), row=0, column=0, columnspan=2, sticky="ew")

        self.search_button = ctk.CTkButton(self.search_frame, text="Search", command=self.search_video_thread)
        self.search_button.grid(pady=10, padx=(5, 10), row=0, column=2)

        # Configure the grid layout for the frame to allow column resizing
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_frame.grid_columnconfigure(1, weight=0)

        # Search results display (listbox for multiple results)
        self.result_listbox = CTkListbox(self.search_frame, height=10, multiple_selection=True, justify='left', hover_color='blue')
        self.result_listbox.grid(pady=10, padx=10, row=1, column=0, columnspan=3, sticky="nsew")

        # Configure row and column resizing for the result_listbox
        self.search_frame.grid_rowconfigure(1, weight=1)

        # Download type option
        self.download_type_var = ctk.StringVar(value="mp3")
        self.download_type_option = ctk.CTkOptionMenu(self.search_frame, variable=self.download_type_var, values=["mp3", "mp4"])
        self.download_type_option.grid(pady=10, padx=(10, 5), row=3, column=2, columnspan=1, sticky="ew")

        self.song_release_button = ctk.CTkCheckBox(self.search_frame, text="Query from YT Music?",
                                     variable=self.song_release_var, onvalue="True", offvalue="False", command=self.update_song_release_var)
        self.song_release_button.grid(pady=10, padx=(10, 5), row=3, column=0, columnspan=1, sticky="ew")

        self.output_directory_button = ctk.CTkButton(self.search_frame, text="Choose Output Directory", command=self.ask_output_directory)
        self.output_directory_button.grid(pady=10, padx=(5, 10), row=3, column=1, sticky="ew")

        # Download button
        self.download_button = ctk.CTkButton(self.search_frame, text="Download", command=self.download_selected_thread)
        self.download_button.grid(pady=10, padx=(5, 10), row=5, column=1, columnspan=2, sticky="ew")

        # Download All button
        self.download_all_button = ctk.CTkButton(self.search_frame, text="Download All", command=self.download_all_thread)
        self.download_all_button.grid(pady=10, padx=(5, 10), row=5, column=0, columnspan=1, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self.search_frame)
        self.progress_bar.grid(pady=10, padx=(5, 10), row=4, column=0, columnspan=3, sticky="ew")
        self.progress_bar.set(0)

        # Class attribute to store video_info DataFrame
        self.video_info = None

    def download_all_thread(self):
        """Start the download_all function in a new thread to avoid GUI freezing."""
        threading.Thread(target=self.download_all, daemon=True).start()

    def download_all(self):
        """Downloads all videos from the video_info DataFrame."""
        try:
            if not self.output_directory:
                raise ValueError("No output directory selected. Please choose a directory.")

            if self.video_info is None or self.video_info.empty:
                raise ValueError("No videos available to download.")

            if self.song_release_var.get() == "True":
                print("Getting song release data from YT Music.")
                self.video_info = data_handler.convert_df_to_song_release(self.video_info, API_KEY)

            download_type = self.download_type_var.get()

            row_count = len(self.video_info)
            for index, row in self.video_info.iterrows():
                # Use the correct column name for the thumbnail
                download.start_download(
                    download_type,
                    row['title'],
                    row['thumbnail'],  # Changed from 'thumbnail_link' to 'thumbnail'
                    row['link'],
                    row['author'],
                    self.output_directory
                )
                progress.update_progress_bar(self.progress_bar, index + 1, row_count)

            messagebox.showinfo("Download", f"All {download_type.upper()} downloads completed!")
        except Exception as e:
            error_handler.handle_error(f"Failed to download all: {e}")


    def select_all_thread(self):
        """Runs the select_all function in a separate thread."""
        threading.Thread(target=self.select_all, daemon=True).start()

    def deselect_all_thread(self):
        """Runs the deselect_all function in a separate thread."""
        threading.Thread(target=self.deselect_all, daemon=True).start()

    def select_all(self):
        """Selects all items in the result listbox concurrently."""
        total_items = self.result_listbox.size()
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(lambda i: self.result_listbox.selection_set(i), range(total_items))

    def deselect_all(self):
        """Deselects all items in the result listbox concurrently."""
        total_items = self.result_listbox.size()
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(lambda i: self.result_listbox.selection_clear(i), range(total_items))

    def update_song_release_var(self):
        """Method to handle changes to the song release checkbox."""
        print(f"Song release variable updated to: {self.song_release_var.get()}")

    def ask_output_directory(self):
        """Method to ask for the output directory."""
        self.output_directory = filedialog.askdirectory()
        if not self.output_directory:
            messagebox.showwarning("Warning", "No directory selected. Please select a directory.")
        else:
            messagebox.showinfo("Directory Selected", f"Files will be saved to: {self.output_directory}")

    def search_video_thread(self):
        """Start the search video function in a new thread to avoid GUI freezing."""
        threading.Thread(target=self.search_video, daemon=True).start()

    def search_video(self):
        query = self.search_entry.get()
        if not query:
            return

        # Clear previous results
        if self.result_listbox.size() > 0:
            self.result_listbox.delete(0, ctk.END)

        video_match, playlist_match = regex_filter.parse_youtube_url(query)

        if playlist_match:
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_match.group(1)}"
            video_urls = youtube_api.fetch_playlist_video_urls(playlist_url)

            if not video_urls:
                messagebox.showinfo("Info", "No videos found in the playlist.")
            else:
                self.video_info = data_handler.process_videos(video_urls)
                self.show_search_results()

        elif video_match:
            video_url = f"https://www.youtube.com/watch?v={video_match.group(1)}"
            self.video_info = data_handler.process_videos([video_url])
            self.show_search_results()

        else:
            video_urls = youtube_api.search_on_youtube(query, API_KEY)
            if self.song_release_var.get() == "True":
                video_urls = youtube_api.search_on_youtube_music(query, API_KEY)
            self.video_info = data_handler.process_videos(video_urls)
            self.show_search_results()

    def show_search_results(self):
        """Display search results in the listbox."""
        if self.video_info is not None and not self.video_info.empty:
            for index, row in self.video_info.iterrows():
                display_index = index + 1  # Display as 1-based for user readability
                title = f"{display_index}. {row['title']} by {row['author']}"
                title = self.truncate_text(title)
                self.result_listbox.insert(ctk.END, title)
        else:
            messagebox.showinfo("Info", "No results found.")


    def truncate_text(self, text, max_length=75):
        """Truncate the text to a fixed length and append '...' if it overflows."""
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        return text

    def download_selected_thread(self):
        """Start the download_selected function in a new thread to avoid GUI freezing."""
        threading.Thread(target=self.download_selected, daemon=True).start()

    def download_selected(self):
        try:
            if not self.output_directory:
                raise ValueError("No output directory selected. Please choose a directory.")

            selected_indices = self.result_listbox.curselection()
            if not selected_indices:
                raise ValueError("No videos selected.")

            # Extract selected rows from video_info DataFrame based on selected indices
            selected_rows = self.video_info.iloc[list(selected_indices)]

            if self.song_release_var.get() == "True":
                print("Getting song release data from YT Music.")
                selected_rows = data_handler.convert_df_to_song_release(selected_rows, API_KEY)

            download_type = self.download_type_var.get()

            if not selected_rows.empty:
                row_count = len(selected_rows)
                
                # Use ThreadPoolExecutor for concurrent downloading
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [
                        executor.submit(
                            download.start_download,
                            download_type,
                            row['title'],
                            row['thumbnail'],  # Changed from 'thumbnail_link' to 'thumbnail'
                            row['link'],
                            row['author'],
                            self.output_directory
                        )
                        for index, row in selected_rows.iterrows()
                    ]

                    for i, future in enumerate(as_completed(futures)):
                        try:
                            future.result()  # Ensures any exception is raised
                            progress.update_progress_bar(self.progress_bar, i + 1, row_count)
                        except Exception as e:
                            error_handler.handle_error(f"Failed to download {i + 1}: {e}")

                messagebox.showinfo("Download", f"Selected {download_type.upper()} downloads completed!")

        except Exception as e:
            error_handler.handle_error(f"Failed to download: {e}")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
