# EZMusicYT

**EZMusicYT** is a simple and intuitive graphical user interface (GUI) application built using Python’s `customtkinter` for downloading YouTube videos and music. This tool allows you to search for YouTube content, view results, and download videos or audio in MP4 or MP3 formats.

## Features

- **Search Functionality**: Input YouTube URLs, playlists, or search terms to fetch relevant results.
- **Video & Audio Downloads**: Supports downloading in MP3 (audio) or MP4 (video) formats.
- **Metadata Extraction**: Retrieve song metadata (such as album covers) from YouTube Music.
- **Progress Bar**: Provides visual feedback for the current download progress.
- **Custom Output Directory**: Choose where the downloaded files are saved.
- **Playlist Support**: Download videos from entire playlists.
- **Modern UI**: Built with `customtkinter`, the app has a sleek and responsive design with dark mode support.

## Requirements

- Python 3.x
- `customtkinter`
- `dotenv`
- `pandas`
- YouTube Data API v3

To install the required libraries, run:

```bash
pip install customtkinter python-dotenv pandas
```

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/EZMusicYT.git
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your YouTube API key:
   - Create a `.env` file in the root of the project directory and add your API key:
    
    ```bash
    API_KEY=your_youtube_api_key
    ```

## Usage

1. Run the application:

    ```bash
    python app.py
    ```

2. Enter a search query or YouTube URL in the search bar.
3. Choose a format (MP3/MP4), and optionally select the output directory.
4. Select the desired videos from the search results and click "Download".
5. Monitor the progress bar and wait for the download to complete.

## To-Do List

- [x] Search songs by category ID to retrieve album covers.
- [x] Add a progress bar for downloads.
- [ ] Implement asynchronous downloads to prevent GUI freezing.
- [ ] Add MP4 metadata tagging.
- [x] Input/output directory management.
- [x] Improve YouTube link detection.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
