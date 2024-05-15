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


