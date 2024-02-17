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
import concurrent.futures

def get_video_id(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|live/|.*&v=)?([^&=%\?]{11})')
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)
    return None

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

def find_latest_file(startswith, folder_path):
    relevant_files = [f for f in os.listdir(folder_path) if f.startswith(startswith) and not f.endswith(".ytdl")]
    full_paths = [os.path.join(folder_path, f) for f in relevant_files]
    if not full_paths:
        return None
    latest_file = max(full_paths, key=os.path.getctime)
    return latest_file

def monitor_download_progress(output_video, output_audio, stop_event):
    while not stop_event.is_set():
        video_size = os.path.getsize(output_video) / (1024 ** 2) if os.path.exists(output_video) else 0
        audio_size = os.path.getsize(output_audio) / (1024 ** 2) if os.path.exists(output_audio) else 0
        clear_output(wait=True)
        print(f"Vídeo: {video_size:.2f} MB\nÁudio: {audio_size:.2f} MB")
        time.sleep(1)  # Atualiza a cada segundo
    print("Download concluído.")

def start_download(link, folder_path, video_info):
    extension = ".mp4"
    output_video = os.path.join(folder_path, "video_temp.mp4")
    output_audio = os.path.join(folder_path, "audio_temp.mp4")

    def download_video():
        subprocess.run(["yt-dlp", "-f", "bestvideo[vcodec^=avc][ext=mp4]", "-o", output_video, link])

    def download_audio():
        subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", output_audio, link])

    # Iniciar threads de download
    video_thread = threading.Thread(target=download_video)
    audio_thread = threading.Thread(target=download_audio)
    stop_event = threading.Event()

    video_thread.start()
    audio_thread.start()

    # Monitorar progresso
    monitor_thread = threading.Thread(target=monitor_download_progress, args=(output_video, output_audio, stop_event))
    monitor_thread.start()

    # Aguardar conclusão do download
    video_thread.join()
    audio_thread.join()
    stop_event.set()  # Indica que o download foi concluído

    # Mesclar vídeo e áudio
    final_output = os.path.join(folder_path, sanitize_filename(video_info['title']) + extension)
    subprocess.run(["ffmpeg", "-i", output_video, "-i", output_audio, "-c", "copy", final_output])

    # Limpar arquivos temporários
    os.remove(output_video)
    os.remove(output_audio)

    clear_output(wait=True)
    print(f"Download e mesclagem concluídos.\nArquivo final: {final_output}")

def play_all():
    link_input = widgets.Text(description="Link da aula:")
    mp4_button = widgets.Button(description=".MP4")

    def on_button_click(_):
        url = link_input.value
        if url:
            video_title = get_video_title(url)
            video_info = {'title': video_title, 'resolution': str(get_video_info(url)) + "p"}
            date_folder = datetime.now().strftime("%Y-%m-%d")
            folder_id = "DOWNLOADER"
            folder_path = f"/content/{folder_id}/{date_folder}"
            os.makedirs(folder_path, exist_ok=True)
            start_download(url, folder_path, video_info)

    mp4_button.on_click(on_button_click)
    display(link_input, mp4_button)