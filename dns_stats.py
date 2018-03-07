#!/usr/bin/env python3

'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

import argparse
import json
from sense_hat import SenseHat
import sys
import time
import urllib.request

def dns_request(address):
    domain_info_hourly = []
    key_count = 0
    domains = 0
    ads = 0

    #retrieve and decode json data from pi-hole ftl daemon
    while True:
        try:
            with urllib.request.urlopen("http://%s/admin/api.php?overTimeData10mins" % \
            address) as url:
                data = json.loads(url.read().decode())
                break
        except json.decoder.JSONDecodeError:
            print('Server unresponsive, reattempting connection...')
            time.sleep(1)
            continue
        except urllib.error.URLError:
            print("Error: Invalid address for DNS server. Try again.")
            sys.exit(1)

    #sort and reverse data so that latest time intervals appear first in list
    for key in sorted(data['domains_over_time'].keys(), reverse=True):
        #aggregate data into hourly intervals
        if key_count > 0 and key_count % 6 == 0:
            domain_info_hourly.append([domains, (ads / domains) * 100 if domains > 0 else 0])
            domains = 0
            ads = 0
        domains += data['domains_over_time'][key]
        ads += data['ads_over_time'][key]
        key_count += 1

    #extract a slice of the previous 24 hours
    domain_info_hourly = domain_info_hourly[:24]

    return domain_info_hourly

#color code hourly interval
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

def generate_chart(data, color, ripple):
    info_chart = []
    domain_min = data[0][0]
    domain_max = data[0][0]
    ad_min = data[0][1]
    ad_max = data[0][1]

    #calculate minimum, maximum, and interval values to scale graph appropriately
    for hour in data:
        if hour[0] > domain_max:
            domain_max = hour[0]
        elif hour[0] < domain_min:
            domain_min = hour[0]

        if hour[1] > ad_max:
            ad_max = hour[1]
        elif hour[1] < ad_min:
            ad_min = hour[1]

    domain_interval = (domain_max - domain_min) / 8 
    ad_interval = (ad_max - ad_min) / 8

    #append scaled values to new list
    for hour in data:
        info_chart.append([int((hour[0] - domain_min) / domain_interval) if domain_interval > 0 \
                           else 0, int((hour[1] - ad_min) / ad_interval) if ad_interval > 0 else 0])
    info_chart = list(reversed(info_chart[:8]))

    sense = SenseHat()
    sense.clear()

    #set pixel values on rgb display
    for col in range(0, 8):
        if info_chart[col][0] > 0:
            for row in range(0, info_chart[col][0]):
                #if color not set, default to red for all values
                if color == 'traffic':
                    sense.set_pixel(row, col, color_dict(info_chart[col][0]))
                    if ripple:
                        time.sleep(0.01)
                elif color == 'ads':
                    sense.set_pixel(row, col, color_dict(info_chart[col][1]))
                    if ripple:
                        time.sleep(0.01)
                else:
                    sense.set_pixel(row, col, (255, 0, 0))
                    if ripple:
                        time.sleep(0.01)

def main():
    parser = argparse.ArgumentParser(description="Generates a chart to display network traffic \
                                     on the sense-hat RGB display")
    parser.add_argument('-c', '--color', action="store", choices=["traffic", "ads", "alternate"], \
                        help="specify 'traffic' to display level of network traffic, 'ads' to \
                        display percentage of ads blocked, or 'alternate' to switch between both")
    parser.add_argument('-r', '--ripple', action="store_true", help="this option generates a \
                        ripple effect when producing the chart")
    parser.add_argument('-a', '--address', action="store", default='127.0.0.1', help="specify \
                        address of DNS server, defaults to localhost")
    args = parser.parse_args()
    
    if args.color == 'alternate':
        color = 'traffic'
    else:
        color = args.color
    
    while True:
        domain_info_hourly = dns_request(args.address)
        if args.color == 'alternate':
            for i in range(0, 15):
                color = 'ads' if color == 'traffic' else 'traffic'
                generate_chart(domain_info_hourly, color, args.ripple)
                time.sleep(2)
        else:
            generate_chart(domain_info_hourly, color, args.ripple)
            time.sleep(30)

if __name__ == '__main__':
    main()
