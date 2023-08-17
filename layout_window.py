import PySimpleGUI as sg
from PIL import Image
import time
import os
from PIL import ImageGrab
from re import search
import json
from ocrapi import OCRApi


def resize_and_save(result, prereq_values):
    test_image = Image.open(prereq_values['temp_shot_jpg'])
    # Calculate the new dimensions based on the original aspect ratio
    aspect_ratio = test_image.size[0] / test_image.size[1]
    new_width = result['width']
    new_height = int(new_width / aspect_ratio)
    test_image = test_image.resize((new_width, new_height))
    test_image.save(result['image_path'], 'PNG')
    return result

def resize(width, image):

    # Calculate the new dimensions based on the original aspect ratio
    aspect_ratio = image.size[0] / image.size[1]
    new_width = width
    new_height = int(new_width / aspect_ratio)
    image = image.resize((new_width, new_height))
    return image

def save_image_corner(prereq_values, map_or_not):
    temp_image_path = prereq_values['temp_shot_jpg']
    temp_image_corner_path = prereq_values['temp_image_corner_path']
    img = Image.open(temp_image_path)
    if map_or_not:
        box = (300, 0, 700, 100)  # (left, upper, right, lower)
        # Crop the image
        cropped_img = img.crop(box)
        # Save the cropped image as a new file
        cropped_img.save(temp_image_corner_path)
    else:
        # Define the region to crop
        box = (1380, 760, 1920, 1000)  # (left, upper, right, lower)
        # Crop the image
        cropped_img = img.crop(box)
        # Save the cropped image as a new file
        cropped_img.save(temp_image_corner_path)




def _check_if_unique_map(prereq_values, map_or_not):
    result = {'match': True, 'unique': True, 'path': '', 'map_name': '', 'width': 1280, 'ocr': True}
    print('Welcome to Capture Game')
    temp_image_path = prereq_values['temp_shot_jpg']
    temp_image_png = prereq_values['temp_shot_png']
    temp_image_corner_path = prereq_values['temp_image_corner_path']
    if os.path.exists(temp_image_path):
        # Delete the file if it exists
        os.remove(temp_image_path)
    if os.path.exists(temp_image_png):
        os.remove(temp_image_png)
    if os.path.exists(temp_image_corner_path):
        os.remove(temp_image_corner_path)
    try:
        image = ImageGrab.grabclipboard()
        # Save the image to a file
        image.save(temp_image_path)
        image = resize(1280, image)
        image.save(temp_image_png, 'PNG')
    except AttributeError:
        result['unique'] = False
        result['match'] = False
        return result
    save_image_corner(prereq_values, map_or_not)
    test_file, test_json = OCRApi.ocr_space_file(filename=temp_image_corner_path, language='eng')
    print(json.dumps(test_json, indent=2))
    results_str = test_json['ParsedResults'][0]['ParsedText']
    match = search(r'(\w+)-(\w+)', results_str)
    if match:
        guess = match.group()
        map_name = guess.lower()
        picture_list = os.listdir('permanenet_db')
        map_name_ext = f'{map_name}.png'
        if map_name_ext not in picture_list:
            map_name_txt = f'{map_name}.txt'
            result['map_name'] = map_name
            result['image_path'] = os.path.join(prereq_values['perm_dir'], map_name_ext)
            result['txt_path'] = os.path.join(prereq_values['perm_dir'], map_name_txt)
            return result
        else:
            map_name_txt = f'{map_name}.txt'
            result['map_name'] = map_name
            result['image_path'] = os.path.join(prereq_values['perm_dir'], map_name_ext)
            result['txt_path'] = os.path.join(prereq_values['perm_dir'], map_name_txt)
            result['unique'] = False
            return result
    else:
        result['unique'] = False
        result['match'] = False
        return result


def check_if_exists_noOCR(prereq_values, typed_map_name):
    result = {'match': True, 'unique': True, 'path': '', 'map_name': '', 'width': 1280, 'ocr': False}
    print('Welcome to Capture Game')
    map_name = typed_map_name.lower()
    picture_list = os.listdir('permanenet_db')
    map_name_ext = f'{map_name}.png'
    if map_name_ext not in picture_list:
        map_name_txt = f'{map_name}.txt'
        result['map_name'] = map_name
        result['image_path'] = os.path.join(prereq_values['perm_dir'], map_name_ext)
        result['txt_path'] = os.path.join(prereq_values['perm_dir'], map_name_txt)
        return result
    else:
        map_name_txt = f'{map_name}.txt'
        result['map_name'] = map_name
        result['image_path'] = os.path.join(prereq_values['perm_dir'], map_name_ext)
        result['txt_path'] = os.path.join(prereq_values['perm_dir'], map_name_txt)
        result['unique'] = False
        return result


def use_api(temp_image_path, result):
        test_file, test_json = OCRApi.ocr_space_file(filename=temp_image_path, language='eng')
        print(json.dumps(test_json, indent=2))
        results_str = test_json['ParsedResults'][0]['ParsedText']
        match = search(r'(\w+)-(\w+)', results_str)
        if match:
            guess = match.group()
            map_name = guess.lower()
        else:
            result['unique'] = False
            result['match'] = False
            return result
        return map_name

def prereq_setup():
    data_dict = {}
    data_dict['cwd'] = os.getcwd()
    data_dict['init_image_path'] = os.path.join(data_dict['cwd'], 'Untitled_1280.png')
    data_dict['temp_shot_jpg'] = os.path.join(data_dict['cwd'], r'temp_screenshots\screenshot.jpg')
    data_dict['temp_shot_png'] = os.path.join(data_dict['cwd'], r'temp_screenshots\screenshot.png')
    data_dict['perm_dir'] = os.path.join(data_dict['cwd'], 'permanenet_db')
    data_dict['temp_image_corner_path'] = os.path.join(data_dict['cwd'], r'temp_screenshots\screenshot_corner.jpg')

    return data_dict


