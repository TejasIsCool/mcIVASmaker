import src.ui_manager.PySimpleGUI as sg

from src.logic.manage_image_tab import manage_img_tab
from src.logic.manage_video_tab import manage_vid_tab
from src.logic.manage_audio_tab import manage_audio_tab
from src.logic.popup_manager import manage_popups


def manage_events(window: sg.Window):
    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read(timeout=20)
        # See if user wants to quit or window was closed
        if event in [sg.WINDOW_CLOSED, 'QUIT!']:
            break

        if "Popup" in event:
            manage_popups(event)
        # Manage image events
        manage_img_tab(window, event, values)
        # Manage video events
        manage_vid_tab(window, event, values)
        # Manage audio events
        manage_audio_tab(window, event, values)

