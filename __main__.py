import os
from app.main import app
from utils.cleanup import Cleanup
from utils.config import BASE_FOLDER, HOST, PORT, TEMP_FOLDER, WAV_FOLDER, OUTPUT_FOLDER


def init():
    # Set global root path
    os.environ["ROOT_PATH"] = os.path.dirname(os.path.abspath(__file__))

    # Initialize directories if not already initialized
    for i in [BASE_FOLDER, TEMP_FOLDER, WAV_FOLDER, OUTPUT_FOLDER]:
        to_make = os.path.join(BASE_FOLDER, i)
        os.makedirs(to_make, exist_ok=True)
        print("Initializing directory", to_make)

    cleanup = Cleanup()
    cleanup.start()

    return cleanup


if __name__ == "__main__":
    cleanup_thread = init()

    import uvicorn
    uvicorn.run(app, host=HOST, port=0)
    cleanup_thread.stop()
    cleanup_thread.delete_files(0)
    cleanup_thread.join()
