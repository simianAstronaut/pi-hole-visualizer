'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

import logging
import os

from sense_emu import SenseHat

SENSE = SenseHat()
RIPPLE_SPEED = 0.025

if os.geteuid() == 0:
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.INFO)

    HANDLER = logging.FileHandler('/var/log/pihole-visualizer.log')
    FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    HANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(HANDLER)
