import os
import time
from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Queue, Manager
from typing import Dict
import ui_manager.PySimpleGUI as sg

from logic.image_logic.image_manager import manipulate_image

from logic.vid_logic import ffmpeg_manager

scriptDir = os.path.dirname(__file__)
assets_path = os.path.join(scriptDir,
                           f"../../../assets/cache/"
                           )
assets_path = os.path.normpath(assets_path)

# The cache folders
vid_cache_folder_jpg = assets_path + "\\img_cache_jpg\\"
vid_cache_folder_png = assets_path + "\\img_cache_png\\"
vid_cache_folder_m4a = assets_path + "\\audio_cache\\"

vid_processed_folder = assets_path + "\\img_process_cache\\"

# Create the paths if they don't exist (Git doesnot recognize empty folders)
if not os.path.exists(vid_cache_folder_jpg):
    os.makedirs(vid_cache_folder_jpg)

if not os.path.exists(vid_cache_folder_png):
    os.makedirs(vid_cache_folder_png)

if not os.path.exists(vid_cache_folder_m4a):
    os.makedirs(vid_cache_folder_m4a)

if not os.path.exists(vid_processed_folder):
    os.makedirs(vid_processed_folder)


THREAD_KEY = '-Vid_Thread-'


def vid_manager(window: sg.Window, filepath: str, output: str, manipulation: str, scale: str, details: Dict):
    # Cleaning cache folders, incase a previous run failed to do so
    cleanup_folders()

    # Instantiating the process/thread related objects
    process_count = details['process_count']
    process_pool = Pool(processes=process_count)
    ff_pool = ThreadPool(processes=2)
    manager = Manager()
    event_queue = manager.Queue()

    frame_count = ffmpeg_manager.get_frame_count(filepath, details['frame_rate'])
    # Close enough frame count
    window.write_event_value((THREAD_KEY, '-Image_Count-'), frame_count)

    # Selecting the correct cache folder
    cache_folder = vid_cache_folder_png if details['quality'] else vid_cache_folder_jpg

    # Running the encoder?(In another thread)
    ff_pool.apply_async(
        ffmpeg_manager.vid_to_img, (filepath, details['frame_rate'], cache_folder),
        callback=lambda x: print(f"Test {x}")
    )
    ff_pool.apply_async(
        ffmpeg_manager.vid_to_audio, (filepath,)
    )
    ff_pool.close()
    # Starting the image conversion, till at least 95% the images are there (Not all, because we don't get exact frame
    # count with the get_frame_count
    current_image = 0
    image_processes = []
    while True:
        # Checking the number of files that have been outputted by ffmpeg
        files = os.listdir(cache_folder)
        file_count = len(files)
        if file_count >= (frame_count * 0.95):
            break
        # Updating the progress meter
        window.write_event_value((THREAD_KEY, '-Img_Conversion-'), file_count / frame_count)

        # Starting the processing of images to blocks, while ffmpeg is generating those images, to save time
        if file_count > current_image:
            img_file_path = cache_folder + files[current_image]
            processed_path = vid_processed_folder + str((current_image + 1)) + ".png"
            image_processes.append(process_pool.apply_async(
                manage_single_image,
                (event_queue, img_file_path, processed_path, manipulation, scale, details)
            ))
            current_image += 1

        # Item count checking frequency
        time.sleep(0.1)
    ff_pool.join()
    # Video has now been converted to images and audio
    window.write_event_value((THREAD_KEY, '-Img_Conversion-'), 1)
    print("I am here")
    # Getting the correct item count
    files = os.listdir(cache_folder)
    file_count = len(files)
    window.write_event_value((THREAD_KEY, '-Image_Count-'), file_count)

    # Processing the rest of the images
    while current_image < file_count:
        img_file_path = cache_folder + files[current_image]
        processed_path = vid_processed_folder + str((current_image + 1)) + ".png"
        image_processes.append(process_pool.apply_async(
            manage_single_image,
            (event_queue, img_file_path, processed_path, manipulation, scale, details)
        ))
        current_image += 1

    process_pool.close()
    print("ERE Too")
    img_count = 0
    while True:
        # Updating the progress meters, till the all the processing has been done
        data = event_queue.get()
        if data[0] == "-Single_Frame-":
            window['-Single_Frame-'](data[1])
        elif data[0] == "-Image_Done-":
            window.write_event_value((THREAD_KEY, '-Image_Done-'), None)
            img_count += 1
            print(data[1])

        if all([proc.ready() for proc in image_processes]):
            break

        if any([not proc.successful() for proc in image_processes if proc.ready()]):
            print("ERROR!")
            proc_list = [not proc.successful() for proc in image_processes if proc.ready()]
            indices = [i for i, x in enumerate(proc_list) if x]
            for index in indices:
                print(image_processes[index].get())
            pass

    process_pool.join()

    # If the processing was very fast, and happened before we caught up with the queue
    # updating the progress meters indicating processing done
    window['-Single_Frame-'](100)
    for i in range(img_count, frame_count):
        window.write_event_value((THREAD_KEY, '-Image_Done-'), None)

    # Creating the ffmpeg run command
    if len(os.listdir(vid_cache_folder_m4a)) > 0:
        re_options = f"-i {vid_cache_folder_m4a}audio.m4a -r {details['frame_rate']} -i {vid_processed_folder}%01d" \
                     f".png -crf 20 -pix_fmt yuv420p {output}"
    else:
        re_options = f"-r {details['frame_rate']} -i {vid_processed_folder}%01d" \
                     f".png -crf 20 -pix_fmt yuv420p {output}"
    print(re_options)
    ffmpeg_manager.ffmpeg_runner(
        re_options
    )
    window.write_event_value((THREAD_KEY, '-Img_Conversion-'), 1.8)
    # Cleaning up the cache folders
    cleanup_folders()
    window.write_event_value((THREAD_KEY, '-Img_Conversion-'), 2)


# Cleans up cache
def cleanup_folders():
    cache_png_files = os.listdir(vid_cache_folder_png)
    for file in cache_png_files:
        os.remove(vid_cache_folder_png + file)

    cache_jpg_files = os.listdir(vid_cache_folder_jpg)
    for file in cache_jpg_files:
        os.remove(vid_cache_folder_jpg + file)

    cache_processed_files = os.listdir(vid_processed_folder)
    for file in cache_processed_files:
        os.remove(vid_processed_folder + file)

    audio_processed_files = os.listdir(vid_cache_folder_m4a)
    for file in audio_processed_files:
        os.remove(vid_cache_folder_m4a+file)


# Running this for every single frame
def manage_single_image(event_queue: Queue, filename: str, output: str, manipulation: str, scale: str, details: Dict):
    manipulation = manipulation.replace("Video", "Image")
    iteration = 0
    image_size = 1
    updates = 30
    # Using the same "image to blocks" conversion as in the image tab
    for values in manipulate_image(filename, output, manipulation, None, scale, details):
        if iteration == 0:
            image_size = values
        iteration += 1
        # Updating the progress every certain amount of iterations
        if iteration % round(image_size / updates) == 0:
            if type(values) == str:
                pass
            else:
                event_queue.put(['-Single_Frame-', values / image_size * 100])
    event_queue.put(['-Image_Done-', output])
