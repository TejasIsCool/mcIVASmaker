import os
import time

import src.ui_manager.PySimpleGUI as sg
from src.logic.fileio.file_verifier import check_file_exists
from src.logic.fileio.image_thumbnail import load_image_for_display, load_image_for_preview
from src.logic.image_logic.image_manager import manipulate_image
from io import BytesIO
import logging
logger = logging.getLogger(__name__)

img_info = {"path": "", "bytes": BytesIO(), "size": [0, 0], "img_size": [0, 0]}


def manage_img_tab(window, event, values):
    # Loads a preview of the selected image
    if event == "-Submit_ITS-":
        img_info['path'] = values['-Text Entered-']
        img_info['img_size'], img_info['bytes'] = load_image_for_display(
            values['-Text Entered-'],
            sg.Window.get_screen_size()
        )
        if img_info['bytes'] is None:
            sg.popup("ERROR!", "Error in file path!")
            return
        elif not img_info['bytes']:
            sg.popup("ERROR!", "Some error in opening/reading the file! Are you sure its an image?")
            return
        window['-LOADED_IMAGE-'](data=img_info['bytes'].getvalue())
        window['-LOADED_IMAGE-'](visible=True)
        window['-Img_Attrs-'](visible=True)
        preview_bytes = load_image_for_preview(
            img_info['bytes'],
            {
                'manipulation': values["-Img_Type-"],
                'brightness': 127,
                'blocklist': values['-Img_Any_Listing_List-'],
                'mode': values['-Img_Any_Options-'],
                'side': values['-Img_Any_Side-'].lower(),
                'dither': values['-Img_Dithering-'],
                'alternate': values['-Img_Lamps_Alternate-'],
                'color_set': values['-Color_Set-'],
                'color_compare': values['-Comparison_Method-']
            }
        )
        window['-Preview_Image-'](data=preview_bytes.getvalue())

        # Updates the text which tells the final resolution of the output
        scale = values['-Img_Scale-']
        scale = int(scale[:-1])

        crop_topx = values['-Img_Crop_Top_X-']
        crop_topy = values['-Img_Crop_Top_Y-']
        crop_bottom_x = values['-Img_Crop_Bottom_X-']
        crop_bottom_y = values['-Img_Crop_Bottom_Y-']

        crop_topx = 0 if crop_topx.lower() == "" else crop_topx
        crop_topy = 0 if crop_topy.lower() == "" else crop_topy
        crop_bottom_x = img_info['img_size'][0] if crop_bottom_x.lower() in ["max", ""] else crop_bottom_x
        crop_bottom_y = img_info['img_size'][1] if crop_bottom_y.lower() in ["max", ""] else crop_bottom_y

        if any([not str(i).isdigit() for i in [crop_topx, crop_topy, crop_bottom_x, crop_bottom_y]]):
            sg.popup("ERROR!", "Invalid Crop Values!")
            return

        # These are the cropped sizes
        new_size_width = crop_bottom_x - crop_topx
        new_size_height = crop_bottom_y - crop_topy
        new_scale = 1 / scale * 16
        if new_size_width % new_scale != 0:
            new_width = new_size_width + (new_scale - (new_size_width % new_scale))
        else:
            new_width = new_size_width

        if new_size_height % new_scale != 0:
            new_height = new_size_height + (new_scale - (new_size_height % new_scale))
        else:
            new_height = new_size_height

        # These are the final images sizes with the current configurations
        img_info['size'][0], img_info['size'][1] = new_width, new_height

        # Update the text
        update_size(window, scale, values)

    # Enabled the button if the entered path is valid
    if event == "-Text Entered-":
        if check_file_exists(values['-Text Entered-']):
            window['-Submit_ITS-'](disabled=False)
        else:
            window['-Submit_ITS-'](disabled=True)

    # Update the output resolution text if the scale changes
    if event == "-Img_Scale-":
        scale = values['-Img_Scale-']
        scale = int(scale[:-1])
        update_size(window, scale, values)

    # Enabling or disabling the view to certain elements, if they are not associated with the selected mode(-Img_Type-)
    if event == "-Img_Type-":
        if "Any" in values['-Img_Type-']:
            window['-Redstone_Lamps_Key-'](visible=False)
            window['-Any_Block_Key-'](visible=True)
            window.refresh()
            window['-Img_Attrs-'].contents_changed()
        else:
            window['-Any_Block_Key-'](visible=False)
            window['-Redstone_Lamps_Key-'](visible=True)
            window.refresh()
            window['-Img_Attrs-'].contents_changed()

        if values['-Img_Type-'] == "Image To Redstone Lamps Schematic":
            window['-Img_Lamps_Schem_Check-'](visible=True)
        else:
            window['-Img_Lamps_Schem_Check-'](visible=False)

        if "Schematic" in values['-Img_Type-']:
            window['-Img_Save_As_Img-'](visible=False)
            window['-Img_Save_As_Schem-'](visible=True)
        else:
            window['-Img_Save_As_Schem-'](visible=False)
            window['-Img_Save_As_Img-'](visible=True)

        # Updating the Text
        scale = values['-Img_Scale-']
        scale = int(scale[:-1])
        update_size(window, scale, values)

    # Updating the final resolution text if any cropping is made
    if "Img_Crop" in event:
        scale = values['-Img_Scale-']
        scale = int(scale[:-1])

        crop_topx = values['-Img_Crop_Top_X-']
        crop_topy = values['-Img_Crop_Top_Y-']
        crop_bottom_x = values['-Img_Crop_Bottom_X-']
        crop_bottom_y = values['-Img_Crop_Bottom_Y-']

        crop_topx = 0 if crop_topx.lower() == "" else crop_topx
        crop_topy = 0 if crop_topy.lower() == "" else crop_topy
        crop_bottom_x = img_info['img_size'][0] if crop_bottom_x.lower() in ["max", ""] else crop_bottom_x
        crop_bottom_y = img_info['img_size'][1] if crop_bottom_y.lower() in ["max", ""] else crop_bottom_y

        if any([not str(i).isdigit() for i in [crop_topx, crop_topy, crop_bottom_x, crop_bottom_y]]):
            sg.popup("ERROR!", "Invalid Crop Values!")
            return

        crop_topx = int(crop_topx)
        crop_topy = int(crop_topy)
        crop_bottom_x = int(crop_bottom_x)
        crop_bottom_y = int(crop_bottom_y)

        new_size_width = crop_bottom_x - crop_topx
        new_size_height = crop_bottom_y - crop_topy
        new_scale = 1 / scale * 16
        if new_size_width % new_scale != 0:
            new_width = new_size_width + (new_scale - (new_size_width % new_scale))
        else:
            new_width = new_size_width

        if new_size_height % new_scale != 0:
            new_height = new_size_height + (new_scale - (new_size_height % new_scale))
        else:
            new_height = new_size_height

        img_info['size'][0], img_info['size'][1] = new_width, new_height
        update_size(window, scale, values)

    # What to do when clicking the run button
    if event == "-Img_Run-":
        # Manage the crop
        crop_topx = values['-Img_Crop_Top_X-']
        crop_topy = values['-Img_Crop_Top_Y-']
        crop_bottom_x = values['-Img_Crop_Bottom_X-']
        crop_bottom_y = values['-Img_Crop_Bottom_Y-']
        all_crop = [crop_topx, crop_topy, crop_bottom_x, crop_bottom_y]
        if all_crop[0] == "":
            all_crop[0] = "0"
        if all_crop[1] == "":
            all_crop[1] = "0"
        if all_crop[2] == "":
            all_crop[2] = "Max"
        if all_crop[3] == "":
            all_crop[3] = "Max"

        if not all((all_crop[i].isdigit() or (all_crop[i].lower() == "max" and i in [2, 3])) for i in range(4)):
            sg.popup("Error!", "Invalid values in crop! Only integers accepted!(Or max for the bottom coordinates)")
            return

        img_type = values['-Img_Type-']
        details = {
            'blocklist': values['-Img_Any_Listing_List-'],
            'mode': values['-Img_Any_Options-'],
            'dither': values['-Img_Dithering-'],
            'alternate': values['-Img_Lamps_Alternate-'],
            'color_set': values['-Color_Set-'],
            'color_compare': values['-Comparison_Method-']
        }

        scale = values['-Img_Scale-']

        details['side'] = values['-Img_Any_Side-'].lower()
        # Setting the correct output path if unspecified
        if values['-Output_Path-'] == "":
            if "Schematic" in img_type:
                file_end = ".schem"
            else:
                file_end = ".png"
            if not os.path.exists("./mcIVASMAKER_output"):
                os.makedirs("./mcIVASMAKER_output")
            output = f"./mcIVASMAKER_output/output{time.strftime('%y_%m_%d-%H_%M_%S', time.localtime())}{file_end}"
        else:
            output = values['-Output_Path-']

        details['brightness'] = values['-Image_Brightness-']
        details['place_redstone_blocks'] = values['-Img_Lamps_Schem_Check-']

        logger.info("Image Conversion")
        logger.debug("Video Details:")
        logger.debug("FilePath: " + img_info['path'])
        logger.debug("Output Path: " + output)
        logger.debug("Manupilations: " + img_type)
        logger.debug(f"Crop: {all_crop}")
        logger.debug(f"Scale: {scale}")
        logger.debug(f"Details: {details}")

        iteration = 0
        progress_size = 0
        # manipulate_image is a generator, so we can update the progress more easily
        for progress in manipulate_image(
                filepath=img_info['path'],
                output=output,
                manipulation=img_type,
                crop=all_crop,
                scale=scale,
                details=details
        ):
            if iteration == 0:
                progress_size = progress - 1
                iteration += 1
                continue
            if progress == "Done Processing!":
                sg.one_line_progress_meter(
                    "Saving..", 0, 1, "Saving...", no_button=True, orientation='horizontal', no_titlebar=True
                )
                continue
            if progress == "Done!":
                sg.one_line_progress_meter(
                    "Saving..", 1, 1, no_button=True, no_titlebar=True, orientation='horizontal',
                )
                sg.popup_auto_close("Done!", "Done!", auto_close_duration=4)
                logger.info("Done Image!")
                continue
            iteration += 1
            sg.one_line_progress_meter(
                "Working...", progress, progress_size, no_button=True, orientation='horizontal'
            )

    # Deselecting the ListBox
    if event == "Deselect All":
        window['-Img_Any_Listing_List-'](set_to_index=[])

    # Updating the preview image if any options change
    if event in [
        "-Image_Brightness-",
        "-Img_Any_Side-",
        "-Img_Any_Options-",
        "-Img_Type-",
        "-Img_Any_Listing_List-",
        "-Img_Lamps_Alternate-",
        "-Img_Dithering-",
        "-Color_Set-",
        "-Comparison_Method-"
    ] and values['-Update_Preview-']:
        preview_bytes = load_image_for_preview(
            img_info['bytes'],
            {
                'manipulation': values["-Img_Type-"],
                'brightness': values['-Image_Brightness-'],
                'blocklist': values['-Img_Any_Listing_List-'],
                'mode': values['-Img_Any_Options-'],
                'side': values['-Img_Any_Side-'].lower(),
                'dither': values['-Img_Dithering-'],
                'alternate': values['-Img_Lamps_Alternate-'],
                'color_set': values['-Color_Set-'],
                'color_compare': values['-Comparison_Method-']
            }
        )
        window['-Preview_Image-'](data=preview_bytes.getvalue())


# Resolution text updater
def update_size(window: sg.Window, scale: int, values):
    if "Schematic" in values['-Img_Type-']:
        total_size = (img_info['size'][0] * scale / 16, img_info['size'][1] * scale / 16)
        window['-Img_Scale_Warning-'](f"Size: ({total_size[0]},{total_size[1]}) blocks")
    else:
        total_size = (img_info['size'][0] * scale, img_info['size'][1] * scale)
        window['-Img_Scale_Warning-'](f"Size: ({total_size[0]},{total_size[1]}) pixels\n"
                                      f"Each block is 16x16 pixels")
