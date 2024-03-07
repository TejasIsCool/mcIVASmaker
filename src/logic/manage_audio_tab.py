import random
import src.ui_manager.PySimpleGUI as sg
# Extra variables
text_list = [
    'Oi', 'Oii', 'Stop it!',
    'Cant you read?', 'Just stop it already!',
    'OIIIIIII', 'Hellloooooo? Stop it!',
    'Ok this is the 3rd last warning',
    'Second Last Warning',
    'You know what, you dont get a last warning. Bye!'
]

extra_chars = list("~!@#$%^&*_+`:;<>,.?/")
all_chars = list("qwertyuiopasdfghjklzxcvbnm1234567890-=[]\\;',./~!@#$%^&*()_+{}:\"?><|")
text_iter = - 1
anger_level = 0
currently_angry = False
over_time = False
wait_time = 0
waiting_time = 120
goodbye = False
tab_close = False
rate_of_wait = 1


def manage_audio_tab(window, event, values):
    global text_iter, anger_level, wait_time, currently_angry, waiting_time, goodbye, over_time, tab_close, rate_of_wait
    if not goodbye:
        if event == "-Audio_Easter_Egg-" and waiting_time >= -100:

            text_iter += 1
            text_to_show = text_list[text_iter % len(text_list)] + "".join(
                [random.choice(extra_chars) for _ in range(anger_level)])
            # We shall shuffle!
            for i in range(anger_level):
                text_to_show = random_character_swapper(text_to_show)

            if text_iter % len(text_list) == (len(text_list) - 1):
                anger_level += 1
                currently_angry = True
                window['-Audio_Easter_Egg-'](disabled=True)
                window['-Audio_Easter_Egg-'](button_color="#404040")
                window['-Audio_Easter_Egg-'].Widget.configure(disabledforeground='#9e9e9e')
                wait_time = 0
            window['-Audio_Easter_Egg-'](text=text_to_show)

        if event == '__TIMEOUT__' and currently_angry:
            wait_time += 1
            if waiting_time < -100 and 405 > wait_time > 200:
                window['-Audio_Easter_Egg-'](text="You just cant stop")
            elif waiting_time < -100 and 625 > wait_time > 405:
                window['-Audio_Easter_Egg-'](text="I suppose i have to step in at some time")
            elif waiting_time < -100 and 805 > wait_time > 625:
                window['-Audio_Easter_Egg-'](text="Its over now.")
            elif waiting_time < -100 and 1065 > wait_time > 805:
                window['-Audio_Easter_Egg-'](text="Goodbye")
            elif waiting_time < -100 and 1200 > wait_time > 1065:
                window['-Audio_Easter_Egg-'](visible=False)
                goodbye = True
                wait_time = 0

            elif wait_time > waiting_time and not over_time:
                currently_angry = False
                waiting_time -= 10
                window['-Audio_Easter_Egg-'](disabled=False)
                window['-Audio_Easter_Egg-'](button_color=sg.DEFAULT_BUTTON_COLOR)

        if waiting_time < -100 and not over_time:
            window['-Audio_Easter_Egg-'](disabled=True)
            window['-Audio_Easter_Egg-'](text="Wow")
            currently_angry = True
            over_time = True
            wait_time = 0

    if goodbye and not tab_close:
        wait_time += rate_of_wait
        if wait_time < 5000:
            if wait_time % 10 == 0:
                for obj in window['-Audio_Frame-'].Rows:
                    if 'DisplayText' in dir(obj[0]):
                        display_text = obj[0].DisplayText
                        if wait_time % 30 == 0:
                            display_text += random.choice(all_chars)
                        new_display_text = random_character_swapper(display_text)
                        obj[0](value=new_display_text)
                tab_title = window['-Audio_Tab-'].Title
                if wait_time % 50 == 0:
                    tab_title += random.choice(all_chars)
                new_tab_title = random_character_swapper(tab_title)
                window['-Audio_Tab-'](title=new_tab_title)
            if wait_time % 200 == 0:
                rate_of_wait = 5 if rate_of_wait < 5 else rate_of_wait
            if wait_time % 400 == 0:
                rate_of_wait = 10 if rate_of_wait < 10 else rate_of_wait
            if wait_time % 800 == 0:
                rate_of_wait = 50
        else:
            rate_of_wait = 1
            if wait_time-5000 < 2:
                for obj in window['-Audio_Frame-'].Rows:
                    if 'DisplayText' in dir(obj[0]):
                        obj[0](value="Bye")
                window['-Audio_Tab-'](title="Bye!")
            if wait_time-5000 == 100:
                window['-Audio_Tab-'](visible=False)
                tab_close = True


def random_character_swapper(text: str) -> str:
    pos1 = random.randrange(0, len(text))
    pos2 = random.randrange(0, len(text))
    while pos2 == pos1:
        pos2 = random.randrange(0, len(text))
    list_text_to_shot = list(text)
    if pos1 > pos2:
        pos1, pos2 = pos2, pos1
    list_text_to_shot.insert(pos1, list_text_to_shot.pop(pos2))
    list_text_to_shot.insert(pos2, list_text_to_shot.pop(pos1 + 1))
    return "".join(list_text_to_shot)
