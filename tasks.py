import time

from celery import Celery
import subprocess
import os
import uuid

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
