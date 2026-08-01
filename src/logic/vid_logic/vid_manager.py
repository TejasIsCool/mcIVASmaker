import os
import time
import queue
from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Queue, Manager
import src.ui_manager.PySimpleGUI as sg
from src.logic.image_logic.image_manager import manipulate_image
from src.logic.vid_logic import ffmpeg_manager
from src.path_manager.pather import resource_path
from src.logic.vid_logic import schematic_manager
import logging

logger = logging.getLogger(__name__)

assets_path = resource_path("./assets/cache/")

# The cache folders
vid_cache_folder_jpg = os.path.normpath(os.path.join(assets_path, "./img_cache_jpg/"))
vid_cache_folder_png = os.path.normpath(os.path.join(assets_path, "./img_cache_png/"))
vid_cache_folder_m4a = os.path.normpath(os.path.join(assets_path, "./audio_cache/"))
vid_processed_folder = os.path.normpath(
    os.path.join(assets_path, "./img_process_cache/")
)

# Create the paths if they don't exist (Git does not recognize empty folders)
if not os.path.exists(vid_cache_folder_jpg):
    os.makedirs(vid_cache_folder_jpg)
if not os.path.exists(vid_cache_folder_png):
    os.makedirs(vid_cache_folder_png)
if not os.path.exists(vid_cache_folder_m4a):
    os.makedirs(vid_cache_folder_m4a)
if not os.path.exists(vid_processed_folder):
    os.makedirs(vid_processed_folder)

THREAD_KEY = "-Vid_Thread-"


