# PySimpleGui library: https://pypi.org/project/PySimpleGUI/


from logic import manage_events
from window import window as window_maker

if __name__ == "__main__":
    # Instantiate the window
    window = window_maker.make_window()
    # Manage all its events
    manage_events.manage_events(window)
    # Finish up by removing from the screen
    window.close()
