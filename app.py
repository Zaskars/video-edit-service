from flask import Flask, request, jsonify, send_from_directory, after_this_request
from tasks import process_video_task, download_video_task
from celery import chain
from utils import save_uploaded_file
import os

app = Flask(__name__)

OUTPUT_DIR = '/app/output'


@app.route('/upload_url', methods=['POST'])
def upload_video_url():
    source = request.form['source']

    try:
        task_chain = chain(download_video_task.s(source), process_video_task.s())
        task = task_chain.apply_async()
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return str(e), 400


@app.route('/upload_file', methods=['POST'])
def upload_video_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    try:
        video_file = save_uploaded_file(file)
        task = process_video_task.delay(video_file)
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return str(e), 400


@app.route('/status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = download_video_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state == 'SUCCESS':
        response = {'state': 'SUCCESS', 'status': 'Video processed.', 'output_file': task.info.get('output_file', '')}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'status': task.info.get('status', '')}
    else:
        response = {'state': task.state, 'status': str(task.info)}

    return jsonify(response)


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    @after_this_request
    def remove_file(response):
        try:
            os.remove(os.path.join(OUTPUT_DIR, filename))
        except Exception as error:
            app.logger.error("Error removing or closing downloaded file handle", error)
        return response

    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
