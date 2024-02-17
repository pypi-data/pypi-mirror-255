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

def monitor_download_progress(folder_path, video_info):
    video_pattern = re.compile(r'video.*\.mp4$')
    audio_pattern = re.compile(r'audio.*\.mp4$')
    video_size, audio_size = 0, 0

    while True:
        video_files = [f for f in os.listdir(folder_path) if video_pattern.match(f)]
        audio_files = [f for f in os.listdir(folder_path) if audio_pattern.match(f)]

        video_size = sum(os.path.getsize(os.path.join(folder_path, f)) for f in video_files) / (1024 ** 2) if video_files else 0
        audio_size = sum(os.path.getsize(os.path.join(folder_path, f)) for f in audio_files) / (1024 ** 2) if audio_files else 0

        clear_output(wait=True)
        print(f"Nome do vídeo: {video_info['title']}\nResolução: {video_info['resolution']}\nVídeo: {video_size:.2f} MB\nÁudio: {audio_size:.2f} MB")

        # Verificar se os downloads foram concluídos
        if not video_files or not audio_files:
            print("\nAguardando o início dos downloads...")
        elif not any(".part" in f for f in os.listdir(folder_path)):
            print("\nDownloads concluídos, aguardando a mesclagem...")
            break

        time.sleep(1)

def start_download(link, extension, video_info):
    date_folder = datetime.now().strftime("%Y-%m-%d")
    folder_id = "DOWNLOADER"
    folder_path = f"/content/{folder_id}/{date_folder}"
    os.makedirs(folder_path, exist_ok=True)

    output_video = os.path.join(folder_path, "video_temp.mp4.part") # Alterado para incluir .part
    output_audio = os.path.join(folder_path, "audio_temp.mp4.part") # Alterado para incluir .part

    # Iniciar downloads
    video_thread = threading.Thread(target=lambda: subprocess.run(["yt-dlp", "-f", "bestvideo[vcodec^=avc][ext=mp4]", "-o", output_video, link]), name="DownloadVideo")
    audio_thread = threading.Thread(target=lambda: subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", output_audio, link]), name="DownloadAudio")

    video_thread.start()
    audio_thread.start()

    # Monitorar progresso
    monitor_thread = threading.Thread(target=monitor_download_progress, args=(folder_path, video_info))
    monitor_thread.start()

    video_thread.join()
    audio_thread.join()

    # Mesclagem dos arquivos
    final_output = os.path.join(folder_path, sanitize_filename(video_info['title']) + extension)
    cmd_merge = ["ffmpeg", "-i", output_video.replace(".part", ""), "-i", output_audio.replace(".part", ""), "-c", "copy", final_output]
    subprocess.run(cmd_merge)

    # Limpar
    os.remove(output_video)
    os.remove(output_audio)

    if os.path.exists(final_output):
        clear_output(wait=True)
        print(f"\nDownload e mesclagem concluídos. Arquivo final disponível em: {final_output}")
    else:
        print("\nErro na criação do arquivo final.")

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