import os
import time
from io import BytesIO

from PIL import Image

import ui_manager.PySimpleGUI as sg
from logic.fileio.file_verifier import check_file_exists
from logic.vid_logic.ffmpeg_manager import get_resolution, get_frame_count
from logic.vid_logic.vid_manager import vid_manager
from path_manager.pather import resource_path

# Loads up the progress animation
IMAGES = []
frame_count = 0
for i in range(60):
    img = Image.open(resource_path(f"./assets/gifs/vid_progress/{i}.png"))
    img = img.resize((50, 50))
    with BytesIO() as out:
        img.save(out, format="PNG")
        data = out.getvalue()
    img.close()
    IMAGES.append(data)

vid_info = {"path": ""}

images_done = 0
img_count = 0
process_running = False
THREAD_KEY = '-Vid_Thread-'

image_size = (0, 0)
advance_state = False


def manage_vid_tab(window, event, values):
    global images_done, img_count
    global process_running
    global THREAD_KEY
    global image_size
    global advance_state

    # Only updating the options, if there is no video conversion going on
    if not process_running:
        # Loads up video attributes
        if event == "-Submit_VTS-":
            vid_info['path'] = values['-Vid Text Entered-']
            window['-Vid_Attrs-'](visible=True)
            window['-Vid_Loaded-'](f"Loaded Video: {vid_info['path']}")
            image_size = get_resolution(vid_info['path'])
            inp_scale = values['-Vid_Scale-']
            scale = int(inp_scale[:-1])
            # If the final resolution is too big, ffmpeg does not work
            # Also large resolutions might even crash the computer
            if image_size[0] * scale > 8000 or image_size[1] * scale > 8000:
                if image_size[0] * scale > 32767 or image_size[1] * scale > 32767:
                    window['-Vid_Scale_Warning-'](
                        "ERROR: ffmpeg only allows the max size of the video to be 32767x32767\n"
                        f"Detected size : ({image_size[0] * scale},{image_size[1] * scale}), Use a smaller scale",
                        text_color="#FF1111"
                    )
                    window['-Vid_Run-'](disabled=True)
                else:
                    window['-Vid_Scale_Warning-'](
                        f"Warning: The resolution is gigantic({image_size[0] * scale},{image_size[1] * scale}).\n"
                        "This may take a long time to run\n"
                        "There is a high chance of the program hanging\n"
                        "and your entire system crashing\n"
                        "Proceed with Caution",
                        text_color="#FFFF0F"
                    )
            else:
                window['-Vid_Scale_Warning-'](
                    f"Output Resolution: ({image_size[0] * scale},{image_size[1] * scale})",
                    text_color="#FFFFFF"
                )
            window['-Frame_Count-'](f"Frame Count: {get_frame_count(vid_info['path'], values['-Vid_Frame_Rate-'])}")

        if event == '-Vid_Scale-':
            inp_scale = values['-Vid_Scale-']
            scale = int(inp_scale[:-1])
            if image_size[0] * scale > 8000 or image_size[1] * scale > 8000:
                if image_size[0] * scale > 32767 or image_size[1] * scale > 32767:
                    window['-Vid_Scale_Warning-'](
                        "ERROR: ffmpeg only allows the max size of the video to be 32767x32767\n"
                        f"Detected size : ({image_size[0] * scale},{image_size[1] * scale}), Use a smaller scale",
                        text_color="#FF1111"
                    )
                    window['-Vid_Run-'](disabled=True)
                else:
                    window['-Vid_Scale_Warning-'](
                        f"Warning: The resolution is gigantic({image_size[0] * scale},{image_size[1] * scale}).\n"
                        f"This may take a long time to run\n"
                        "There is also a chance of it silently failing,\n"
                        "and your entire system crashing\n"
                        "Proceed with Caution",
                        text_color="#FFFF0F"
                    )
                    window['-Vid_Run-'](disabled=False)
            else:
                window['-Vid_Run-'](disabled=False)
                window['-Vid_Scale_Warning-'](
                    f"Output Resolution: ({image_size[0] * scale},{image_size[1] * scale})",
                    text_color="#FFFFFF"
                )

        # Enabled the load button if the path is valid
        if event == "-Vid Text Entered-":
            if check_file_exists(values['-Vid Text Entered-']):
                window['-Submit_VTS-'](disabled=False)
            else:
                window['-Submit_VTS-'](disabled=True)

        # Updating the frame count text if the frame rate slider is moved
        if event == "-Vid_Frame_Rate-":
            window['-Frame_Count-'](f"Frame Count: {get_frame_count(vid_info['path'], values['-Vid_Frame_Rate-'])}")

        # Show certain elements, depending on which modes are enabled
        if event == "-Vid_Type-":
            if "Any" in values['-Vid_Type-']:
                window['-Vid_Redstone_Lamps_Key-'](visible=False)
                window['-Vid_Any_Block_Key-'](visible=True)
                window.refresh()
                window['-Vid_Attrs-'].contents_changed()
            else:
                window['-Vid_Any_Block_Key-'](visible=False)
                window['-Vid_Redstone_Lamps_Key-'](visible=True)
                window.refresh()
                window['-Vid_Attrs-'].contents_changed()

        # Showing/hiding advance options, on clicking the advance options text
        if event == "-Advance_Dropdown-":
            if advance_state:
                window['-Advance_Dropdown-']("Advance Options ∧")
                window['-Advance_Options-'](visible=False)
            else:
                window['-Advance_Dropdown-']("Advance Options v")
                window['-Advance_Options-'](visible=True)
            advance_state = not advance_state

        # Deselecting the ListBox
        if event == "Deselect All":
            window['-Vid_Any_Listing_List-'](set_to_index=[])

        # On clicking the run button
        if event == "-Vid_Run-":
            frame_rate = values["-Vid_Frame_Rate-"]
            details = {
                'blocklist': values['-Vid_Any_Listing_List-'],
                'mode': values['-Vid_Any_Options-'],
                'quality': values['-Vid_Quality-'],
                'frame_rate': frame_rate,
                'dither': values['-Vid_Dithering-'],
                'alternate': values['-Vid_Lamps_Alternate-'],
                'color_set': values['-Vid_Color_Set-'],
                'color_compare': values['-Vid_Comparison_Method-']
            }

            # Validating the process count
            process_count = values['-Process_Count-']
            if not str(process_count).isdigit():
                process_count = 2
            elif not (1 <= int(process_count) <= 16):
                process_count = 2
            else:
                process_count = int(process_count)

            details['process_count'] = process_count

            scale = values['-Vid_Scale-']
            vid_type = values['-Vid_Type-']
            details['side'] = values['-Vid_Any_Side-'].lower()
            filepath = vid_info['path']
            # Setting the correct output location
            if values['-Vid_Output_Path-'] == "":
                if not os.path.exists("./mcIVASMAKER_output"):
                    os.makedirs("./mcIVASMAKER_output")
                output = f"./mcIVASMAKER_output/output{time.strftime('%y_%m_%d-%H_%M_%S', time.localtime())}.mp4"
            else:
                output = values['-Vid_Output_Path-']

            details['brightness'] = values['-Vid_Brightness-']
            process_running = True

            window['-Vid_Run-'](disabled=True)
            window['-Vid_Progress_Meters-'](visible=True)

            # This runs the function in another thread, so the gui can be kept updated
            window.perform_long_operation(lambda: vid_manager(
                window=window,
                filepath=filepath,
                output=output,
                manipulation=vid_type,
                scale=scale,
                details=details
            ), '-Vid Process Complete-')

    # When the thread is running
    if event[0] == THREAD_KEY:
        # Update the progress meter
        if event[1] == '-Image_Count-':
            img_count = values[event]
        if event[1] == '-Reset_Images_Done-':
            images_done = 0
        if event[1] == "-Set_Images_Done-":
            images_done = values[event]
        if event[1] == "-Image_Done-":
            images_done += 1
            progress = images_done / img_count * 100
            window['-Number_Of_Frames-'](progress)
            window['-Number_Of_Frames_Text-'](f"{images_done}/{img_count}")

        if event[1] == '-Img_Conversion-':
            window['-Images_Vid_Conversion-'](values[event])

    # If the processing is complete, allow the options to work again, and reset the progress meters
    if event == "-Vid Process Complete-":
        sg.popup("Done!", auto_close=True, auto_close_duration=10)
        process_running = False
        images_done = 0
        img_count = 0
        window['-Vid_Run-'](disabled=False)
        window['-Number_Of_Frames-'](0)
        window['-Images_Vid_Conversion-'](0)
        window['-Single_Frame-'](0)

    # Updating the progress animations, every certain amount of time
    if event == sg.TIMEOUT_KEY and process_running:
        update_animation(window)


# This updates the progress animation
def update_animation(window):
    global IMAGES
    global frame_count

    image = IMAGES[frame_count % 60]

    frame_count += 1
    window['-Progress_Gif-'](data=image)
    pass
