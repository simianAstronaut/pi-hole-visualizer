#!/usr/bin/env python3

'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

import argparse
from itertools import cycle
import json
import logging
import operator
import os
import random
import re
import socket
import sys
import time
import urllib.request

from sense_hat import SenseHat

import joystick

SENSE = SenseHat()
RIPPLE_SPEED = 0.025

if os.geteuid() == 0:
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.INFO)

    HANDLER = logging.FileHandler('/var/log/pihole-visualizer.log')
    FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    HANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(HANDLER)


def color_dict(level):
    return {
        0 : (0, 0, 255),
        1 : (0, 128, 255),
        2 : (0, 255, 255),
        3 : (255, 128, 0),
        4 : (0, 255, 0),
        5 : (128, 255, 0),
        6 : (255, 255, 0),
        7 : (255, 128, 0),
        8 : (255, 0, 0),
    }[level]


def global_access(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (Google Public DNS A)
    Port: 53/TCP
    Service: domain
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


def api_request(address, pw_hash):
    if not hasattr(api_request, "initial_connection"):
        api_request.initial_connection = True
    max_attempts = 100 if api_request.initial_connection else 10
    attempts = 0
    query = "?summary&overTimeData10mins&getQueryTypes&getQuerySources&auth=%s" % pw_hash

    #retrieve and decode json data from server
    while True:
        try:
            if attempts == 0 and api_request.initial_connection:
                if os.geteuid() == 0:
                    LOGGER.info('Initiating connection with server.')
                print('Initiating connection with server.')
            with urllib.request.urlopen("http://%s/admin/api.php%s" % (address, query)) as url:
                attempts += 1
                raw_data = json.loads(url.read().decode())
                break
        except json.decoder.JSONDecodeError:
            if attempts < max_attempts:
                time.sleep(1)
                continue
            else:
                if os.geteuid() == 0:
                    LOGGER.error('Exceeded max attempts to connect with server.')
                print('Error: Exceeded max attempts to connect with server.')
                sys.exit(1)
        except urllib.error.URLError:
            if os.geteuid() == 0:
                LOGGER.error('Web server offline or invalid address entered.')
            print("Error: Web server offline or invalid address entered.")

            if attempts < max_attempts:
                time.sleep(1)
                continue
            else:
                sys.exit(1)

    if 'domains_over_time' not in raw_data or 'ads_over_time' not in raw_data or \
       'ads_percentage_today' not in raw_data:
        if os.geteuid() == 0:
            LOGGER.error('Invalid data returned from server. Check if pihole-FTL service is \
                         running.')
        print('Error: Invalid data returned from server. Check if pihole-FTL service is running.')
        sys.exit(1)

    if api_request.initial_connection:
        if os.geteuid() == 0:
            LOGGER.info('Successful connection with server.')
        print('Successful connection with server.')

    api_request.initial_connection = False

    return raw_data


def generate_interval_data(raw_data, interval):
    interval_data = []
    domains = 0
    ads = 0

    #sort and reverse data so that latest time intervals appear first in list
    for counter, key in enumerate(sorted(raw_data['domains_over_time'].keys(), reverse=True)):
        if interval == 10:
            domains = raw_data['domains_over_time'][key]
            ads = raw_data['ads_over_time'][key]
            interval_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
        else:
            if interval == 30:
                if counter > 0 and counter % 3 == 0:
                    interval_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
                    domains = 0
                    ads = 0
            elif interval == 60:
                if counter > 0 and counter % 6 == 0:
                    interval_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
                    domains = 0
                    ads = 0
            elif interval == 120:
                if counter > 0 and counter % 12 == 0:
                    interval_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
                    domains = 0
                    ads = 0
            elif interval == 180:
                if counter > 0 and counter % 18 == 0:
                    interval_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
                    domains = 0
                    ads = 0

            domains += raw_data['domains_over_time'][key]
            ads += raw_data['ads_over_time'][key]

    #extract a slice of the previous 24 hours
    if interval == 10:
        interval_data = interval_data[:144]
    elif interval == 30:
        interval_data = interval_data[:48]
    elif interval == 60:
        interval_data = interval_data[:24]
    elif interval == 120:
        interval_data = interval_data[:12]
    elif interval == 180:
        interval_data = interval_data[:8]

    return interval_data


def connectivity_icon(status, orientation, lowlight, randomize):
    color = (0, 255, 0) if status else (255, 0, 0)
    icon = [
        [1, 2, 3, 4, 5, 6],
        [0, 7],
        [2, 3, 4, 5],
        [1, 6],
        [3, 4],
        [2, 5],
        [3, 4]
    ]

    SENSE.clear()
    SENSE.set_rotation(orientation)
    SENSE.low_light = lowlight

    for row in random.sample(range(0, 7), 7) if randomize else range(6, -1, -1):
        for col in random.sample(icon[row], len(icon[row])) if randomize else icon[row]:
            SENSE.set_pixel(col, row, color)
            if randomize:
                time.sleep(RIPPLE_SPEED)
        if not randomize:
            time.sleep(RIPPLE_SPEED * 8)


def bar_chart_vertical(interval_data, color, orientation, lowlight, randomize):
    info_chart = []
    domain_min = interval_data[0][0]
    domain_max = interval_data[0][0]
    ad_min = interval_data[0][1]
    ad_max = interval_data[0][1]

    #calculate minimum, maximum, and interval values to scale graph appropriately
    for i in interval_data:
        if i[0] > domain_max:
            domain_max = i[0]
        elif i[0] < domain_min:
            domain_min = i[0]

        if i[1] > ad_max:
            ad_max = i[1]
        elif i[1] < ad_min:
            ad_min = i[1]

    domain_interval = (domain_max - domain_min) / 8
    ad_interval = (ad_max - ad_min) / 8

    #append scaled values to new list
    for i in interval_data:
        info_chart.append([int((i[0] - domain_min) / domain_interval) if domain_interval > 0 \
                           else 0, int((i[1] - ad_min) / ad_interval) if ad_interval > 0 else 0])

    #handles cases of incomplete data
    while len(info_chart) < 8:
        info_chart.append([0, 0])

    info_chart = list(reversed(info_chart[:8]))

    SENSE.clear()
    SENSE.set_rotation(orientation)
    SENSE.low_light = lowlight

    #set pixel values on rgb display
    for col in random.sample(range(0, 8), 8) if randomize else range(0, 8):
        if info_chart[col][0] > 0:
            for row in random.sample(range(0, info_chart[col][0]), info_chart[col][0]) if \
                randomize else range(0, info_chart[col][0]):
                #if color not set, default to red for all values
                if color == 'traffic':
                    SENSE.set_pixel(col, 7 - row, color_dict(info_chart[col][0]))
                    time.sleep(RIPPLE_SPEED)
                elif color == 'ads':
                    SENSE.set_pixel(col, 7 - row, color_dict(info_chart[col][1]))
                    time.sleep(RIPPLE_SPEED)
                elif color == 'basic':
                    SENSE.set_pixel(col, 7 - row, (255, 0, 0))
                    time.sleep(RIPPLE_SPEED)


def spiral_graph(block_percentage, orientation, lowlight, randomize, x=3, y=3):
    grid_size = 64
    grid_list = []
    dx = 0
    dy = 1
    pivot_index = 0
    pivot_point = 1

    grid_units = int(grid_size * block_percentage)

    if not randomize:
        SENSE.clear()
    SENSE.set_rotation(orientation)
    SENSE.low_light = lowlight

    for i in range(grid_size):
        if i < grid_units:
            if randomize:
                grid_list.append((x, 7 - y, (255, 0, 0)))
            else:
                SENSE.set_pixel(x, 7 - y, (255, 0, 0))
        else:
            if randomize:
                grid_list.append((x, 7 - y, (0, 0, 255)))
            else:
                SENSE.set_pixel(x, 7 - y, (0, 0, 255))

        if not randomize:
            time.sleep(RIPPLE_SPEED)

        if pivot_index == pivot_point:
            if dx == 0:
                dx, dy = dy, dx
                pivot_index = 0
            elif dy == 0:
                dx, dy = dy, -dx
                pivot_index = 0
                pivot_point += 1

        x += dx
        y += dy
        pivot_index += 1

    if randomize:
        SENSE.clear()

        for pixel in random.sample(grid_list, grid_size):
            SENSE.set_pixel(pixel[0], pixel[1], pixel[2])

            time.sleep(RIPPLE_SPEED)


def bar_chart_horizontal(top_sources, orientation, lowlight, randomize):
    source_list = []
    info_chart = []

    if len(top_sources) > 0:
        for source in sorted(top_sources.items(), key=operator.itemgetter(1), reverse=True):
            source_list.append(source[1])

        source_max = source_list[0]
        source_min = source_list[-1] if len(source_list) > 1 else 0
        source_interval = (source_max - source_min) / 8

        for source in source_list:
            info_chart.append(int((source - source_min) / source_interval))

    #handles cases of incomplete data
    while len(info_chart) < 8:
        info_chart.append(0)

    SENSE.clear()
    SENSE.set_rotation(orientation)
    SENSE.low_light = lowlight

    #set pixel values on rgb display
    for row in random.sample(range(0, 8), 8) if randomize else range(0, 8):
        if info_chart[row] > 0:
            for col in random.sample(range(0, info_chart[row]), info_chart[row]) if \
                randomize else range(0, info_chart[row]):
                SENSE.set_pixel(col, row, color_dict(info_chart[row]))
                time.sleep(RIPPLE_SPEED)


def pie_chart(ipv4_percentage, orientation, lowlight, randomize):
    grid_size = 64
    grid_list = []
    grid_units = int(grid_size * ipv4_percentage)
    counter = 0

    if not randomize:
        SENSE.clear()
    SENSE.set_rotation(orientation)
    SENSE.low_light = lowlight

    for row in range(0, 8):
        for col in range(4, 8):
            if counter < grid_units:
                if randomize:
                    grid_list.append((col, row, (255, 128, 0)))
                else:
                    SENSE.set_pixel(col, row, (255, 128, 0))
            else:
                if randomize:
                    grid_list.append((col, row, (128, 255, 0)))
                else:
                    SENSE.set_pixel(col, row, (128, 255, 0))

            if not randomize:
                time.sleep(RIPPLE_SPEED)

            counter += 1

    for row in range(7, -1, -1):
        for col in range(3, -1, -1):
            if counter < grid_units:
                if randomize:
                    grid_list.append((col, row, (255, 128, 0)))
                else:
                    SENSE.set_pixel(col, row, (255, 128, 0))
            else:
                if randomize:
                    grid_list.append((col, row, (128, 255, 0)))
                else:
                    SENSE.set_pixel(col, row, (128, 255, 0))

            if not randomize:
                time.sleep(RIPPLE_SPEED)

            counter += 1

    if randomize:
        SENSE.clear()

        for pixel in random.sample(grid_list, grid_size):
            SENSE.set_pixel(pixel[0], pixel[1], pixel[2])

            time.sleep(RIPPLE_SPEED)


def event_loop(args, pw_hash):
    modes = ['icon', 'vertical', 'spiral']
    cycler = cycle(modes)

    while True:
        joystick_event = False

        status = global_access()
        raw_data = api_request(args.address, pw_hash)
        interval_data = generate_interval_data(raw_data, args.interval)

        block_percentage = float(raw_data['ads_percentage_today']) / 100

        if 'top_sources' in raw_data and 'querytypes' in raw_data:
            if len(modes) != 4:
                modes.extend(['horizontal', 'pie'])
            ipv4_percentage = float(raw_data['querytypes']['A (IPv4)']) / 100

        for _ in range(0, 15):
            mode = next(cycler)
            if  mode == 'icon':
                connectivity_icon(status, args.orientation, args.lowlight, args.randomize)
            elif  mode == 'vertical':
                bar_chart_vertical(interval_data, args.color, args.orientation, args.lowlight, \
                          args.randomize)
            elif mode == 'spiral':
                spiral_graph(block_percentage, args.orientation, args.lowlight, args.randomize)
            elif mode == 'horizontal':
                bar_chart_horizontal(raw_data['top_sources'], args.orientation, args.lowlight, \
                                     args.randomize)
            elif mode == 'pie':
                pie_chart(ipv4_percentage, args.orientation, args.lowlight, args.randomize)

            for _ in range(0, 2):
                events = SENSE.stick.get_events()
                if events:
                    joystick_event = True
                    last_event = events[-1]

                    if last_event.direction == 'up':
                        args.color = joystick.up_pushed(args.color)
                        print("Color mode switched to '%s'." % args.color.capitalize())
                        break
                    elif last_event.direction == 'right':
                        args.interval = joystick.right_pushed(args.interval)
                        print("Time interval switched to %d minutes." % args.interval)
                        break
                    elif last_event.direction == 'down':
                        args.lowlight = joystick.down_pushed(args.lowlight)
                        print("Low-light mode", "enabled." if args.lowlight else \
                              "disabled.")
                        break
                    elif last_event.direction == 'left':
                        args.orientation = joystick.left_pushed(args.orientation)
                        print("Orientation switched to %d degrees." % args.orientation)
                        break
                    elif last_event.direction == 'middle' and last_event.action == 'released':
                        args.randomize = joystick.middle_pushed(args.randomize)
                        print("Randomization", "enabled." if args.randomize else "disabled.")
                        break
                    elif last_event.direction == 'middle' and last_event.action == 'held':
                        joystick.middle_held()

                time.sleep(1)

            if joystick_event:
                break


def parse_config(config_path):
    pw_hash = ''

    with open(config_path, 'r') as fp:
        try:
            for line in fp:
                hex_pattern = re.compile(r'WEBPASSWORD=([0-9a-fA-F]+)')
                match = re.match(hex_pattern, line)
                if match:
                    pw_hash = match.group(1)
                    return pw_hash
        except Exception:
            return pw_hash


def retrieve_hash(address):
    pw_hash = ''

    if address == '127.0.0.1':
        config_path = '/etc/pihole/setupVars.conf'

        if os.getegid() != 0:
            return pw_hash
        else:
            if os.path.exists(config_path):
                return parse_config(config_path)
            else:
                if os.geteuid() == 0:
                    LOGGER.error("Pi-hole configuration file not found in default location '%s'." \
                                 % config_path)
                print("Pi-hole configuration file not found in default location '%s'." \
                      % config_path)

                return pw_hash
    else:
        env_pw = os.environ.get("WEBPASSWORD", None)

        if env_pw is None:
            if os.geteuid() == 0:
                LOGGER.warning("Environment variable containing password hash could not be found.")
            print("Environment variable containing password hash could not be found.")
        else:
            pw_hash = env_pw

        return pw_hash


def main():
    parser = argparse.ArgumentParser(description="Generates a chart to display network traffic \
                                     on the Sense-HAT RGB display")

    parser.add_argument('-i', '--interval', action="store", choices=[10, 30, 60, 120, 180], \
                        type=int, default='60', help="specify interval time in minutes")
    parser.add_argument('-c', '--color', action="store", choices=['basic', 'traffic', 'ads'], \
                        default='basic', help="specify 'basic' to generate bar charts in the \
                        default red color, 'traffic' to color code based on level of DNS queries, \
                        or 'ads' to color code by ad block percentage.")
    parser.add_argument('-a', '--address', action="store", default='127.0.0.1', help="specify \
                        address of DNS server, defaults to localhost")
    parser.add_argument('-o', '--orientation', action="store", choices=[0, 90, 180, 270], \
                        type=int, default='0', help="rotate graph to match orientation of RPi")
    parser.add_argument('-ll', '--lowlight', action="store_true", help="set LED matrix to \
                        light mode for use in dark environments")
    parser.add_argument('-r', '--randomize', action="store_true", help="randomize order of \
                        pixels displayed")

    args = parser.parse_args()

    pw_hash = retrieve_hash(args.address)

    event_loop(args, pw_hash)


if __name__ == '__main__':
    main()
