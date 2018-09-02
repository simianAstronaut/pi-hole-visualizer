#!/usr/bin/env python3

'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

import argparse
from itertools import cycle
import operator
import random
import time

import config
import joystick
import requests
import utils

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

    config.SENSE.clear()
    config.SENSE.set_rotation(orientation)
    config.SENSE.low_light = lowlight

    for row in random.sample(range(0, 7), 7) if randomize else range(6, -1, -1):
        for col in random.sample(icon[row], len(icon[row])) if randomize else icon[row]:
            config.SENSE.set_pixel(col, row, color)
            if randomize:
                time.sleep(config.RIPPLE_SPEED)
        if not randomize:
            time.sleep(config.RIPPLE_SPEED * 8)


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

    config.SENSE.clear()
    config.SENSE.set_rotation(orientation)
    config.SENSE.low_light = lowlight

    #set pixel values on rgb display
    for col in random.sample(range(0, 8), 8) if randomize else range(0, 8):
        if info_chart[col][0] > 0:
            for row in random.sample(range(0, info_chart[col][0]), info_chart[col][0]) if \
                randomize else range(0, info_chart[col][0]):
                #if color not set, default to red for all values
                if color == 'traffic':
                    config.SENSE.set_pixel(col, 7 - row, utils.color_dict(info_chart[col][0]))
                    time.sleep(config.RIPPLE_SPEED)
                elif color == 'ads':
                    config.SENSE.set_pixel(col, 7 - row, utils.color_dict(info_chart[col][1]))
                    time.sleep(config.RIPPLE_SPEED)
                elif color == 'basic':
                    config.SENSE.set_pixel(col, 7 - row, (255, 0, 0))
                    time.sleep(config.RIPPLE_SPEED)


def spiral_graph(block_percentage, orientation, lowlight, randomize, x=3, y=3):
    grid_size = 64
    grid_list = []
    dx = 0
    dy = 1
    pivot_index = 0
    pivot_point = 1

    grid_units = int(grid_size * block_percentage)

    if not randomize:
        config.SENSE.clear()
    config.SENSE.set_rotation(orientation)
    config.SENSE.low_light = lowlight

    for i in range(grid_size):
        if i < grid_units:
            if randomize:
                grid_list.append((x, 7 - y, (255, 0, 0)))
            else:
                config.SENSE.set_pixel(x, 7 - y, (255, 0, 0))
        else:
            if randomize:
                grid_list.append((x, 7 - y, (0, 0, 255)))
            else:
                config.SENSE.set_pixel(x, 7 - y, (0, 0, 255))

        if not randomize:
            time.sleep(config.RIPPLE_SPEED)

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
        config.SENSE.clear()

        for pixel in random.sample(grid_list, grid_size):
            config.SENSE.set_pixel(pixel[0], pixel[1], pixel[2])

            time.sleep(config.RIPPLE_SPEED)


def bar_chart_horizontal(top_sources, color, orientation, lowlight, randomize):
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

    config.SENSE.clear()
    config.SENSE.set_rotation(orientation)
    config.SENSE.low_light = lowlight

    #set pixel values on rgb display
    for row in random.sample(range(0, 8), 8) if randomize else range(0, 8):
        if info_chart[row] > 0:
            for col in random.sample(range(0, info_chart[row]), info_chart[row]) if \
                randomize else range(0, info_chart[row]):
                if color == 'basic':
                    config.SENSE.set_pixel(col, row, (255, 0, 0))
                else:
                    config.SENSE.set_pixel(col, row, utils.color_dict(info_chart[row]))
                time.sleep(config.RIPPLE_SPEED)


