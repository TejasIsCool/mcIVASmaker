from ui_manager import PySimpleGUI as sg
import textwrap


def get_image_tab(window_size:list[int]):
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
            sg.Column([
                [
                    sg.Text("Brightness Required", key="-Img_List_Text-"),
                    sg.Combo(
                        ["None", "Whitelist", "Blacklist"],
                        key="-Img_Any_Options-",
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
                        key="-Image_Brightness-",
                        enable_events=True
                    )
                ],
                [
                    sg.Text("Blocks side", key="-Img_Any_Side_Text-", visible=False),
                    sg.Combo(
                        ["Top", "Bottom", "Front", "Back", "Side"],
                        key="-Img_Any_Side-",
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
                    sg.Text("Blocks List", visible=False, key="-Img_Any_Listing_Text-")
                ],
                [
                    sg.Multiline(key="-Img_Any_Listing-", size=(20, 8), visible=False)
                ]
            ]),
        ],
        [
            sg.Checkbox("With power sources?", default=False, visible=False, key="-Img_Lamps_Schem_Check-")
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
    ], key="-Img_Attrs-", visible=False, scrollable=True, size=(int(window_size[0]/1.4), int(window_size[1]/1.4)))

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
