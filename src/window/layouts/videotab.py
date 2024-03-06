from ui_manager import PySimpleGUI as sg
import textwrap
from path_manager.pather import resource_path
import json

path = resource_path("./assets/blocks/all_blocks_textures/")
with open(resource_path("./assets/blocks/img_generator_code/names_list.json"), "r") as f:
    blocks_data: list = list(json.load(f).keys())
    blocks_data.sort()


def get_video_tab():
    # The attributes you can select for the video
    VTS_vid_attributes = sg.Column([
        [
            sg.Text("Loaded Video: ", key="-Vid_Loaded-")
        ],
        [
            sg.Text("Frame rate: "),
            sg.Slider(
                (0.1, 150),
                default_value=60, key="-Vid_Frame_Rate-", orientation="horizontal", resolution=0.1, enable_events=True
            ),
            sg.Text("Frame Count: ", key='-Frame_Count-')
        ],
        [
            sg.Text("Scale: "),
            sg.Combo(
                ['16x', '8x', '4x', '2x', '1x'], default_value="16x", key="-Vid_Scale-",
                enable_events=True, readonly=True, background_color="#00000000"
            ),
            sg.Text(
                textwrap.fill("", width=50),
                visible=True, text_color="#FF1111", key="-Vid_Scale_Warning-"
            )
        ],
        [
            sg.Checkbox("Retain Quality?", key='-Vid_Quality-'),
            sg.T("A bit slower, and more cache storage taken")
        ],
        [
            sg.Text("Type: "),
            sg.Combo(
                [
                    "Video To Any Block Video",
                    "Video To Redstone Lamps Video",
                    # These two later
                    # "Video To Any Block Schematic",
                    # "Video To Redstone Lamps Schematic"
                ], key="-Vid_Type-",
                enable_events=True,
                default_value="Video To Redstone Lamps Video",
                readonly=True,
                background_color="#00000000"
            )
        ],
        [
            sg.Frame(title="Redstone Lamps Options", layout=[
                [
                    sg.Text("Brightness Required", key="-Vid_List_Text-"),
                    sg.Slider(
                        range=(0, 255),
                        default_value=127,
                        orientation="horizontal",
                        key="-Vid_Brightness-"
                    )
                ],
                [
                    sg.Checkbox(
                        "Dithering",
                        tooltip="Dithering is useful in preserving details, but makes things look faded"
                                "\nIt disables the brightness slider and alternate renderer checkbox",
                        key="-Vid_Dithering-"
                    )
                ],
                [
                    sg.Checkbox(
                        "Alternate Renderer",
                        tooltip="This one uses Pillow to convert to greyscale, "
                                "\nthen filter out the dark and bright pixels",
                        key="-Vid_Lamps_Alternate-"
                    )
                ],
            ], key="-Vid_Redstone_Lamps_Key-"
            ),
            sg.Frame(title="Any Block Image Attributes", layout=[
                [
                    sg.Text("Blocks Blacklist/Whitelist"),
                    sg.Combo(
                        ["None", "Whitelist", "Blacklist"],
                        key="-Vid_Any_Options-",
                        default_value="None",
                        readonly=True,
                        background_color="#00000000"
                    ),
                ],
                [
                    sg.Text("Blocks side"),
                    sg.Combo(
                        ["Top", "Bottom", "Front", "Back", "Side"],
                        key="-Vid_Any_Side-",
                        default_value="Top",
                        readonly=True,
                        background_color="#00000000"
                    )
                ],
                [
                    sg.Text("Blocks List"),
                    sg.Listbox(
                        values=blocks_data,
                        pad=(12, 2),
                        select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        key="-Vid_Any_Listing_List-",
                        size=(30, 10),
                        highlight_background_color="#00FF00",
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
                            key="-Vid_Average_Colour_Popup-",
                            enable_events=True
                        ),
                        sg.Listbox([
                            "Linear Average",
                            "Root Mean Square Average",
                            "HSL Average",
                            "HSV Average",
                            "LAB Average",
                            "Dominant Color"
                        ], default_values=["Linear Average"], size=(20, 4), key="-Vid_Color_Set-")
                    ],
                    [
                        sg.Text(
                            "Color Comparison Algorithm (?)",
                            tooltip="Changes how each individual pixel's rgb value is compared to "
                                    "each block's average color",
                            text_color="#AAAAFF",
                            key="-Vid_Color_Difference_Popup-",
                            enable_events=True
                        ),
                        sg.Listbox([
                            "Absolute Difference",
                            "Euclidean Difference",
                            "Weighted Euclidean",
                            "Redmean Difference",
                            "CIE76 DelE"
                        ], default_values=["Absolute Difference"], size=(20, 4), key="-Vid_Comparison_Method-")
                    ]
                ])]
            ], key="-Vid_Any_Block_Key-", visible=False),
        ],
        [
            sg.Text("Output: "),
            sg.Input(enable_events=True, key="-Vid_Output_Path-", size=30),
            sg.FileSaveAs("Save as", file_types=(("Video Files", "*.mp4"),))
        ],
        [sg.Text("Advance Options ∧", key="-Advance_Dropdown-", enable_events=True)],
        [
            sg.Column([
                [
                    sg.Text("Process Count"), sg.Spin(
                        [i+1 for i in range(16)],
                        initial_value=2,
                        key="-Process_Count-",
                    ),
                    sg.Text("May cause issues\nwith high process counts.")
                ],
            ], visible=False, key='-Advance_Options-')
        ],
        [
            sg.Button("Run", key="-Vid_Run-")
        ],
        [
            sg.T("", size=(1, 12))
        ]
    ], key="-Vid_Attrs-", visible=False, scrollable=True, size=(500, 350))

    # Progress meters to check the video's conversion progress
    Progress_Meters = sg.Column([
        [sg.T("Video Image Conversion")],
        [sg.Progress(max_value=2, orientation='horizontal', size=(20, 10), key='-Images_Vid_Conversion-')],
        [sg.T("Frames Converted")],
        [
            sg.Progress(max_value=100, orientation='horizontal', size=(20, 10), key='-Number_Of_Frames-'),
            sg.Text("0/0", key="-Number_Of_Frames_Text-")
        ],
        [sg.T("Singular Frame Progress")],
        [sg.Progress(max_value=100, orientation='horizontal', size=(20, 10), key='-Single_Frame-')],
        [sg.Image(size=(50, 50), key='-Progress_Gif-')]
    ], key='-Vid_Progress_Meters-', visible=False)

    # The area to load the Video
    VTS_Videoloader = sg.Column([
        [
            sg.Text(text="HI!")
        ],
        [sg.Text('Filename')],
        [
            sg.Input(enable_events=True, key="-Vid Text Entered-"),
            sg.FileBrowse(tooltip="Browse for an Video", file_types=(("Video Files", "*.mp4;*.mpeg;*.mkv"),))
        ],
        [sg.Button("Load", disabled=True, key="-Submit_VTS-")],
        [
            sg.HorizontalSeparator()
        ],
        [
            Progress_Meters
        ]

    ])

    # The full video tab layout
    VTS_layout = [[
        VTS_Videoloader, sg.VerticalSeparator(), VTS_vid_attributes
    ]]

    return VTS_layout
