from ui_manager import PySimpleGUI as sg
from window.layouts import imagetab, videotab
from path_manager.pather import resource_path

# A custom decent theme
DecentGrey = {
    'BACKGROUND': '#303030',
    'TEXT': '#ffffff',
    'INPUT': '#404040',
    'TEXT_INPUT': '#ffffff',
    'SCROLL': '#707070',
    'BUTTON': ('#ffffff', '#505050'),
    'PROGRESS': ('#505F69', '#32414B'),
    'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
}
sg.theme_add_new('DecentGrey', DecentGrey)
sg.theme('DecentGrey')


def make_window():
    # Making sure the window size is alright
    # sg.Window.get_screen_size returns the actual screen size
    window_size = [1280, 720]
    if window_size[0] > sg.Window.get_screen_size()[0]:
        window_size[0] = sg.Window.get_screen_size()[0]

    if window_size[1] > sg.Window.get_screen_size()[1]:
        window_size[1] = sg.Window.get_screen_size()[1]

    # The layout for the Image Tab
    ITS_layout = imagetab.get_image_tab(window_size)
    # Layout for Video Tab
    VTS_layout = videotab.get_video_tab()
    # Layout for Audio Tab
    # TODO
    ATS_layout = [
        [
            sg.Text(text="ATS!")
        ],
        [
            sg.Text(text="This is unfinished!")
        ]
    ]

    # Joining all the layouts to one Layout
    layout = [
        [sg.Titlebar(title="IVAS-Maker", background_color="#2E2E2E", icon=resource_path("./assets/icon/IVASMaker_Icon_Tiny.png"))],
        # [sg.Col([[sg.Text("IVAS-Maker", text_color="#FFFFFF", background_color="#2E2E2E", grab=True)]],
        #         pad=(0, 0), background_color="#2e2e2e")],
        [
            sg.TabGroup([[
                sg.Tab('Image Stuff', ITS_layout),
                sg.Tab('Video Stuff', VTS_layout),
                sg.Tab('Audio Stuff', ATS_layout)
            ]])
        ],
        [
            sg.Button("QUIT!")
        ]
    ]

    # Loading the cool icon
    with open(resource_path("./assets/icon/icon_base64.txt"), "rb") as f:
        icon_base64 = f.read()

    # Note, i hav commented out a few lines in PySimpleGUI.py
    # To make the icon stuff appear on taskbar
    # Find wm_overrideredirect there ig

    # Instantiating the window
    main_window = sg.Window(
        'IVAS-Maker', layout,
        size=(window_size[0], window_size[1]),
        background_color="#1E1E1E",
        icon=icon_base64,
    )
    return main_window
