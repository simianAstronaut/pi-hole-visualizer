'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

import json
import os
import socket
import sys
import time
import urllib.request

import config

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
                    config.LOGGER.info('Initiating connection with server.')
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
                    config.LOGGER.error('Exceeded max attempts to connect with server.')
                print('Error: Exceeded max attempts to connect with server.')
                sys.exit(1)
        except urllib.error.URLError:
            if os.geteuid() == 0:
                config.LOGGER.error('Web server offline or invalid address entered.')
            print("Error: Web server offline or invalid address entered.")

            if attempts < max_attempts:
                time.sleep(1)
                continue
            else:
                sys.exit(1)

    if 'domains_over_time' not in raw_data or 'ads_over_time' not in raw_data or \
       'ads_percentage_today' not in raw_data:
        if os.geteuid() == 0:
            config.LOGGER.error('Invalid data returned from server. Check if pihole-FTL service is \
                         running.')
        print('Error: Invalid data returned from server. Check if pihole-FTL service is running.')
        sys.exit(1)

    if api_request.initial_connection:
        if os.geteuid() == 0:
            config.LOGGER.info('Successful connection with server.')
        print('Successful connection with server.')

    api_request.initial_connection = False

    return raw_data
