#!/usr/bin/env python3

'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

import argparse
from itertools import cycle
import json
import logging
import os
from sense_hat import SenseHat
import sys
import time
import urllib.request

SENSE = SenseHat()
RIPPLE_SPEED = 0.025

if os.geteuid() == 0:
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.INFO)

    HANDLER = logging.FileHandler('/var/log/pihole-visualizer.log')
    FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    HANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(HANDLER)


def joystick_up_pushed(color):
    color_options = ('basic', 'traffic', 'ads')
    color_index = color_options.index(color)

    if color_index == 2:
        color_index = 0
    else:
        color_index += 1

    color = color_options[color_index]

    return color


def joystick_right_pushed(interval):
    interval_options = (10, 30, 60, 120, 180)
    interval_index = interval_options.index(interval)

    if interval_index == 4:
        interval_index = 0
    else:
        interval_index += 1

    interval = interval_options[interval_index]

    return interval


def joystick_down_pushed(lowlight):
    if lowlight:
        lowlight = False
    else:
        lowlight = True

    return lowlight


def joystick_left_pushed(orientation):
    orientation_options = (0, 90, 180, 270)
    orientation_index = orientation_options.index(orientation)

    if orientation_index == 3:
        orientation_index = 0
    else:
        orientation_index += 1

    orientation = orientation_options[orientation_index]

    return orientation


def joystick_middle_held():
    if os.geteuid() == 0:
        LOGGER.info('Program terminated by user.')
    print('Program terminated by user.')

    SENSE.clear()

    sys.exit()


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


def api_request(address):
    if not hasattr(api_request, "initial_connection"):
        api_request.initial_connection = True
    max_attempts = 300 if api_request.initial_connection else 30
    attempts = 0

    #retrieve and decode json data from server
    while True:
        try:
            if attempts == 0 and api_request.initial_connection:
                if os.geteuid() == 0:
                    LOGGER.info('Initiating connection with server.')
                print('Initiating connection with server.')
            with urllib.request.urlopen("http://%s/admin/api.php?summary&overTimeData10mins" % \
            address) as url:
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
                LOGGER.error('Invalid address for DNS server.')
            print("Error: Invalid address for DNS server. Try again.")
            sys.exit(1)

    if 'domains_over_time' not in raw_data or 'ads_over_time' not in raw_data:
        if os.geteuid() == 0:
            LOGGER.error('Invalid data returned from server. Ensure pihole-FTL service is running.')
        print('Error: Invalid data returned from server. Ensure pihole-FTL service is running.')
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


def spiral_graph(block_percentage, orientation, lowlight, x=3, y=3):
    grid_size = 64
    dx = 0
    dy = 1
    pivot_index = 0
    pivot_point = 1

    grid_units = int(grid_size * block_percentage)

    SENSE.clear()
    SENSE.set_rotation(orientation)
    SENSE.low_light = lowlight

    for i in range(grid_size):
        if i < grid_units:
            SENSE.set_pixel(x, 7 - y, (255, 0, 0))
        else:
            SENSE.set_pixel(x, 7 - y, (0, 0, 255))

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


def bar_chart(interval_data, color, orientation, lowlight):
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
    for row in range(0, 8):
        if info_chart[row][0] > 0:
            for col in range(0, info_chart[row][0]):
                #if color not set, default to red for all values
                if color == 'traffic':
                    SENSE.set_pixel(row, 7 - col, color_dict(info_chart[row][0]))
                    time.sleep(RIPPLE_SPEED)
                elif color == 'ads':
                    SENSE.set_pixel(row, 7 - col, color_dict(info_chart[row][1]))
                    time.sleep(RIPPLE_SPEED)
                elif color == 'basic':
                    SENSE.set_pixel(row, 7 - col, (255, 0, 0))
                    time.sleep(RIPPLE_SPEED)


def event_loop(args):
    modes = ('bar', 'spiral')
    cycler = cycle(modes)

    while True:
        joystick_event = False

        raw_data = api_request(args.address)
        block_percentage = float(raw_data['ads_percentage_today']) / 100
        interval_data = generate_interval_data(raw_data, args.interval)

        for _ in range(0, 15):
            mode = next(cycler)
            if  mode == 'bar':
                bar_chart(interval_data, args.color, args.orientation, args.lowlight)
            elif mode == 'spiral':
                spiral_graph(block_percentage, args.orientation, args.lowlight)

            for _ in range(0, 2):
                events = SENSE.stick.get_events()
                if events:
                    joystick_event = True
                    last_event = events[-1]
                    if last_event.direction == 'up':
                        args.color = joystick_up_pushed(args.color)
                        print("Color mode switched to '%s'." % args.color.capitalize())
                        break
                    elif last_event.direction == 'right':
                        args.interval = joystick_right_pushed(args.interval)
                        print("Time interval switched to %d minutes." % args.interval)
                        break
                    elif last_event.direction == 'down':
                        args.lowlight = joystick_down_pushed(args.lowlight)
                        print("Low-light mode", "enabled." if args.lowlight else \
                              "disabled.")
                        break
                    elif last_event.direction == 'left':
                        args.orientation = joystick_left_pushed(args.orientation)
                        print("Orientation switched to %d degrees." % args.orientation)
                        break
                    elif last_event.direction == 'middle' and last_event.action == 'held':
                        joystick_middle_held()

                time.sleep(1)

            if joystick_event:
                break


def main():
    parser = argparse.ArgumentParser(description="Generates a chart to display network traffic \
                                     on the Sense-HAT RGB display")

    parser.add_argument('-i', '--interval', action="store", choices=[10, 30, 60, 120, 180], \
                        type=int, default='60', help="specify interval time in minutes")
    parser.add_argument('-c', '--color', action="store", choices=['basic', 'traffic', 'ads'], \
                        default='basic', help="specify 'basic' to generate the default red \
                        chart, 'traffic' to represent the intensity of network traffic, or \
                        'ads' to represent the percentage of ads blocked")
    parser.add_argument('-a', '--address', action="store", default='127.0.0.1', help="specify \
                        address of DNS server, defaults to localhost")
    parser.add_argument('-o', '--orientation', action="store", choices=[0, 90, 180, 270], \
                        type=int, default='0', help="rotate graph to match orientation of RPi")
    parser.add_argument('-ll', '--lowlight', action="store_true", help="set LED matrix to \
                        light mode for use in dark environments")

    args = parser.parse_args()

    event_loop(args)


if __name__ == '__main__':
    main()