def simple_window(prereq_data):

    # Create the layout

    column_1 = [[sg.Image(prereq_data['init_image_path'], key='--IMAGE--', size=(1440, 810))],
                [sg.Button('Capture', key='--CAPTURE--'),
                 sg.Button('Capture map', key='--CAPTUREMAP--'),
                 sg.Button('Redo', key='--REDO--', disabled=True),
                 sg.Input('', key='--INPUT--'),
                 sg.Multiline(key='--INFO--', autoscroll=True, size=(30, 10)),
                 sg.Button('Check Map', key='--CHECK--', disabled=True),
                 sg.Button('Fill Details', key='--CONT--', disabled=True),
                 sg.Input('', key='--CORRECT_MAP--')]]
    column_2 = [[sg.Multiline(key='--DETAILS--', size=(30, 10))], [sg.Button('Done', key='--DONE--', disabled=True)]]

    layout = [
        [sg.Column(column_1, element_justification='c'), sg.Column(column_2, element_justification='c')]
    ]

    # Create the window
    window = sg.Window('My Window', layout, finalize=True)

    # Run the event loop to process events and display the window

    map_name = ''
    while True:
        window['--IMAGE--'].update(prereq_data['init_image_path'])
        window['--INFO--'].update(f'Welcome to starting page\n', append=True)
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '--CAPTURE--' or '--CAPTUREMAP--':
            correct_map = window['--INPUT--'].get()
            if (correct_map != '' or None) and search(r'(\w+)-(\w+)', correct_map):
                results = check_if_exists_noOCR(prereq_data, correct_map)
                window['--CAPTURE--'].update(disabled=True)
                window['--CAPTUREMAP--'].update(disabled=True)
            elif event == '--CAPTURE--':
                results = _check_if_unique_map(prereq_data, False)
                window['--CAPTURE--'].update(disabled=True)
                window['--CAPTUREMAP--'].update(disabled=True)
            elif event == '--CAPTUREMAP--':
                results = _check_if_unique_map(prereq_data, True)
                window['--CAPTURE--'].update(disabled=True)
                window['--CAPTUREMAP--'].update(disabled=True)

            if results['match']:
                if results['ocr']:
                    window['--IMAGE--'].update(prereq_data['temp_shot_png'])
                else:
                    window['--IMAGE--'].update(prereq_data['init_image_path'])
                if results['unique']:
                    window['--INFO--'].update(f'matched: {results["map_name"]}\n', append=True)
                    window['--CONT--'].update(disabled=False)
                    window['--REDO--'].update(disabled=False)
                    event, values = window.read()
                    if event == '--REDO--':
                        window['--CONT--'].update(disabled=True)
                        window['--REDO--'].update(disabled=True)
                        window['--CAPTURE--'].update(disabled=False)
                        window['--CAPTUREMAP--'].update(disabled=False)
                        continue
                    if event == '--CONT--':
                        fixed_map = window['--CORRECT_MAP--'].get()
                        if (fixed_map != '' or None) and search(r'(\w+)-(\w+)', fixed_map):
                            map_name_ext = f'{fixed_map}.png'
                            map_name_txt = f'{fixed_map}.txt'
                            results['image_path'] = os.path.join(prereq_data['perm_dir'], map_name_ext)
                            results['txt_path'] = os.path.join(prereq_data['perm_dir'], map_name_txt)
                            results["map_name"] = fixed_map
                            window['--CORRECT_MAP--'].update('')
                        window['--DONE--'].update(disabled=False)
                        window['--CONT--'].update(disabled=True)
                        window['--REDO--'].update(disabled=True)
                        window['--INFO--'].update(f'Filling: {results["map_name"]}\n', append=True)
                        resize_and_save(results, prereq_data)
                        event, values = window.read()
                        if event == '--DONE--':
                            with open(results['txt_path'], 'w') as file:
                                file.write(window['--DETAILS--'].get())
                                file.close()
                            window['--DETAILS--'].update('')
                            window['--INFO--'].update(f'Filled: {results["map_name"]}\n', append=True)
                            window['--CAPTURE--'].update(disabled=False)
                            window['--CAPTUREMAP--'].update(disabled=False)
                            window['--DONE--'].update(disabled=True)
                        if event == sg.WIN_CLOSED:
                            break
                    if event == sg.WIN_CLOSED:
                        break
                else:
                    window['--INFO--'].update('Already exists\n', append=True)
                    window['--CHECK--'].update(disabled=False)
                    window['--REDO--'].update(disabled=False)
                    event, values = window.read()
                    if event == '--CHECK--':
                        window['--IMAGE--'].update(results['image_path'])
                        details = open(results['txt_path'], 'r')
                        window['--DETAILS--'].update(details.read())
                        window['--CHECK--'].update(disabled=True)
                        event, values = window.read()
                        if event == '--REDO--':
                            window['--CHECK--'].update(disabled=True)
                            window['--REDO--'].update(disabled=True)
                            window['--CAPTURE--'].update(disabled=False)
                            window['--CAPTUREMAP--'].update(disabled=False)
                            window['--DETAILS--'].update('')
                            continue
            else:
                window['--INFO--'].update('Redo capture or type correct format\n', append=True)
                window['--CAPTURE--'].update(disabled=False)
                window['--CAPTUREMAP--'].update(disabled=False)

    # Close the window
    window.close()


if __name__ == '__main__':
    data_basic = prereq_setup()
    simple_window(data_basic)







