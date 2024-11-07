import os
import sys
import yt_dlp
import instaloader
import requests
from bs4 import BeautifulSoup
import csv
import time
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen

# ---------------------------------
# Version and Update Variables
# ---------------------------------
CURRENT_VERSION = "v1.0.0"
UPDATE_URL = "https://api.github.com/repos/nayandas69/social-media-downloader/releases/latest"

# ---------------------------------
# Author Details
# ---------------------------------
def display_author_details():
    print("\033[1;34m" + "=" * 50 + "\033[0m")  # Blue line
    print("\033[1;32mSocial Media Downloader\033[0m")  # Green title
    print("\033[1;33mAuthor:\033[0m Nayan Das")  # Yellow label
    print("\033[1;33mEmail:\033[0m \033[4;36mnayanchandradas@hotmail.com\033[0m")  # Cyan email with underline
    print("\033[1;33mWebsite:\033[0m \033[4;36mhttps://socialportal.nayanchandradas.com\033[0m")  # Cyan website with underline
    print("\033[1;33mVersion:\033[0m " + CURRENT_VERSION)  # Display the current version
    print("\033[1;34m" + "=" * 50 + "\033[0m\n")  # Reset color
    time.sleep(1)

# Display author details at the start
display_author_details()

# Create media download directory if it doesn't exist
download_directory = 'media'
history_file = 'download_history.csv'
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Check for updates function
def check_for_updates():
    print(f"Current version: {CURRENT_VERSION}")
    print("Checking for updates...")
    try:
        response = requests.get(UPDATE_URL)
        response.raise_for_status()
        data = response.json()

        latest_version = data.get('tag_name')
        download_link = None
        if 'assets' in data and data['assets']:
            download_link = data['assets'][0].get('browser_download_url')

        if latest_version:
            if latest_version > CURRENT_VERSION:
                print(f"\nNew version available: {latest_version}")
                print(f"Current version: {CURRENT_VERSION}")
                changelog = data.get('body', 'No changelog available').strip()
                print("New features in this update:")
                print(changelog)
                confirm = input("Do you want to update to the latest version? (y/n): ")
                if confirm.lower() == 'y':
                    download_update(download_link, latest_version)
                else:
                    print("Thank you! You can update anytime when you want.\n")
            else:
                print("You are already using the latest version.\n")
        else:
            print("Error: Could not retrieve the latest version information.")
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Error checking for updates: {str(e)}")

