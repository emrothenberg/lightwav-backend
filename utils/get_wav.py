import os
from pydub import AudioSegment

from .config import BASE_FOLDER, WAV_FOLDER


async def save_temp_wav(audio_file, job_id):
    wav_path = os.path.join(
        BASE_FOLDER, WAV_FOLDER, job_id + ".wav")
    if audio_file.content_type == "audio/wav":
        with open(wav_path, "wb") as buffer:
            buffer.write(await audio_file.read())

    elif audio_file.content_type == "audio/mpeg":
        mp3_path = os.path.join(
            BASE_FOLDER, WAV_FOLDER, job_id + ".mp3")
        with open(mp3_path, "wb") as buffer:
            buffer.write(await audio_file.read())

        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")
        os.remove(mp3_path)
