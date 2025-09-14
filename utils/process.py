import shutil
import subprocess
import threading
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from scipy.fft import fft
from moviepy.editor import AudioFileClip, ImageSequenceClip
import os
from PIL import Image
import math

from .config import BASE_FOLDER, BASS, MAX_THRESHOLD, MID, OUTPUT_FOLDER, SD_DIMENSIONS, TEMP_FOLDER, TREBLE, UPSCALED_DIMENSIONS, WAV_FOLDER, FPS


def create_log_entry(percent, msg):
    return f'\n{percent}%: {msg}'


def get_audio_segment(file_path):
    return AudioSegment.from_wav(file_path)


def split_audio_to_segments(audio_segment, segments_per_second=FPS):
    segment_duration = 1000 // segments_per_second  # in milliseconds
    segments = [audio_segment[i:i + segment_duration]
                for i in range(0, len(audio_segment), segment_duration)]
    return segments


def calculate_fft_levels(segment, sample_rate):
    samples = np.array(segment.get_array_of_samples())
    samples = samples.astype(np.float32)
    fft_result = np.abs(fft(samples))

    # Define frequency ranges for bass, mid, and treble
    freqs = np.fft.fftfreq(len(fft_result), 1/sample_rate)
    bass = np.mean(fft_result[(freqs >= BASS) & (freqs < MID)])
    mid = np.mean(fft_result[(freqs >= MID) & (freqs < TREBLE)])
    treble = np.mean(fft_result[(freqs >= TREBLE) & (freqs < MAX_THRESHOLD)])

    return bass, mid, treble


def normalize_levels(levels, max_level):
    try:
        return int((levels / max_level) * 255)
    except ValueError:
        return 0


def generate_rgb_colors(segments, sample_rate, max_levels):
    colors = []
    for segment in segments:
        bass, mid, treble = calculate_fft_levels(segment, sample_rate)
        red = normalize_levels(bass, max_levels['bass'])
        green = normalize_levels(mid, max_levels['mid'])
        blue = normalize_levels(treble, max_levels['treble'])
        colors.append((red, green, blue))
    return colors


def create_color_frames(colors, resolution=SD_DIMENSIONS):
    frames = []
    for color in colors:
        frame = np.zeros((resolution[1], resolution[0], 3), dtype=np.uint8)
        frame[:, :] = color
        frames.append(frame)
    return frames


def create_video(wav_file_path, job_path, output_video_path):
    progress = 0
    log_file = open(os.path.join(job_path, "progress.log"), 'w')
    log_file.write("0%: Starting process...")

    audio_segment = get_audio_segment(wav_file_path)
    sample_rate = audio_segment.frame_rate
    progress += 5
    log_file.write(create_log_entry(progress, "Sampled audio"))

    segments = split_audio_to_segments(audio_segment)
    progress += 10
    log_file.write(create_log_entry(progress, "Segmented audio"))

    # Calculate max levels for normalization
    all_levels = [calculate_fft_levels(
        segment, sample_rate) for segment in segments]
    max_levels = {
        'bass': max(level[0] for level in all_levels),
        'mid': max(level[1] for level in all_levels),
        'treble': max(level[2] for level in all_levels)
    }
    progress += 30
    log_file.write(create_log_entry(
        progress, "Calculated levels for normalization"))

    # Generate RGB colors for each segment
    colors = generate_rgb_colors(segments, sample_rate, max_levels)
    progress += 20
    log_file.write(create_log_entry(progress, "Calculated colors"))

    # Create color frames
    frames = create_color_frames(colors)
    progress += 15
    log_file.write(create_log_entry(progress, "Created color frames"))

    # Save frames as a video
    temp_dir = os.path.join(job_path, "temp_frames")
    os.makedirs(temp_dir, exist_ok=True)
    frame_files = []
    for i, frame in enumerate(frames):
        frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
        plt.imsave(frame_path, frame)
        frame_files.append(frame_path)
        progress += 10 / len(frames)

        if int(progress) - 10 / len(frames) < int(progress):
            log_file.write(create_log_entry(
                progress, f"Processed frame {i+1}/{len(frames)}"))

    progress = 90
    log_file.write(create_log_entry(progress, f"Processed all frames..."))
    print("Processed all frames")

    audio_clip = AudioFileClip(wav_file_path)
    video_clip = ImageSequenceClip(frame_files, fps=FPS).set_audio(audio_clip)
    video_clip.write_videofile(output_video_path, codec="libx264", fps=FPS)

    progress += 4
    log_file.write(create_log_entry(progress, f"Finalizing video..."))

    # Clean up temporary files
    for frame_path in frame_files:
        os.remove(frame_path)
    os.rmdir(temp_dir)
    progress += 1
    log_file.write(create_log_entry(progress, f"Upscaling video..."))

    return colors


def create_cover(rgb_colors, output):
    n_colors = len(rgb_colors)
    square_size = 8  # Each color is a 2x2 square
    grid_size = math.ceil(math.sqrt(n_colors))

    # Create an image with the new size
    img = Image.new("RGB", (grid_size * square_size, grid_size * square_size))

    # Populate the image with 2x2 squares of colors
    for i, color in enumerate(rgb_colors):
        x = (i % grid_size) * square_size
        y = (i // grid_size) * square_size
        for dx in range(square_size):
            for dy in range(square_size):
                img.putpixel((x + dx, y + dy), color)

    # Save the image as a PNG file
    img.save(output)


def upscale(og, output):
    temp_output = '.mp4'.join(output.split('.mp4')[:-1]) + '.tmp.mp4'
    subprocess.run([
        'ffmpeg', '-i', og, '-vf', f'scale={UPSCALED_DIMENSIONS[0]}:{UPSCALED_DIMENSIONS[1]}',
        '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k', '-y', temp_output
    ])
    os.rename(temp_output, output)


def process(job_id: str):
    print("Processing")
    job_path = os.path.join(BASE_FOLDER, TEMP_FOLDER, job_id)
    wav_file = os.path.join(
        BASE_FOLDER, WAV_FOLDER, job_id+'.wav')
    temp_output_path = os.path.join(
        BASE_FOLDER, TEMP_FOLDER, job_id, job_id+'.mp4')
    output_path = os.path.join(
        BASE_FOLDER, OUTPUT_FOLDER, job_id+'.mp4')
    os.makedirs(job_path, exist_ok=True)
    colors = create_video(wav_file, job_path, temp_output_path)
    create_cover(colors, output_path + '.png')
    upscale(temp_output_path, output_path)
    os.remove(wav_file)
    shutil.rmtree(job_path)
