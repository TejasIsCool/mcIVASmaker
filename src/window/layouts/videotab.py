from ui_manager import PySimpleGUI as sg
import textwrap


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
            sg.Column([
                [
                    sg.Text("Brightness Required", key="-Vid_List_Text-"),
                    sg.Combo(
                        ["None", "Whitelist", "Blacklist"],
                        key="-Vid_Any_Options-",
                        default_value="None",
                        visible=False,
                        readonly=True,
                        background_color="#00000000",
                        enable_events=True
                    ),
                    sg.Slider(
                        range=(0, 255),
                        default_value=127,
                        orientation="horizontal",
                        key="-Vid_Brightness-",
                        enable_events=True
                    )
                ],
                [
                    sg.Text("Blocks side", key="-Vid_Any_Side_Text-", visible=False),
                    sg.Combo(
                        ["Top", "Bottom", "Front", "Back", "Side"],
                        key="-Vid_Any_Side-",
                        default_value="Top",
                        visible=False,
                        readonly=True,
                        background_color="#00000000",
                        enable_events=True
                    )
                ]
            ]
            ),
            sg.Column([
                [
                    sg.Text("Blocks List", visible=False, key="-Vid_Any_Listing_Text-")
                ],
                [
                    sg.Multiline(key="-Vid_Any_Listing-", size=(10, 8), visible=False)
                ]
            ]),
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