def vid_manager(
    window: sg.Window,
    filepath: str,
    output: str,
    manipulation: str,
    scale: str,
    details: dict,
    preserve_cache: bool,
):
    loop_start_time = time.time()

    # Cleaning cache folders, incase a previous run failed to do so
    cleanup_folders()
    logger.info("Cleaned Previous Cache")

    logger.debug("Video Details:")
    logger.debug("FilePath: " + filepath)
    logger.debug("Output Path: " + output)
    logger.debug("Manipulations: " + manipulation)
    logger.debug("Scale: " + scale)
    logger.debug(f"Details: {details}")

    frame_count = ffmpeg_manager.get_frame_count(filepath, details["frame_rate"])
    resolution = ffmpeg_manager.get_resolution(filepath)

    logger.debug(f"Expected Frame count: {frame_count}")
    logger.debug(f"Resolution: {resolution}")
    logger.debug(f"Frame rate: {details['frame_rate']}")
    logger.debug(f"Process count: {details['process_count']}")
    logger.debug(f"Quality (PNG): {details['quality']}")

    logger.info("Starting converting the video into intermediate images")

    # Instantiating the process/thread related objects
    process_count = details["process_count"]
    process_pool = Pool(processes=process_count)
    ff_pool = ThreadPool(processes=2)
    manager = Manager()
    event_queue = manager.Queue()

    logger.debug(f"Created Pool(processes={process_count}), ThreadPool(processes=2), Manager Queue")

    # Close enough frame count
    window.write_event_value((THREAD_KEY, "-Image_Count-"), frame_count)

    # Selecting the correct cache folder
    cache_folder = vid_cache_folder_png if details["quality"] else vid_cache_folder_jpg
    logger.debug(f"Using cache folder: {cache_folder}")

    # Running the encoder (In another thread)
    img_async = ff_pool.apply_async(
        ffmpeg_manager.vid_to_img,
        (filepath, details["frame_rate"], cache_folder),
        callback=lambda x: logger.debug(f"FFmpeg vid_to_img callback: return code {x}"),
    )
    audio_async = ff_pool.apply_async(ffmpeg_manager.vid_to_audio, (filepath,))
    ff_pool.close()
    logger.debug("Submitted ffmpeg vid_to_img and vid_to_audio to thread pool")

    # Starting the image conversion, till at least 95% the images are there
    current_image = 0
    image_processes = []
    img_count = 0
    first_loop_start = time.time()

    while True:
        # Checking the number of files that have been outputted by ffmpeg
        files = os.listdir(cache_folder)
        file_count = len(files)

        if file_count >= (frame_count * 0.95) or img_async.ready():
            reason = "file_count >= 95%" if file_count >= (frame_count * 0.95) else "img_async.ready()"
            logger.info(
                f"First while loop exited: {reason} | "
                f"files_on_disk={file_count}, expected={frame_count}, "
                f"images_dispatched={current_image}, "
                f"elapsed={time.time() - first_loop_start:.2f}s"
            )
            break

        # Updating the progress meter
        window.write_event_value(
            (THREAD_KEY, "-Img_Conversion-"), file_count / frame_count
        )

        # Starting the processing of images to blocks, while ffmpeg is generating those images
        if file_count > current_image:
            img_file_path = os.path.join(cache_folder, files[current_image])
            # Remove the first 4 and last 4 characters, to get just the number
            file_number = os.path.split(img_file_path)[1][4:-4]

            if "Schematic" in manipulation:
                processed_path = os.path.join(
                    vid_processed_folder, file_number + ".schem"
                )
            else:
                processed_path = os.path.join(
                    vid_processed_folder, file_number + ".png"
                )

            logger.debug(f"Dispatching image {current_image + 1}: {files[current_image]}")

            image_processes.append(
                process_pool.apply_async(
                    manage_single_image,
                    (
                        event_queue,
                        img_file_path,
                        processed_path,
                        manipulation,
                        scale,
                        details,
                    ),
                )
            )
            current_image += 1

        # Item count checking frequency
        time.sleep(0.1)

    ff_pool.join()
    try:
        img_rc = img_async.get()
        logger.debug(f"ff_pool.join() complete. vid_to_img return code: {img_rc}")
    except Exception as e:
        logger.error(f"vid_to_img raised an exception: {e}")

    try:
        audio_rc = audio_async.get()
        logger.debug(f"vid_to_audio return code: {audio_rc}")
    except Exception as e:
        logger.warning(f"vid_to_audio raised an exception: {e}")

    logger.info("Converted Video to intermediate images and audio")

    # Run the already processing images and show their status
    logger.debug(f"Waiting for {len(image_processes)} first-batch image processes to complete...")
    for i, process in enumerate(image_processes):
        process.wait()
        if not process.successful():
            try:
                err = process.get()
            except Exception as e:
                err = e
            logger.error(f"First-batch process {i} FAILED: {err}")
        window.write_event_value((THREAD_KEY, "-Image_Done-"), None)
        img_count += 1

    logger.debug(f"First batch complete: {img_count} images in {time.time() - first_loop_start:.2f}s")

    # Update images done
    window.write_event_value((THREAD_KEY, "-Set_Images_Done-"), img_count)

    # Video has now been converted to images and audio
    window.write_event_value((THREAD_KEY, "-Img_Conversion-"), 1)
    logger.debug("Now doing the bulk processing")

    # Getting the correct item count and finding which files we have to process now
    files: list[str] = os.listdir(cache_folder)
    file_count = len(files)
    completed_files = os.listdir(vid_processed_folder)

    logger.debug(f"Total files in cache: {file_count}, already processed: {len(completed_files)}")

    for completed_file in completed_files:
        if "Schematic" in manipulation:
            file_no = completed_file.replace(".schem", "")
        else:
            file_no = completed_file.replace(".png", "")
        name_of_file = (
            "file"
            + file_no
            + (".jpg" if cache_folder == vid_cache_folder_jpg else ".png")
        )
        try:
            files.remove(name_of_file)
        except ValueError:
            logger.warning(
                f"Could not match completed file '{completed_file}' to source "
                f"'{name_of_file}' — not found in remaining list"
            )

    remaining_count = len(files)
    logger.info(f"Bulk processing: {remaining_count} images remaining out of {file_count} total")
    logger.debug(f"Remaining files to process: {files}")

    window.write_event_value((THREAD_KEY, "-Image_Count-"), file_count)

    # Processing the rest of the images
    for unprocessed_file in files:
        img_file_path = os.path.join(cache_folder, unprocessed_file)
        file_number = os.path.split(img_file_path)[1][4:-4]

        if "Schematic" in manipulation:
            processed_path = os.path.join(vid_processed_folder, file_number + ".schem")
        else:
            processed_path = os.path.join(vid_processed_folder, file_number + ".png")

        image_processes.append(
            process_pool.apply_async(
                manage_single_image,
                (
                    event_queue,
                    img_file_path,
                    processed_path,
                    manipulation,
                    scale,
                    details,
                ),
            )
        )
        current_image += 1

    process_pool.close()
    logger.debug(f"All {len(image_processes)} total processes dispatched. Pool closed.")

    # Second monitoring loop
    iter_count = 0
    second_loop_start = time.time()
    last_progress_log = time.time()

    while True:
        # Non-blocking queue read with timeout to avoid deadlock
        try:
            data = event_queue.get(timeout=0.2)
            if data[0] == "-Single_Frame-":
                window["-Single_Frame-"](data[1])
            elif data[0] == "-Image_Done-":
                logger.debug(f"Queue: Image done -> {data[1]}")
        except queue.Empty:
            pass  # No item right now, fall through to status checks

        if all(proc.ready() for proc in image_processes):
            logger.info(
                f"All {len(image_processes)} image processes complete. "
                f"Second loop: {time.time() - second_loop_start:.2f}s, "
                f"{iter_count} iterations"
            )
            break

        iter_count += 1

        # Update the images done progress bar periodically
        if iter_count % 10 == 0:
            processed_file_count = len(os.listdir(vid_processed_folder))
            progress = processed_file_count / file_count * 100
            window["-Number_Of_Frames-"](progress)
            window["-Number_Of_Frames_Text-"](f"{processed_file_count}/{file_count}")

            # Log progress at most every 5 seconds to avoid spam
            if time.time() - last_progress_log > 5:
                ready_count = sum(1 for p in image_processes if p.ready())
                logger.debug(
                    f"Progress: {processed_file_count}/{file_count} files | "
                    f"Processes ready: {ready_count}/{len(image_processes)} | "
                    f"Queue size: {event_queue.qsize()}"
                )
                last_progress_log = time.time()

        # Check for failed processes
        if any(not proc.successful() for proc in image_processes if proc.ready()):
            logger.error("One or more image processes FAILED!")
            for i, proc in enumerate(image_processes):
                if proc.ready() and not proc.successful():
                    try:
                        error = proc.get()
                        logger.error(f"  Process {i} error: {error}")
                    except Exception as e:
                        logger.error(f"  Process {i} exception: {e}")

    process_pool.join()
    logger.debug("process_pool.join() complete")

    # If the processing was very fast, and happened before we caught up with the queue
    # updating the progress meters indicating processing done
    window["-Single_Frame-"](100)
    for i in range(img_count, frame_count):
        window.write_event_value((THREAD_KEY, "-Image_Done-"), None)
    window.write_event_value((THREAD_KEY, "-Img_Conversion-"), 1.4)

    if "Schematic" in manipulation:
        logger.info(
            "Intermediate Images converted to Intermediate block schematic frames"
        )
    else:
        logger.info("Intermediate Images converted to Intermediate block images")

    if "Schematic" in manipulation:
        schematic_manager.make_final_schematic(vid_processed_folder, output, details)
    else:
        # Creating the ffmpeg run command
        audio_file = os.path.join(vid_cache_folder_m4a, "audio.m4a")
        img_pattern = os.path.join(vid_processed_folder, "%01d.png")

        processed_files = os.listdir(vid_processed_folder)
        logger.debug(f"Files in processed folder for reassembly: {len(processed_files)}")
        logger.debug(f"Audio file exists: {os.path.exists(audio_file)}")

        if len(os.listdir(vid_cache_folder_m4a)) > 0:
            re_args = [
                "-i",
                audio_file,
                "-r",
                str(details["frame_rate"]),
                "-i",
                img_pattern,
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                output,
            ]
        else:
            logger.warning("No audio file found in cache. Creating video without audio.")
            re_args = [
                "-r",
                str(details["frame_rate"]),
                "-i",
                img_pattern,
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                output,
            ]

        logger.debug("The ffmpeg reassembly command: " + " ".join(re_args))
        return_code = ffmpeg_manager.ffmpeg_runner(re_args)
        if return_code != 0:
            logger.error(f"FFmpeg reassembly failed with return code {return_code}")
        else:
            logger.debug("FFmpeg reassembly succeeded")

    window.write_event_value((THREAD_KEY, "-Img_Conversion-"), 1.8)
    logger.info("Video Created")

    if not preserve_cache:
        # Cleaning up the cache folders
        cleanup_folders()
        logger.info("Cleaned Cache")
    else:
        logger.info("Skipped cleaning cache")

    window.write_event_value((THREAD_KEY, "-Img_Conversion-"), 2)
    total_elapsed = time.time() - loop_start_time
    logger.info(f"Video Conversion Completed! Total time: {total_elapsed:.2f}s")


