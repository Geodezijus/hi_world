from ocrapi import OCRApi
import pyperclip
from PIL import ImageGrab
import json
import os
from re import search
import speech_recognition as sr
from PIL import Image
import PySimpleGUI as sg


def setup_mic():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
    return r, mic


def capture_game(r, mic, name, window):

    with open('possible_options_capture') as file:
        options_list = file.read().split('\n')
    map_details = name
    window['--INFO--'].update(map_details)

    while True:
        try:
            print("Say something!")
            window['--TERMINAL--'].update("Say something!")
            with mic as source:
                audio = r.listen(source, phrase_time_limit=2, timeout=5)
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            window['--TERMINAL--'].update(f"You said: {text}")
            if text in options_list:
                map_details = map_details + text + '\n'
                window['--INFO--'].update(map_details)
                print('Value read')
                window['--TERMINAL--'].update('Value read')
            else:
                print('Read value does not match. Repeat')
                window['--TERMINAL--'].update('Read value does not match. Repeat')
            if text == 'done':
                with open(rf'permanenet_db/{name}.txt', 'w') as file:
                    file.write(map_details)
                break

        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            print("Error making request to speech recognition service: {0}".format(e))
        except sr.WaitTimeoutError:
            print('You are silent')


def resize_and_save(path_for_shot, width, map_name):
    test_image = Image.open(path_for_shot)

    # Calculate the new dimensions based on the original aspect ratio
    aspect_ratio = test_image.size[0] / test_image.size[1]
    new_width = width
    new_height = int(new_width / aspect_ratio)
    test_image = test_image.resize((new_width, new_height))
    file_path = rf'permanenet_db/{map_name}.png'
    test_image.save(file_path, 'PNG')
    return file_path


def _check_if_unique_map(window):
    print('Welcome to Capture Game')
    temp_image_path = r'temp_screenshots/screenshot.jpg'
    if os.path.exists(temp_image_path):
        # Delete the file if it exists
        os.remove(temp_image_path)
    image = ImageGrab.grabclipboard()
    # Save the image to a file
    image.save(temp_image_path)
    test_file, test_json = OCRApi.ocr_space_file(filename=temp_image_path, language='eng')
    print(json.dumps(test_json, indent=2))
    results_str = test_json['ParsedResults'][0]['ParsedText']
    match = search(r'(\w+)-(\w+)', results_str)
    if match:
        guess = match.group()
        map_name = guess.lower()
        picture_list = os.listdir('permanenet_db')
        if map_name not in picture_list:
            file_path = resize_and_save(temp_image_path, 1280, map_name)
            window['--IMAGE--'].update(file_path)
            return True, map_name
        else:
            return False, None
    else:
        return None, None


def simple_window():
    # Create the layout

    column_1 = [[sg.Image('Untitled_1280.png', key='--IMAGE--', size=(1440, 810))], [sg.Multiline(key='--INFO--', auto_refresh=True)]]
    column_2 = [[sg.Multiline(key='--TERMINAL--', auto_refresh=True)]]

    layout = [
        [sg.Column(column_1, element_justification='c'), sg.Column(column_2)]
    ]

    # Create the window
    window = sg.Window('My Window', layout, finalize=True)
    return window


if __name__ == '__main__':
    active_window = simple_window()
    r, mic = setup_mic()

    while True:
        try:
            active_window['--TERMINAL--'].update("Say something!")

            with mic as source:
                audio = r.listen(source, phrase_time_limit=5, timeout=20)
            text = r.recognize_google(audio)
            active_window['--TERMINAL--'].write(f"You said: {text}")
            active_window['--TERMINAL--'].update()
            print(f"You said: {text}")
            if text == 'exit':
                break
            if text == 'capture':
                result, name = _check_if_unique_map(active_window)
                if result is None:
                    active_window['--TERMINAL--'].update('redo the capture')
                    print('redo the capture')
                    continue
                elif result:
                    capture_game(r, mic, name, active_window)
                    active_window['--TERMINAL--'].update('Back to menu')
                    print('Back to menu')
                    continue
                elif not result:
                    active_window['--TERMINAL--'].update('already exists')
                    print('already exists')
                    continue
        except sr.UnknownValueError:
            active_window['--TERMINAL--'].write("Sorry, I couldn't understand what you said.")
            print("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            active_window['--TERMINAL--'].update("Error making request to speech recognition service: {0}".format(e))
            print("Error making request to speech recognition service: {0}".format(e))
        except sr.WaitTimeoutError:
            active_window['--TERMINAL--'].update('You are silent')
            print('You are silent')









# Check if the file "myfile.txt" exists
#if os.path.exists(temp_image_path):
#    # Delete the file if it exists
#    os.remove(temp_image_path)


test_file = OCRApi.ocr_space_file(filename='untitled.jpg', language='eng')