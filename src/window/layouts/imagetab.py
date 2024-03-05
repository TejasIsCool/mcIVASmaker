from ui_manager import PySimpleGUI as sg
import textwrap
from path_manager.pather import resource_path
import json

# TODO: Black/white list will be all blocks name in a list, and clicking them changes colour to indicate its been
#  selected
path = resource_path("./assets/blocks/all_blocks_textures/")
with open(resource_path("./assets/blocks/img_generator_code/out.json"), "r") as f:
    blocks_data: list = list(json.load(f).items())
    block_name_list = [x[0] for x in blocks_data]
    block_name_list.sort()


def get_image_tab(window_size: list[int]):
    # The attributes you can select for an image
    ITS_img_attributes = sg.Column([
        [

            sg.Text("Crop: "),
            sg.Input(key="-Img_Crop_Top_X-", tooltip="Top corner X", size=4, pad=0, enable_events=True),
            sg.Text(",", pad=0),
            sg.Input(key="-Img_Crop_Top_Y-", tooltip="Top corner Y", size=4, pad=0, enable_events=True),
            sg.Text(" To ", pad=0),
            sg.Input(key="-Img_Crop_Bottom_X-", tooltip="Top corner X", size=4, pad=0, enable_events=True),
            sg.Text(",", pad=0),
            sg.Input(key="-Img_Crop_Bottom_Y-", tooltip="Top corner Y", size=4, pad=0, enable_events=True),
            sg.Text(" ", pad=0)
        ],
        [
            sg.Text("Scale: "),
            sg.Combo(
                ['16x', '8x', '4x', '2x', '1x'], default_value="16x", key="-Img_Scale-",
                enable_events=True, readonly=True, background_color="#00000000"
            ),
            sg.Text(textwrap.fill("", width=50), key="-Img_Scale_Warning-")
        ],
        [
            sg.Text("Type: "),
            sg.Combo(
                [
                    "Image To Any Block Image",
                    "Image To Redstone Lamps Image",
                    "Image To Any Block Schematic",
                    "Image To Redstone Lamps Schematic"
                ], key="-Img_Type-",
                enable_events=True,
                default_value="Image To Redstone Lamps Image",
                readonly=True,
                background_color="#00000000"
            )
        ],
        [
            sg.Frame(
                title="Redstone Lamps Options",
                key="-Redstone_Lamps_Key-",
                layout=[
                    [
                        sg.Text("Brightness Required"),
                        sg.Slider(
                            range=(0, 255),
                            default_value=127,
                            orientation="horizontal",
                            key="-Image_Brightness-",
                            enable_events=True
                        )
                    ],
                    [
                        sg.Checkbox(
                            "Dithering",
                            tooltip="Dithering is useful in preserving details, but makes things look faded"
                                    "\nIt disables the brightness slider and alternate renderer checkbox",
                            key="-Img_Dithering-",
                            enable_events=True
                        )
                    ],
                    [
                        sg.Checkbox(
                            "Alternate Renderer",
                            tooltip="This one uses Pillow to convert to greyscale, "
                                    "\nthen filter out the dark and bright pixels",
                            key="-Img_Lamps_Alternate-",
                            enable_events=True
                        )
                    ],
                    [
                        sg.Checkbox("With power sources?", default=False, visible=False, key="-Img_Lamps_Schem_Check-")
                    ]
                ]
            ),
            sg.Frame(
                title="Any Block Image Attributes",
                key="-Any_Block_Key-",
                visible=False,
                layout=[
                    [
                        sg.Text("Blocks Blacklist/Whitelist"),
                        sg.Combo(
                            ["None", "Whitelist", "Blacklist"],
                            key="-Img_Any_Options-",
                            default_value="None",
                            readonly=True,
                            background_color="#00000000",
                            enable_events=True
                        ),
                    ],
                    [
                        sg.Text("Blocks side"),
                        sg.Combo(
                            ["Top", "Bottom", "Front", "Back", "Side"],
                            key="-Img_Any_Side-",
                            default_value="Top",
                            readonly=True,
                            background_color="#00000000",
                            enable_events=True
                        )
                    ],
                    [
                        sg.Text("Blocks List To Whitelist/Blacklist"),
                        sg.Listbox(
                            pad=(12, 2),
                            values=block_name_list,
                            select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                            key="-Img_Any_Listing_List-",
                            size=(30, 10),
                            highlight_background_color="#00FF00",
                            enable_events=True,
                            right_click_menu=['&Right', ['Deselect All']]
                        ),
                    ],
                    [sg.Frame(title="Color Settings", layout=[
                        [
                            sg.Text(
                                "Average Color set (?)",
                                tooltip="These are the pre-computed color averages of each minecraft block, "
                                        "calculated in different ways",
                                text_color="#AAAAFF",
                                key="-Average_Colour_Popup-",
                                enable_events=True
                            ),
                            sg.Listbox([
                                "Linear Average",
                                "Root Mean Square Average",
                                "HSL Average",
                                "HSV Average",
                                "LAB Average",
                                "Dominant Color"
                            ], default_values=["Linear Average"], size=(20, 4), enable_events=True, key="-Color_Set-")
                        ],
                        [
                            sg.Text(
                                "Color Comparison Algorithm (?)",
                                tooltip="Changes how each individual pixel's rgb value is compared to "
                                        "each block's average color",
                                text_color="#AAAAFF",
                                key="-Color_Difference_Popup-",
                                enable_events=True
                            ),
                            sg.Listbox([
                                "Absolute Difference",
                                "Euclidean Difference",
                                "Weighted Euclidean",
                                "Redmean Difference",
                                "CIE76 DelE"
                            ], default_values=["Absolute Difference"], size=(20, 4), enable_events=True,
                                key="-Comparison_Method-")
                        ]
                    ])]
                ]
            )
        ],
        [
            sg.Text("Output: "),
            sg.Input(enable_events=True, key="-Output_Path-", size=30),
            sg.FileSaveAs("Save as",
                          key='-Img_Save_As_Img-',
                          file_types=(("Image Files", "*.png *.jpg"),),
                          target="-Output_Path-"
                          ),
            sg.FileSaveAs("Save as",
                          key='-Img_Save_As_Schem-',
                          file_types=(("Schematic Files", "*.schem"),),
                          visible=False,
                          target="-Output_Path-"
                          )
        ],
        [
            sg.Button("Run", key="-Img_Run-")
        ],
        [
            sg.Check("Update Preview?", default=True, key="-Update_Preview-")
        ],
        [
            sg.Text("Preview: (Renders at a low scale and \nno cropping and decreased resolution)")
        ],
        [
            sg.Image(key="-Preview_Image-")
        ],
        [
            sg.Text("May not be what you see when the image is rendered", size=(40, 10))
        ]
    ], key="-Img_Attrs-", visible=False, scrollable=True, size=(int(window_size[0] / 1.4), int(window_size[1] / 1.2)))

    # The area to load the image
    ITS_imageloader = sg.Column([
        [
            sg.Text(text="HI!")
        ],
        [sg.Text('Filename')],
        [
            sg.Input(enable_events=True, key="-Text Entered-"),
            sg.FileBrowse(tooltip="Browse for an Image", file_types=(("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"),))
        ],
        [sg.Button("Load", disabled=True, key="-Submit_ITS-")],
        [sg.Image(key="-LOADED_IMAGE-", visible=False)]
    ])

    # The full image tab layout
    ITS_layout = [[
        ITS_imageloader, sg.VerticalSeparator(), ITS_img_attributes
    ]]

    return ITS_layout


