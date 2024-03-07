from src.ui_manager import PySimpleGUI as sg


def get_audio_tab() -> list:
    audio_tab_layout = [
        [sg.Frame(title="", layout=[
            [
                sg.Text(text="ATS!")
            ],
            [
                sg.Text(text="This is unfinished!")
            ],
            [
                sg.Text(text="Here is a button. Dont press it")
            ],
            [
                sg.Button(button_text="Button", key="-Audio_Easter_Egg-")
            ]], key="-Audio_Frame-")]
    ]
    return audio_tab_layout