def pie_chart(query_types, orientation, lowlight, randomize):
    query_colors = {
        "A (IPv4)": (0, 26, 65),        #navy
        "AAAA (IPv6)": (0, 180, 251),   #sky blue
        "ANY": (255, 132, 34),          #orange
        "SRV": (250, 101, 96),          #pink
        "SOA": (67, 108, 52),           #moss green
        "PTR": (142, 58, 137),          #purple
        "TXT": (255, 255, 255),         #white
    }
    query_types = query_types.copy()
    grid_size = 64
    grid_list = []
    counter = 0

    for category in query_types:
        query_types[category] = int((query_types[category] / 100) * grid_size)

    current_type = max(query_types, key=query_types.get)

    if not randomize:
        config.SENSE.clear()
    config.SENSE.set_rotation(orientation)
    config.SENSE.low_light = lowlight

    for row in range(0, 8):
        for col in range(4, 8):
            if counter < query_types[current_type]:
                if randomize:
                    grid_list.append((col, row, query_colors[current_type]))
                else:
                    config.SENSE.set_pixel(col, row, query_colors[current_type])
                last_valid = current_type
            else:
                del query_types[current_type]
                if query_types:
                    current_type = max(query_types, key=query_types.get)
                    if query_types[current_type]:
                        last_valid = current_type

                if randomize:
                    grid_list.append((col, row, query_colors[current_type] if \
                                     query_types[current_type] else query_colors[last_valid]))
                else:
                    config.SENSE.set_pixel(col, row, query_colors[current_type] if \
                                           query_types[current_type] else query_colors[last_valid])

            if not randomize:
                time.sleep(config.RIPPLE_SPEED)

            counter += 1

    for row in range(7, -1, -1):
        for col in range(3, -1, -1):
            if counter < query_types[current_type]:
                if randomize:
                    grid_list.append((col, row, query_colors[current_type]))
                else:
                    config.SENSE.set_pixel(col, row, query_colors[current_type])
                last_valid = current_type
            else:
                del query_types[current_type]
                counter = 0
                if query_types:
                    current_type = max(query_types, key=query_types.get)
                    if query_types[current_type]:
                        last_valid = current_type

                if randomize:
                    grid_list.append((col, row, query_colors[current_type] if \
                                     query_types[current_type] else query_colors[last_valid]))
                else:
                    config.SENSE.set_pixel(col, row, query_colors[current_type] if \
                                           query_types[current_type] else query_colors[last_valid])

            if not randomize:
                time.sleep(config.RIPPLE_SPEED)

            counter += 1

    if randomize:
        config.SENSE.clear()

        for pixel in random.sample(grid_list, grid_size):
            config.SENSE.set_pixel(pixel[0], pixel[1], pixel[2])

            time.sleep(config.RIPPLE_SPEED)


def event_loop(args, pw_hash):
    modes = ['icon', 'vertical', 'spiral']
    cycler = cycle(modes)


    while True:
        joystick_event = False

        status = requests.global_access()
        raw_data = requests.api_request(args.address, pw_hash)
        interval_data = generate_interval_data(raw_data, args.interval)

        block_percentage = float(raw_data['ads_percentage_today']) / 100

        if 'top_sources' in raw_data and 'querytypes' in raw_data:
            if len(modes) != 5:
                modes.extend(['horizontal', 'pie'])
        else:
            if len(modes) == 5:
                modes = [mode for mode in modes if mode not in ('horizontal', 'pie')]

        included = args.select
        if included:
            included = set(included)
            excluded = {1, 2, 3, 4, 5} - included

            for chart in sorted(excluded, reverse=True):
                if chart <= len(modes):
                    modes.pop(chart - 1)

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
                bar_chart_horizontal(raw_data['top_sources'], args.color, args.orientation, \
                                     args.lowlight, args.randomize)
            elif mode == 'pie':
                pie_chart(raw_data['querytypes'], args.orientation, args.lowlight, args.randomize)

            for _ in range(0, 2):
                events = config.SENSE.stick.get_events()
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


def main():
    parser = argparse.ArgumentParser(description="Displays Pi-hole statistics on the Raspberry Pi \
                                     Sense-HAT with multiple animations")

    parser.add_argument('-i', '--interval', action="store", choices=[10, 30, 60, 120, 180], \
                        type=int, default='60', help="specify interval time in minutes")
    parser.add_argument('-c', '--color', action="store", choices=['basic', 'traffic', 'ads'], \
                        default='basic', help="enter 'basic' to generate bar charts in the \
                        default red color, 'traffic' to color code based on level of DNS queries, \
                        or 'ads' to color code by ad block percentage.")
    parser.add_argument('-a', '--address', action="store", default='127.0.0.1', help="specify \
                        address of DNS server, defaults to localhost")
    parser.add_argument('-o', '--orientation', action="store", choices=[0, 90, 180, 270], \
                        type=int, default='0', help="rotate graph to match orientation of RPi")
    parser.add_argument('-ll', '--lowlight', action="store_true", help="set LED matrix to \
                        low-light mode for use in dark environments")
    parser.add_argument('-r', '--randomize', action="store_true", help="randomize order of \
                        pixels displayed")
    parser.add_argument('-s', '--select', nargs='+', choices=range(1, 6), type=int, \
                        help="specify which animations to display(1-5), with multiple items \
                        separated by a space")

    args = parser.parse_args()

    pw_hash = utils.retrieve_hash(args.address)

    event_loop(args, pw_hash)


if __name__ == '__main__':
    main()