# Download and install update, remove old version, and restart
def download_update(download_link, latest_version):
    if not download_link:
        print("Error: No download link available for the update.")
        return

    print("Downloading update...")
    update_file = "SocialMediaDownloader_latest.exe"

    # Download the latest version
    response = requests.get(download_link, stream=True)
    with open(update_file, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print("Update downloaded successfully.")
    
    # Remove the old version and replace it with the new one
    old_exe = sys.argv[0]
    new_exe = os.path.abspath(update_file)
    try:
        shutil.move(new_exe, old_exe)
        print("Old version removed and updated version applied.")
        print("Restarting with the latest version...\n")
        time.sleep(2)
        Popen([old_exe])  # Restart the updated version
        sys.exit()  # Exit the current instance
    except Exception as e:
        print(f"Failed to update: {str(e)}")

# Initialize download logging
def log_download(url, status, timestamp=None):
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(history_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([url, status, timestamp])

# YouTube and TikTok download with format selection
def download_youtube_or_tiktok_video(url):
    ydl_opts = {'listformats': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info['formats']

        print("\nAvailable formats:")
        for i, format in enumerate(formats):
            format_id = format['format_id']
            ext = format['ext']
            height = format.get('height', 'Unknown')
            fps = format.get('fps', 'Unknown')
            vcodec = format.get('vcodec', 'none')
            acodec = format.get('acodec', 'none')
            format_note = format.get('format_note', '')
            print(f"{i + 1}. {format_id} - {ext} - {height}p - {fps}fps - {vcodec} - {acodec} - {format_note}")

        choice = input("\nEnter the format ID to download (or type 'mp3' for best audio): ")

        if choice.lower() == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }
        else:
            ydl_opts = {
                'format': f'{choice}+bestaudio/best',
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s')
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                title = info.get("title", "video")
                log_download(url, "Success")
                print(f"\nDownloaded video: {title} with audio and video.")
                print("\nDownload complete! Thank you for using.")
        except Exception as e:
            log_download(url, f"Failed: {str(e)}")
            print(f"Error downloading video: {str(e)}")

# Instagram download
def download_instagram_post(url):
    try:
        L = instaloader.Instaloader()
        shortcode = url.split("/")[-2]
        L.download_post(instaloader.Post.from_shortcode(L.context, shortcode), target=download_directory)
        log_download(url, "Success")
        print(f"Downloaded Instagram post from {url}")
        print("\nDownload complete! Thank you for using.")
    except Exception as e:
        log_download(url, f"Failed: {str(e)}")
        print(f"Failed to download Instagram post: {str(e)}")

# Facebook download using BeautifulSoup to find video link
def download_facebook_video(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        video_url = soup.find('meta', property="og:video")['content']
        if video_url:
            video_response = requests.get(video_url)
            file_path = os.path.join(download_directory, 'facebook_video.mp4')
            with open(file_path, 'wb') as f:
                f.write(video_response.content)
            log_download(url, "Success")
            print("Downloaded Facebook video")
            print("\nDownload complete! Thank you for using.")
        else:
            print("Failed to find video URL")
    except Exception as e:
        log_download(url, f"Failed: {str(e)}")
        print(f"Failed to download Facebook video: {str(e)}")

# Batch download for multiple URLs
def batch_download(urls):
    print("Starting batch download...")
    with ThreadPoolExecutor() as executor:
        executor.map(download_media, urls)

# Function to display a help menu
def show_help():
    print("\n\033[1;36mHow to Use Social Media Downloader:\033[0m")
    print("1. \033[1;33mYouTube Download\033[0m: Enter '1' to download a YouTube video. Paste the URL when prompted.")
    print("2. \033[1;33mFacebook Download\033[0m: Enter '2' to download a Facebook video. Paste the URL when prompted.")
    print("3. \033[1;33mInstagram Download\033[0m: Enter '3' to download an Instagram post.")
    print("4. \033[1;33mTikTok Download\033[0m: Enter '4' to download a TikTok video.")
    print("5. \033[1;33mBatch Download\033[0m: Enter '5' to download multiple URLs at once.")
    print("6. \033[1;33mCheck for Updates\033[0m: Enter '6' to check for updates.")
    print("7. \033[1;33mHelp\033[0m: Enter '7' for help.")
    print("8. \033[1;33mExit\033[0m: Enter '8' to exit the program.")
    print("\nAll downloads are saved in the 'media' directory, and a log is saved in 'download_history.csv'.")
    print("If you encounter any issues, crashes, bugs, or have new feature requests, please contact the author:")
    display_author_details()

# Main download function with platform detection
def download_media(url):
    if 'youtube.com' in url or 'youtu.be' in url or 'tiktok.com' in url:
        download_youtube_or_tiktok_video(url)
    elif 'instagram.com' in url:
        download_instagram_post(url)
    elif 'facebook.com' in url:
        download_facebook_video(url)
    else:
        print(f"Unknown platform for URL: {url}")

# CLI interface for the downloader
def main():
    while True:
        print("\n\033[1;34mSelect the platform to download from:\033[0m")
        print("1. YouTube")
        print("2. Facebook")
        print("3. Instagram")
        print("4. TikTok")
        print("5. Batch Download")
        print("6. Check for Updates")
        print("7. Help")
        print("8. Exit")
        choice = input("Enter the number: ")

        if choice == '8':
            print("Exiting the downloader. Goodbye!")
            break
        elif choice == '7':
            show_help()
            continue  # Skip the "Download complete!" message for help
        elif choice == '6':
            check_for_updates()
        elif choice == '5':
            file_path = input("Enter the path to the text file containing URLs: ")
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            batch_download(urls)
        else:
            url = input("Enter the URL of the media: ")
            download_media(url)

if __name__ == '__main__':
    main()
