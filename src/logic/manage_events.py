import ui_manager.PySimpleGUI as sg

from logic.manage_image_tab import manage_img_tab
from logic.manage_video_tab import manage_vid_tab


def manage_events(window: sg.Window):
    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read(timeout=20)
        # See if user wants to quit or window was closed
        if event in [sg.WINDOW_CLOSED, 'QUIT!']:
            break

        # Manage image events
        manage_img_tab(window, event, values)
        # Manage video events
        manage_vid_tab(window, event, values)
