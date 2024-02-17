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

def monitor_download_progress(folder_path, video_info, future_video, future_audio):
  while True:
        time.sleep(1)  # Diminui a frequência de atualização para cada segundo
        video_file = find_latest_file("video", folder_path)
        audio_file = find_latest_file("audio", folder_path)
        if video_file:
            video_size = os.path.getsize(video_file) / (1024 ** 2)  # Converte para MB
        else:
            video_size = 0
        if audio_file:
            audio_size = os.path.getsize(audio_file) / (1024 ** 2)  # Converte para MB
        else:
            audio_size = 0
        clear_output(wait=True)
        print(f"Nome do vídeo: {video_info['title']}\nResolução: {video_info['resolution']}\nVídeo: {video_size:.2f} MB\nÁudio: {audio_size:.2f} MB")

        # Encerra a thread se os downloads estiverem completos
        if not any([future_video.running(), future_audio.running()]):
            break

def start_download(link, folder_path, video_info):
  extension = ".mp4"

  output_video = os.path.join(folder_path, "video_temp.mp4")
  output_audio = os.path.join(folder_path, "audio_temp.mp4")

  def download_video():
    subprocess.run(["yt-dlp", "-f", "bestvideo[vcodec^=avc][ext=mp4]", "-o", output_video, link])

  def download_audio():
    subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", output_audio, link])

  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    future_video = executor.submit(download_video)
    future_audio = executor.submit(download_audio)

    # Inicia a thread de monitoramento em paralelo
    threading.Thread(target=monitor_download_progress, args=(folder_path, video_info)).start()

    # Espera os dois concluirem
    concurrent.futures.wait([future_video, future_audio], return_when=concurrent.futures.ALL_COMPLETED)

    # Merge depois do download
    final_output = os.path.join(folder_path, sanitize_filename(video_info['title']) + extension)
    subprocess.run(["ffmpeg", "-i", output_video, "-i", output_audio, "-c", "copy", final_output])

    # Limpar arquivos temporários
    if os.path.exists(output_video):
      os.remove(output_video)
    if os.path.exists(output_audio):
      os.remove(output_audio)

    if os.path.exists(final_output):
      clear_output(wait=True)
      print(f"\nConcluído!\nArquivo final disponível em: {final_output}\n")
    else:
      print("\nErro na criação do arquivo final.")

def play_all():
  link_input = widgets.Text(description="Link da aula:")
  mp4_button = widgets.Button(description=".mp4")

  def on_button_click(button):
    clear_output(wait=True)  # Limpa a saída para remover informações antigas
    url = link_input.value
    if url:
      # Reiniciar informações do vídeo
      video_info = {
        'title': get_video_title(url),
        'resolution': str(get_video_info(url)) + "p",
      }
      date_folder = datetime.now().strftime("%Y-%m-%d")
      folder_id = "DOWNLOADER"
      folder_path = f"/content/{folder_id}/{date_folder}"
      os.makedirs(folder_path, exist_ok=True)
      clear_output(wait=True)

      print("Iniciando download. Por favor, aguarde...")

      # Inicia o processo de download para o novo vídeo
      start_download(url, folder_path, video_info)
        
      # Redefine a interface para estar pronta para um novo input após o download
      display(link_input, mp4_button)
  
  mp4_button.on_click(on_button_click)
  display(link_input, mp4_button)
