import os
import threading
import time

from .config import BASE_FOLDER, OUTPUT_FOLDER, WAV_FOLDER


class Cleanup(threading.Thread):
    def __init__(self, minutes=30, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minutes = minutes
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            self.delete_files(self.minutes)
            time.sleep(30)

    def delete_files(self, minutes):
        out_dir = os.path.join(BASE_FOLDER, OUTPUT_FOLDER)
        wav_dir = os.path.join(BASE_FOLDER, WAV_FOLDER)
        current_time = time.time()
        for directory in [out_dir, wav_dir]:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_age = (current_time - os.path.getmtime(file_path)) / 60
                    if file_age > minutes:
                        try:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")

    def stop(self):
        self._stop_event.set()
        print("Stopped thread")
