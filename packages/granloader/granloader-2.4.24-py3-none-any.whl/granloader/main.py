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

def find_latest_file(startswith, folder_path):
    relevant_files = [f for f in os.listdir(folder_path) if f.startswith(startswith) and not f.endswith(".ytdl")]
    full_paths = [os.path.join(folder_path, f) for f in relevant_files]
    if not full_paths:
        return None
    latest_file = max(full_paths, key=os.path.getctime)
    return latest_file

def monitor_download_progress(folder_path, video_info):
    while True:
        video_file = find_latest_file("video", folder_path)
        audio_file = find_latest_file("audio", folder_path)
        video_size = os.path.getsize(video_file) / (1024 ** 2) if video_file and os.path.exists(video_file) else 0
        audio_size = os.path.getsize(audio_file) / (1024 ** 2) if audio_file and os.path.exists(audio_file) else 0

        clear_output(wait=True)
        print(f"Nome do vídeo: {video_info['title']}\nResolução: {video_info['resolution']}\nVídeo: {video_size:.2f} MB\nÁudio: {audio_size:.2f} MB")

        # Verifica se os threads de download ainda estão ativos
        if threading.active_count() <= 2:
            break
        time.sleep(1)

def start_download(link, folder_path, video_info):
    extension = ".mp4"

    output_video = os.path.join(folder_path, "video_temp")
    output_audio = os.path.join(folder_path, "audio_temp")

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
    cmd_merge = ["ffmpeg", "-i", output_video, "-i", output_audio, "-c", "copy", final_output]
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
    mp4_button = widgets.Button(description=".MP4")

   def on_button_click(button):
    clear_output(wait=True)  # Limpa a saída para remover informações antigas
    url = link_input.value
    if url:
        # Reiniciar informações do vídeo
        video_info = {
            'title': get_video_title(url),
            'resolution': str(get_video_info(url)) + "p",
            'upload_date': get_upload_date_and_time(url)[0],
        }
        date_folder = datetime.now().strftime("%Y-%m-%d")
        folder_id = "DOWNLOADER"
        folder_path = f"/content/{folder_id}/{date_folder}"
        os.makedirs(folder_path, exist_ok=True)
        
        # Inicia o processo de download para o novo vídeo
        start_download(url, folder_path, video_info)
        
        # Redefine a interface para estar pronta para um novo input após o download
        display(link_input, mp4_button)

mp4_button.on_click(on_button_click)