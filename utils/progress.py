import os

from .config import BASE_FOLDER, OUTPUT_FOLDER, TEMP_FOLDER


def get_progress(job_id: str):
    job_path = os.path.join(BASE_FOLDER, TEMP_FOLDER, job_id)
    try:
        with open(os.path.join(job_path, "progress.log")) as f:
            return f.read().split('\n')[-1]
    except FileNotFoundError:
        if os.path.exists(os.path.join(BASE_FOLDER, OUTPUT_FOLDER, job_id+'.mp4')):
            return '100%: Done'
        if os.path.exists(job_path):
            return 'Processing...'
        return "Job not found"
