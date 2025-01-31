# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import random
import time
import requests

import board
import displayio
import framebufferio
import terminalio
import rgbmatrix
from adafruit_display_text import label

displayio.release_displays()


matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

def changeable_label(value, color, x, y, suffix=""):
    group = displayio.Group()
    main_label = label.Label(terminalio.FONT, text=str(value), color=color,x=0,y=0)
    change_label = label.Label(terminalio.FONT, text="+0", color=0x00FF00, x=0,y=0)

    group.x = x
    group.y = y

    group.append(main_label)
    group.append(change_label)

    def onchange(new_value, suffix=""):
        if not suffix or not main_label.text or not main_label.text[:-len(suffix)]:
            old_value = int(main_label.text)
        else:
            old_value = int(main_label.text[:-len(suffix)])

        main_label.text = str(new_value) + suffix

        change = new_value - old_value
        if change > 0:
            change_label.text = f"+{change}{suffix}"
            change_label.color = 0x00FF00
        elif change < 0:
            change_label.text = str(change) + suffix
            change_label.color = 0xFF0000
        else:
            change_label.text = "0" + suffix
            change_label.color = 0x555555

        change_label.x = 64 - (change_label.bounding_box[2] - change_label.bounding_box[0])

    onchange(value, suffix)
    
    group.onchange = onchange

    return group

def c(group, value, suffix=""):
    group.onchange(value, suffix)



money_group = displayio.Group()

sales_label = changeable_label(0, 0xFFFFFF, 0, 3, "€")
charity_label = changeable_label(0, 0x00FF00, 0, 13, "€")
money_group.append(charity_label)
money_group.append(sales_label)



articles_group = displayio.Group()

articles_label = changeable_label(0, 0xFFFFFF, 0, 3)
imported_label = changeable_label(0, 0xFFFFFF, 0, 13)
sold_label = changeable_label(0000, 0xFFFFFF, 0, 23)

articles_group.append(articles_label)
articles_group.append(imported_label)
articles_group.append(sold_label)


data = {}

def request_data():
    global data
    d = requests.get("https://ksb.unser.dns64.de/api/display?token=hfjkdhjh543ktjrebgfdfds")
    data = d.json()

def parse_data():
    c(articles_label, data["amount_articles"])
    c(imported_label, data["imported"])
    c(sold_label, data["sold"])

    c(sales_label, data["sold_value"], "€")
    c(charity_label, int(data["sold_value"] * 0.2), "€")

FRAMES = 30

scenes = [money_group, articles_group]
current_scene = 0
last_switch = 0
last_refresh = 0


def switch():
    global current_scene, last_switch

    display.root_group = scenes[current_scene]
    current_scene = (current_scene + 1) % len(scenes)
    last_switch = time.time()

switch()

while True:
    if time.time() - last_switch > 5:
        request_data()
        parse_data()
        switch()

    display.refresh(minimum_frames_per_second=FRAMES)
    time.sleep(1.0 / FRAMES)
