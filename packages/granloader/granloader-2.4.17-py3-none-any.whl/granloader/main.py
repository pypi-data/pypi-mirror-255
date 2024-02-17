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

def monitor_download_progress(output_video, output_audio, video_info, folder_path):
    while True:
        video_size = os.path.getsize(output_video + ".part") / (1024 ** 2) if os.path.exists(output_video + ".part") else 0
        audio_size = os.path.getsize(output_audio + ".part") / (1024 ** 2) if os.path.exists(output_audio + ".part") else 0

        clear_output(wait=True)
        print(f"Nome do vídeo: {video_info['title']}\nResolução: {video_info['resolution']}")
        print(f"Vídeo: {video_size:.2f} MB\nÁudio: {audio_size:.2f} MB")

        # Saída da função se os downloads forem concluídos e os arquivos .part não existirem mais.
        if not os.path.exists(output_video + ".part") and not os.path.exists(output_audio + ".part"):
            final_output = os.path.join(folder_path, sanitize_filename(video_info['title']) + ".mp4")
            if os.path.exists(final_output):
                print(f"\nDownload e mesclagem concluídos. Arquivo final disponível em: {final_output}")
            else:
                print("\nAguardando a conclusão da mesclagem...")
            break

        time.sleep(1)

def start_download(link, extension, video_info):
    date_folder = datetime.now().strftime("%Y-%m-%d")
    folder_id = "DOWNLOADER"
    folder_path = f"/content/{folder_id}/{date_folder}"
    os.makedirs(folder_path, exist_ok=True)

    output_video = os.path.join(folder_path, "video_temp.mp4")
    output_audio = os.path.join(folder_path, "audio_temp.mp4")

    video_thread = threading.Thread(target=lambda: subprocess.run(["yt-dlp", "-f", "bestvideo[vcodec^=avc][ext=mp4]", "-o", output_video, link]), name="DownloadVideo")
    audio_thread = threading.Thread(target=lambda: subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", output_audio, link]), name="DownloadAudio")

    video_thread.start()
    audio_thread.start()

    monitor_thread = threading.Thread(target=monitor_download_progress, args=(output_video, output_audio, video_info, folder_path))
    monitor_thread.start()

    # Esperar pelo fim dos downloads antes de iniciar a mesclagem
    video_thread.join()
    audio_thread.join()

    # Mesclagem de áudio e vídeo
    cmd_merge = ["ffmpeg", "-i", output_video, "-i", output_audio, "-c", "copy", os.path.join(folder_path, sanitize_filename(video_info['title']) + ".mp4")]
    subprocess.run(cmd_merge)

    # Remover arquivos temporários
    os.remove(output_video)
    os.remove(output_audio)

def play_all():
    link_input = widgets.Text(description="Link da aula:")
    mp4_button = widgets.Button(description=".mp4")

    def on_button_click(button, extension):
        clear_output(wait=True)
        url = link_input.value
        if url:
            video_info = {
                'title': get_video_title(url),
                'resolution': str(get_video_info(url)) + "p",
                'upload_date': get_upload_date_and_time(url)[0]
            }
            print("Preparando para download...")
            start_download(url, extension, video_info)
        display(link_input, mp4_button)

    mp4_button.on_click(lambda b: on_button_click(b, '.mp4'))
    display(link_input, mp4_button)

play_all()