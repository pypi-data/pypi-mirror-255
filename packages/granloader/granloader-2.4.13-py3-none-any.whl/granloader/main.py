import os
import subprocess
from datetime import datetime
import ipywidgets as widgets
from IPython.display import clear_output, display
import re
import json
import string
import threading
import time

def get_video_id(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|live/|.*&v=)?([^&=%\?]{11})')
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)
    return None

def get_upload_date_and_time(link):
    cmd = ["yt-dlp", "-j", link]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    video_info = json.loads(result.stdout)
    return video_info.get("upload_date"), video_info.get("timestamp")

def get_video_title(link):
    cmd = ["yt-dlp", "--get-title", link]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    return result.stdout.strip()

def get_video_info(link):
    cmd = ["yt-dlp", "-F", link]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    lines = result.stdout.split('\n')
    max_resolution = 0
    for line in lines:
        if "mp4" in line and "video" in line:
            match = re.search(r'(\d{3,4})x(\d{3,4})', line)
            if match:
                width, height = map(int, match.groups())
                max_resolution = max(max_resolution, height)
    return max_resolution

def sanitize_filename(title):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized_filename = ''.join(c for c in title if c in valid_chars)
    return sanitized_filename

def download_video(link, extension, display_progress=True):
    video_id = get_video_id(link)
    if not video_id:
        print("Link inválido.")
        return

    video_title = get_video_title(link)
    max_resolution = get_video_info(link)
    final_resolution = "1080p" if max_resolution <= 1080 else f"{max_resolution}p"
    upload_date, upload_time = get_upload_date_and_time(link)

    date_folder = datetime.now().strftime("%Y-%m-%d")
    folder_id = "DOWNLOADER"
    folder_path = f"./{folder_id}/{date_folder}"
    os.makedirs(folder_path, exist_ok=True)

    output_video = os.path.join(folder_path, "video.mp4")
    output_audio = os.path.join(folder_path, "audio.mp4")
    final_output = os.path.join(folder_path, sanitize_filename(video_title) + extension)

    def update_download_progress():
        nonlocal output_video, output_audio
        video_size = os.path.getsize(output_video) / (1024 ** 2) if os.path.exists(output_video) else 0
        audio_size = os.path.getsize(output_audio) / (1024 ** 2) if os.path.exists(output_audio) else 0
        clear_output(wait=True)
        print(f"Nome do vídeo: {video_title}\nResolução: {final_resolution}\nData de upload: {upload_date} - {upload_time}\nVídeo: {video_size:.2f} MB\nÁudio: {audio_size:.2f} MB")

    # Download video e audio
    cmd_video = ["yt-dlp", "-f", "bestvideo[vcodec^=avc][ext=mp4]", "-o", output_video, link]
    cmd_audio = ["yt-dlp", "-f", "bestaudio", "-o", output_audio, link]
    subprocess.Popen(cmd_video)
    subprocess.Popen(cmd_audio)

    if display_progress:
        while not os.path.exists(output_video) or not os.path.exists(output_audio):
            update_download_progress()
            time.sleep(1)

    # Merge audio e video
    cmd_merge = ["ffmpeg", "-i", output_video, "-i", output_audio, "-c", "copy", final_output]
    subprocess.run(cmd_merge)

    if os.path.exists(final_output):
        print(f"\nDownload e mesclagem concluídos. Arquivo final: {final_output}")
    else:
        print("\nErro na criação do arquivo final.")

def play_all():
    link_input = widgets.Text(description="Link da aula:")
    mp4_button = widgets.Button(description=".mp4")

    def on_button_click(button, extension):
        clear_output(wait=True)
        url = link_input.value
        if url:
            threading.Thread(target=download_video, args=(url, extension), kwargs={'display_progress': True}).start()
        display(link_input, mp4_button)

    mp4_button.on_click(lambda b: on_button_click(b, '.mp4'))
    display(link_input, mp4_button)

play_all()