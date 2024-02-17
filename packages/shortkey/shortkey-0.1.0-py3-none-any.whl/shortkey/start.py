import json
import os
import pprint
import sys
import threading
from functools import partial

import pystray
from loguru import logger
from PIL import Image
from pynput import keyboard
from pynput.keyboard import Controller
from pystray import MenuItem as menu_item

from .res_path import ICON_PATH, KEY_PATH

# 키 상태를 추적하기 위한 집합
is_active = True
is_quit = False


def create_image(imgFilePath, width, height):
    # 이미지 파일을 엽니다
    image = Image.open(imgFilePath)
    # 이미지 크기를 지정된 너비와 높이로 조정합니다
    resized_image = image.resize((width, height))
    return resized_image


def try_quit():
    global is_quit
    is_quit = True


def toggle_activation():
    global is_active
    is_active = not is_active
    if is_active:
        logger.info("Program re-activated")
    else:
        logger.info("Program suspended")


def launch(param):
    global is_active
    if is_active:
        logger.info(f"launch {param}")
        os.system(param)


def is_alpha_numeric(char):
    # 길이가 1인 문자열인지 확인
    if len(char) == 1:
        # 알파벳 또는 숫자인지 확인
        return char.isalnum()
    else:
        return False


def parse_keys(item):
    keys = item.split("+")
    key_values = []
    for key in keys:
        key = key.replace("<", "").replace(">", "")
        if key in keyboard.Key.__members__.keys():
            key_values.append(keyboard.Key.__members__[key])
        elif is_alpha_numeric(key):
            key_values.append(keyboard.KeyCode(char=key))
    return key_values


def parse_defined_keys(keyList):
    key_dict = {}
    for item in keyList:
        if item["type"] == "launch":
            value = parse_keys(item["key"])
            key_dict[item["key"]] = {
                "parsed_key": value,
                "cmd": partial(launch, item["cmd"]),
            }
    return key_dict


def main():
    key_path = KEY_PATH
    global is_quit
    pressed_keys = set()
    with open(key_path, "r") as fp:
        json_key_list = json.load(fp)
    logger.info(pprint.pformat(json_key_list))
    # 이벤트 처리
    parsed_defined_keys = parse_defined_keys(json_key_list)
    with keyboard.Events() as events:
        for event in events:
            if is_quit is True:
                logger.info("is Quit -- ")
                break
            if event.key == keyboard.Key.esc:
                is_quit = True
                logger.info("will finished")
                continue
            elif isinstance(event, keyboard.Events.Press):
                pressed_keys.add(event.key)
                for key, defined_keyDict in parsed_defined_keys.items():
                    if all(
                        _key in pressed_keys for _key in defined_keyDict["parsed_key"]
                    ):
                        logger.info(f"pressed - key:{defined_keyDict['parsed_key']}")
                        defined_keyDict["cmd"]()
                        break
                if all(
                    _key in pressed_keys
                    for _key in [keyboard.Key.cmd, keyboard.Key.f10]
                ):
                    toggle_activation()
                if all(
                    _key in pressed_keys
                    for _key in [keyboard.Key.cmd, keyboard.Key.f13]
                ):
                    try_quit()
            elif isinstance(event, keyboard.Events.Release):
                try:
                    pressed_keys.remove(event.key)
                except KeyError:
                    pass
            else:
                pass


class MyIcon(pystray.Icon):
    def __init__(self):
        menu = (menu_item("start", self.on_start), menu_item("quit", self.on_quit))
        super().__init__("ShortKey", create_image(ICON_PATH, 64, 64), "ShortKey", menu)
        self.hotkey_thread = threading.Thread(target=main, args=(KEY_PATH,))

    def run_main(self):
        main()

    def on_start(self, item):
        logger.info("on_start")
        main()
        self.hotkey_thread.start()

    def on_quit(self, item):
        global is_quit
        logger.info("on_quit")
        is_quit = True
        _keyboard = Controller()
        _keyboard.press(keyboard.Key.cmd)
        _keyboard.press(keyboard.Key.f13)
        _keyboard.release(keyboard.Key.cmd)
        _keyboard.release(keyboard.Key.f13)
        self.hotkey_thread.join()
        self.stop()
        sys.exit(1)


def run_ui():
    icon = MyIcon()
    icon.run()


if __name__ == "__main__":
    icon = MyIcon()
    icon.run()
