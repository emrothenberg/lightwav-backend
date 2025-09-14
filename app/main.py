import logging
import os
import threading
import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse

from utils.config import BASE_FOLDER, OUTPUT_FOLDER, WAV_FOLDER
from utils.get_wav import save_temp_wav
from utils.progress import get_progress
from utils.process import process

app = FastAPI(docs_url=None, redoc_url=None)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class NoLoggingFilter(logging.Filter):
    def filter(self, record):
        return '/check-progress' not in record.getMessage()

# Add filter to FastAPI's default logger
logging.getLogger("uvicorn.access").addFilter(NoLoggingFilter())


@app.get("/")
def main():
    response = '''
    <html>
    <head>
    <title>
    LightWAV Backend API
    </title>
    </head>
    <body>
    </body>
    </html>
    '''
    return HTMLResponse(response)


@app.post("/process")
async def process_wav(audio_file: UploadFile):
    if not audio_file or not audio_file.content_type in ["audio/wav", "audio/mpeg"]:
        return JSONResponse(status_code=400, content={"message": "Invalid file or file not provided."})

    job_id = str(uuid.uuid4())

    try:
        await save_temp_wav(audio_file, job_id)
        processing = threading.Thread(target=process, args=(job_id,))
        processing.start()
        print("Started processing")
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": e})

    return JSONResponse(status_code=200, content={"message": job_id})


@app.get("/check-progress")
async def check_progress(job_id: str):
    progress = get_progress(job_id)
    return JSONResponse(status_code=200, content={"message": progress})


@app.get("/get-video")
async def get_video(job_id: str):
    file_path = os.path.join(
        BASE_FOLDER, OUTPUT_FOLDER, job_id + ".mp4")

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"message": "File does not exist"})

    def iterfile():
        with open(file_path, mode="rb") as f:
            yield from f

    headers = {
        "Content-Disposition": f"attachment; filename={job_id}.mp4"
    }

    return StreamingResponse(iterfile(), media_type="video/mp4", headers=headers)

@app.get("/get-image")
async def get_image(job_id: str):
    file_path = os.path.join(
        BASE_FOLDER, OUTPUT_FOLDER, job_id + ".mp4" + ".png")

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"message": "File does not exist"})

    def iterfile():
        with open(file_path, mode="rb") as f:
            yield from f

    headers = {
        "Content-Disposition": f"attachment; filename={job_id}.png"
    }

    return StreamingResponse(iterfile(), media_type="image/png", headers=headers)
