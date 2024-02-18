import os
import re
import json
import time
import string
import threading
import subprocess
import ipywidgets as widgets
from google.colab import files
from datetime import datetime
from IPython.display import clear_output, display

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
  title = result.stdout.strip()
  return title

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

def monitor_download_progress(folder_path, title, resolution, download_ready_event):
  while not download_ready_event.is_set():
    video_file = find_latest_file("video", folder_path)
    audio_file = find_latest_file("audio", folder_path)
    video_size = os.path.getsize(video_file) / (1024 ** 2) if video_file else 0
    audio_size = os.path.getsize(audio_file) / (1024 ** 2) if audio_file else 0
    
    clear_output(wait=True)
    
    print(f"Nome: {title}")
    print(f"Resolução: {resolution}p")
    print(f"Vídeo: {video_size:.2f} MB")
    print(f"Áudio: {audio_size:.2f} MB")
    
    time.sleep(1)

  # Limpa a saída e exibe apenas o nome e a resolução quando o download está pronto
  clear_output(wait=True)
  print(f"Resolução: {resolution}p")
      
  time.sleep(1)

def start_download(link, folder_path):
    title = get_video_title(link)
    resolution = get_video_info(link)
    sanitized_title = sanitize_filename(title)
    extension = ".mp4"

    output_audio = os.path.join(folder_path, "audio_temp")
    output_video = os.path.join(folder_path, "video_temp")

    video_thread = threading.Thread(target=lambda: subprocess.run(["yt-dlp", "-f", "bestvideo[vcodec^=avc][ext=mp4]", "-o", output_video, link]), daemon=True)
    audio_thread = threading.Thread(target=lambda: subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", output_audio, link]), daemon=True)

    download_ready_event = threading.Event()

    video_thread.start()
    audio_thread.start()

    monitor_thread = threading.Thread(target=monitor_download_progress, args=(folder_path, title, resolution, download_ready_event), daemon=True)
    monitor_thread.start()

    video_thread.join()
    audio_thread.join()
    
    final_output = os.path.join(folder_path, sanitized_title + extension)
    print("\nMesclando arquivos e preparando para download.")
    cmd_merge = ["ffmpeg", "-i", output_video, "-i", output_audio, "-c", "copy", final_output]
    subprocess.run(cmd_merge)

    os.remove(output_video)
    os.remove(output_audio)

    download_ready_event.set()
    monitor_thread.join()

    if os.path.exists(final_output):
      clear_output()
      print(f"Iniciando download do arquivo final.")
      try:
        clear_output(wait=True)
        print("Este download pode demorar mais que o processo anterior.\n")
        print(f"Resolução: {resolution}p")
        files.download(final_output)
      except Exception as e:
        print(f"Erro no download do arquivo final: {e}")
    else:
      print("Erro: Arquivo não encontrado após download.")
    
    play_all()

def play_all():
  link_input = widgets.Text(description="Link da aula:")
  mp4_button = widgets.Button(description=".mp4")

  def on_button_click(button):
    clear_output(wait=True)
    url = link_input.value
    if url:
      date_folder = datetime.now().strftime("%Y-%m-%d")
      folder_id = "DOWNLOADER"
      folder_path = f"/content/{folder_id}/{date_folder}"
      os.makedirs(folder_path, exist_ok=True)
      clear_output(wait=True)

      print("Iniciando.\nPor favor, aguarde...")

      # Inicia o processo de download para o novo vídeo
      start_download(url, folder_path)
  
  mp4_button.on_click(on_button_click)
  display(link_input, mp4_button)
