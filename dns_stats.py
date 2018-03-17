#!/usr/bin/env python3

'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

import argparse
import json
import logging
import sys
import time
import urllib.request
from sense_hat import SenseHat

sense = SenseHat()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('/var/log/pihole-visualizer.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#color code interval
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
    attempts = 0

    #retrieve and decode json data from server
    while True:
        try:
            if attempts == 0:
                logger.info('Initiating connection with server.')
                print('Initiating connection with server.')
            with urllib.request.urlopen("http://%s/admin/api.php?overTimeData10mins" % \
            address) as url:
                attempts += 1
                raw_data = json.loads(url.read().decode())
                break
        except json.decoder.JSONDecodeError:
            if attempts < 300:
                time.sleep(1)
                continue
            else:
                logger.error('Exceeded max attempts to connect with server.')
                print('Error: Exceeded max attempts to connect with server.')
                sys.exit(1)
        except urllib.error.URLError:
            logger.error('Invalid address for DNS server.')
            print("Error: Invalid address for DNS server. Try again.")
            sys.exit(1)

    if 'domains_over_time' not in raw_data or 'ads_over_time' not in raw_data:
        logger.error('Invalid data returned from server. Ensure pihole-FTL service is running.')
        print('Error: Invalid data returned from server. Ensure pihole-FTL service is running.')
        sys.exit(1)

    logger.info('Successful connection with server.')
    print('Successful connection with server.')

    return raw_data

def organize_data(raw_data, interval):
    clean_data = []
    key_count = 0
    domains = 0
    ads = 0

    #sort and reverse data so that latest time intervals appear first in list
    for key in sorted(raw_data['domains_over_time'].keys(), reverse=True):
        if interval == 10:
            domains = raw_data['domains_over_time'][key]
            ads = raw_data['ads_over_time'][key]
            clean_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
        else:
            if interval == 30:
                if key_count > 0 and key_count % 3 == 0:
                    clean_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
                    domains = 0
                    ads = 0
            elif interval == 60:
                if key_count > 0 and key_count % 6 == 0:
                    clean_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
                    domains = 0
                    ads = 0
            elif interval == 120:
                if key_count > 0 and key_count % 12 == 0:
                    clean_data.append([domains, (ads / domains) * 100 if domains > 0 else 0])
                    domains = 0
                    ads = 0
            domains += raw_data['domains_over_time'][key]
            ads += raw_data['ads_over_time'][key]
            key_count += 1

    #extract a slice of the previous 24 hours
    if interval == 10:
        clean_data = clean_data[:144]
    elif interval == 30:
        clean_data = clean_data[:48]
    elif interval == 60:
        clean_data = clean_data[:24]
    elif interval == 120:
        clean_data = clean_data[:12]

    return clean_data

def generate_chart(clean_data, color, ripple, orientation, lowlight):
    info_chart = []
    domain_min = clean_data[0][0]
    domain_max = clean_data[0][0]
    ad_min = clean_data[0][1]
    ad_max = clean_data[0][1]

    #calculate minimum, maximum, and interval values to scale graph appropriately
    for i in clean_data:
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
    for i in clean_data:
        info_chart.append([int((i[0] - domain_min) / domain_interval) if domain_interval > 0 \
                           else 0, int((i[1] - ad_min) / ad_interval) if ad_interval > 0 else 0])
    info_chart = list(reversed(info_chart[:8]))

    sense.clear()
    sense.set_rotation(orientation)
    sense.low_light = lowlight

    #set pixel values on rgb display
    for row in range(0, 8):
        if info_chart[row][0] > 0:
            for col in range(0, info_chart[row][0]):
                #if color not set, default to red for all values
                if color == 'traffic':
                    sense.set_pixel(row, 7 - col, color_dict(info_chart[row][0]))
                    if ripple:
                        time.sleep(0.01)
                elif color == 'ads':
                    sense.set_pixel(row, 7 - col, color_dict(info_chart[row][1]))
                    if ripple:
                        time.sleep(0.01)
                elif color == 'basic':
                    sense.set_pixel(row, 7 - col, (255, 0, 0))
                    if ripple:
                        time.sleep(0.01)

def main():
    parser = argparse.ArgumentParser(description="Generates a chart to display network traffic \
                                     on the sense-hat RGB display")

    parser.add_argument('-i', '--interval', action="store", choices=[10, 30, 60, 120], \
                        type=int, default='60', help="specify interval time in minutes")
    parser.add_argument('-c', '--color', action="store", choices=['basic', 'traffic', 'ads', 'alternate'], \
                        default='basic', help="specify 'basic' to generate the default red chart, 'traffic' to \
                        represent the level of network traffic, 'ads' to represent the percentage \
                        of ads blocked, or 'alternate' to switch between traffic level and ad block percentage")
    parser.add_argument('-r', '--ripple', action="store_true", help="this option generates a \
                        ripple effect when producing the chart")
    parser.add_argument('-a', '--address', action="store", default='127.0.0.1', help="specify \
                        address of DNS server, defaults to localhost")
    parser.add_argument('-o', '--orientation', action="store", choices=[0, 90, 180, 270], \
                        type=int, default='0', help="rotate graph to match orientation of RPi")
    parser.add_argument('-ll', '--lowlight', action="store_true", help="set LED matrix to \
                        light mode for use in dark environments")

    args = parser.parse_args()

    if args.color == 'alternate':
        color = 'traffic'
    else:
        color = args.color

    while True:
        raw_data = api_request(args.address)
        clean_data = organize_data(raw_data, args.interval)

        if args.color == 'alternate':
            for i in range(0, 15):
                color = 'ads' if color == 'traffic' else 'traffic'
                generate_chart(clean_data, color, args.ripple, args.orientation, args.lowlight)
                time.sleep(2)
        else:
            generate_chart(clean_data, color, args.ripple, args.orientation, args.lowlight)
            time.sleep(30)

if __name__ == '__main__':
    main()
