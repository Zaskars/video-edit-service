from celery import Celery, chain
import yt_dlp as youtube_dl
import os
import re
import uuid
import time
import subprocess

app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

DOWNLOADS_DIR = '/app/downloads'
OUTPUT_DIR = '/app/output'

for directory in [DOWNLOADS_DIR, OUTPUT_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)


@app.task(bind=True)
def process_video_task(self, video_file: str) -> dict:
    self.update_state(state='PROGRESS', meta={'status': 'Processing video...'})
    try:
        unique_filename = f'{uuid.uuid4()}.mp4'
        output_file = os.path.join(OUTPUT_DIR, unique_filename)
        cmd = f'ffmpeg -y -i "{video_file}" "{output_file}"'
        subprocess.run(cmd, shell=True, check=True)
        return {'status': 'Completed', 'output_file': unique_filename}
    except subprocess.CalledProcessError as e:
        return {'status': 'Failed', 'error': str(e)}


@app.task(bind=True)
def download_video_task(self, source: str) -> str:
    self.update_state(state='PROGRESS', meta={'status': 'Downloading video...'})
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    ydl_opts = {'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s')}

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(source, download=True)
            video_file = ydl.prepare_filename(info_dict)

            safe_video_file = re.sub(r'[^A-Za-z0-9_\-./]', '_', video_file)
            safe_video_file_path = os.path.join(DOWNLOADS_DIR, safe_video_file)

            os.rename(video_file, safe_video_file_path)

            return safe_video_file_path
    except Exception as e:
        return str(e)


@app.task
def cleanup_task():
    now = time.time()
    cutoff = now - 120  # 2 минуты
    for directory in [DOWNLOADS_DIR, OUTPUT_DIR]:
        files = os.listdir(directory)
        for filename in files:
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_creation_time = os.path.getctime(file_path)
                if file_creation_time < cutoff:
                    os.remove(file_path)


app.conf.beat_schedule = {
    'cleanup-task-every-2-minutes': {
        'task': 'tasks.cleanup_task',
        'schedule': 120.0,
    },
}
