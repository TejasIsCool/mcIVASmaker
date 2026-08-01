import math
import os
import subprocess
import time
from src.path_manager.pather import resource_path
import ffmpeg
import logging

logger = logging.getLogger(__name__)

assets_path = resource_path("./assets/cache/")

# The cache folders
vid_cache_folder_jpg = os.path.normpath(os.path.join(assets_path, "./img_cache_jpg/"))
vid_cache_folder_png = os.path.normpath(os.path.join(assets_path, "./img_cache_png/"))
vid_cache_folder_m4a = os.path.normpath(os.path.join(assets_path, "./audio_cache/"))
vid_processed_folder = os.path.normpath(
    os.path.join(assets_path, "./img_process_cache./")
)


# Runs ffmpeg in a subprocess
def ffmpeg_runner(options: list[str]):
    # Prevent FFmpeg from hanging on stdin prompts by adding -nostdin
    command = ["ffmpeg", "-y", "-nostdin"] + options
    logger.debug(f"Running FFmpeg: {' '.join(command)}")

    start_time = time.time()
    result = subprocess.run(command, stdout=None, stderr=None)
    elapsed = time.time() - start_time

    if result.returncode != 0:
        logger.error(f"FFmpeg exited with code {result.returncode} after {elapsed:.2f}s")
        logger.error(f"  Command: {' '.join(command)}")
    else:
        logger.debug(f"FFmpeg completed successfully in {elapsed:.2f}s")

    return result.returncode


# Does not give the exact frame count
def get_frame_count(vid_path: str, frame_rate: float) -> int:
    data = ffmpeg.probe(vid_path)
    total_time = data["format"]["duration"]
    time_in_seconds = float(total_time)
    number_of_frames = time_in_seconds * frame_rate
    result = math.ceil(number_of_frames)
    logger.debug(
        f"Frame count estimate: duration={time_in_seconds:.3f}s x "
        f"rate={frame_rate} = {number_of_frames:.2f} -> ceil={result}"
    )
    return result


def get_resolution(vid_path: str) -> tuple[int, int]:
    data = ffmpeg.probe(vid_path)
    dimensions = data["streams"][0]["width"], data["streams"][0]["height"]
    logger.debug(f"Video resolution: {dimensions[0]}x{dimensions[1]}")
    return dimensions


# Converts a video to sequence of images
def vid_to_img(vid_path: str, frame_rate: int, cache_folder: str):
    extension = "jpg" if cache_folder == vid_cache_folder_jpg else "png"
    out_pattern = os.path.join(cache_folder, f"file%01d.{extension}")
    logger.debug(f"vid_to_img: '{vid_path}' -> '{out_pattern}' @ {frame_rate}fps ({extension})")
    return_code = ffmpeg_runner(["-i", vid_path, "-r", str(frame_rate), out_pattern])
    logger.debug(f"vid_to_img finished with return code: {return_code}")
    return return_code


# Vid to images: Unused
def vid_to_img_single(vid_path: str, frame_rate: int, cache_folder: str):
    if cache_folder == vid_cache_folder_jpg:
        extension = "jpg"
    else:
        extension = "png"
    number_of_frames = get_frame_count(vid_path, frame_rate)
    for frame_number in range(number_of_frames):
        frame_time = frame_number * 1 / frame_rate
        ffmpeg_runner(
            f'-ss {frame_time} -i "{vid_path}" '
            f"-vframes 1 {os.path.join(cache_folder, 'file' + str(frame_number) + '.' + extension)}"
        )


def vid_to_audio(vid_path: str):
    out_audio = os.path.join(vid_cache_folder_m4a, "audio.m4a")
    logger.debug(f"vid_to_audio: '{vid_path}' -> '{out_audio}'")
    return_code = ffmpeg_runner(["-i", vid_path, "-q:a", "0", "-map", "a", out_audio])
    if return_code != 0:
        logger.warning(
            f"Audio extraction failed (code {return_code}). "
            f"Video may have no audio stream."
        )
    else:
        logger.debug("vid_to_audio finished successfully")
    return return_code
