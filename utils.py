'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

import os
import re

import config

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
                    config.LOGGER.error("Pi-hole configuration file not found in default location '%s'." \
                                 % config_path)
                print("Pi-hole configuration file not found in default location '%s'." \
                      % config_path)

                return pw_hash
    else:
        env_pw = os.environ.get("WEBPASSWORD", None)

        if env_pw is None:
            if os.geteuid() == 0:
                config.LOGGER.warning("Environment variable containing password hash could not be found.")
            print("Environment variable containing password hash could not be found.")
        else:
            pw_hash = env_pw

        return pw_hash
