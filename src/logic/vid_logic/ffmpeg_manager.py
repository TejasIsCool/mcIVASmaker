import math
import os
import subprocess
from src.path_manager.pather import resource_path
import ffmpeg

assets_path = resource_path(f"./assets/cache/")

# The cache folders
vid_cache_folder_jpg = os.path.normpath(os.path.join(assets_path, "./img_cache_jpg/"))
vid_cache_folder_png = os.path.normpath(os.path.join(assets_path, "./img_cache_png/"))
vid_cache_folder_m4a = os.path.normpath(os.path.join(assets_path, "./audio_cache/"))

vid_processed_folder = os.path.normpath(os.path.join(assets_path, "./img_process_cache./"))


# Runs ffmpeg in a subprocess
def ffmpeg_runner(options: str):
    full_command = 'ffmpeg -y ' + options
    output = subprocess.call(full_command, shell=True)
    return output


# Does not give the exact frame count
def get_frame_count(vid_path: str, frame_rate: float) -> int:
    data = ffmpeg.probe(vid_path)
    total_time = data['format']['duration']
    time_in_seconds = float(total_time)
    number_of_frames = time_in_seconds * frame_rate
    return math.ceil(number_of_frames)


def get_resolution(vid_path: str) -> tuple[int, int]:
    data = ffmpeg.probe(vid_path)
    dimensions = data['streams'][0]['width'], data['streams'][0]['height']
    return dimensions


# Converts a video to sequence of images
def vid_to_img(vid_path: str, frame_rate: int, cache_folder: str):
    if cache_folder == vid_cache_folder_jpg:
        extension = "jpg"
    else:
        extension = "png"
    return ffmpeg_runner(f'-i "{vid_path}" -r {frame_rate} "{os.path.join(cache_folder,"file%01d."+extension)}"')


# Vid to images: Unused
def vid_to_img_single(vid_path: str, frame_rate: int, cache_folder: str):
    if cache_folder == vid_cache_folder_jpg:
        extension = "jpg"
    else:
        extension = "png"
    number_of_frames = get_frame_count(vid_path, frame_rate)
    for frame_number in range(number_of_frames):
        frame_time = frame_number * 1 / frame_rate
        ffmpeg_runner(f'-ss {frame_time} -i "{vid_path}" '
                      f'-vframes 1 {os.path.join(cache_folder,"file"+str(frame_number)+"."+extension)}')


def vid_to_audio(vid_path: str):
    ffmpeg_runner(f'-i "{vid_path}" -q:a 0 -map a "{os.path.join(vid_cache_folder_m4a,"audio.m4a")}"')
