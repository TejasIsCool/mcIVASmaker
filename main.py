#!/usr/bin/env python
# PySimpleGui library: https://pypi.org/project/PySimpleGUI/
import os
import importlib.util

from src.logic import manage_events
from src.window import window as window_maker
import multiprocessing
import logging
from src.logger import configure_logging

if __name__ == "__main__":

    configure_logging()
    logging.info("This is the log console. Most events that take place will be shown here")

    # Py Installer SPlash manager
    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash

        pyi_splash.update_text('UI Loaded ...')
        pyi_splash.close()
        logging.info('Splash screen closed.')

    # Enable Multiprocessing to work in executable form
    multiprocessing.freeze_support()
    logging.debug("Multiprocessing freeze_support enabled")

    # Instantiate the window
    window = window_maker.make_window()
    logging.debug("Window instantiated")

    # Manage all its events
    manage_events.manage_events(window)
    # Finish up by removing from the screen
    window.close()
    logging.warning("The Program has been closed!")

