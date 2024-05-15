import os
import yt_dlp as youtube_dl
import re

DOWNLOADS_DIR = '/app/downloads'


def save_uploaded_file(file) -> str:
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    file_path = os.path.join(DOWNLOADS_DIR, file.filename)
    file.save(file_path)
    return file_path


def download_video(source: str) -> str:
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    ydl_opts = {'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s')}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(source, download=True)
        video_file = ydl.prepare_filename(info_dict)

        safe_video_file = re.sub(r'[^A-Za-z0-9_\-./]', '_', video_file)
        safe_video_file_path = os.path.join(DOWNLOADS_DIR, safe_video_file)

        os.rename(video_file, safe_video_file_path)

        return safe_video_file_path