# Cleans up cache
def cleanup_folders():
    cache_png_files = os.listdir(vid_cache_folder_png)
    for file in cache_png_files:
        os.remove(os.path.join(vid_cache_folder_png, file))

    cache_jpg_files = os.listdir(vid_cache_folder_jpg)
    for file in cache_jpg_files:
        os.remove(os.path.join(vid_cache_folder_jpg, file))

    cache_processed_files = os.listdir(vid_processed_folder)
    for file in cache_processed_files:
        os.remove(os.path.join(vid_processed_folder, file))

    audio_processed_files = os.listdir(vid_cache_folder_m4a)
    for file in audio_processed_files:
        os.remove(os.path.join(vid_cache_folder_m4a, file))

    logger.debug(
        f"Cleanup: removed {len(cache_png_files)} png, {len(cache_jpg_files)} jpg, "
        f"{len(cache_processed_files)} processed, {len(audio_processed_files)} audio files"
    )


# Running this for every single frame
def manage_single_image(
    event_queue: Queue,
    filename: str,
    output: str,
    manipulation: str,
    scale: str,
    details: dict,
):
    manipulation = manipulation.replace("Video", "Image")
    iteration = 0
    image_size = 1
    updates = 30

    # Using the same "image to blocks" conversion as in the image tab
    for values in manipulate_image(
        filename, output, manipulation, None, scale, details
    ):
        if iteration == 0:
            image_size = values
        iteration += 1

        # Updating the progress every certain amount of iterations
        if iteration % round(image_size / updates) == 0:
            if isinstance(values, str):
                pass
            else:
                event_queue.put(["-Single_Frame-", values / image_size * 100])

    event_queue.put(["-Image_Done-", output])
