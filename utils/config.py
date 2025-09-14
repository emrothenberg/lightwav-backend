# Audio channel threshold
import os


BASS = 20
MID = 250
TREBLE = 4000
MAX_THRESHOLD = 20000

# Video properties
FPS = 12
RATIO = 16/9
SD_RES = 100
UPSCALED_RES = 720
SD_DIMENSIONS = [int(SD_RES * RATIO), SD_RES]
UPSCALED_DIMENSIONS = [int(UPSCALED_RES * RATIO), UPSCALED_RES]

# API
HOST = '0.0.0.0'
PORT = 8000

# RUNTIME
HOME = os.path.expanduser('~')
BASE_FOLDER = os.path.join(HOME, "LightWAV")
TEMP_FOLDER = '.in_progress'
WAV_FOLDER = '.wav'
OUTPUT_FOLDER = '.out'
