'''
Pi-hole DNS traffic visualizer for the Raspberry Pi Sense HAT
By Sam Lindley, 2/21/2018
'''

def up_pushed(color):
    color_options = ('basic', 'traffic', 'ads')
    color_index = color_options.index(color)

    if color_index == 2:
        color_index = 0
    else:
        color_index += 1

    color = color_options[color_index]

    return color


def right_pushed(interval):
    interval_options = (10, 30, 60, 120, 180)
    interval_index = interval_options.index(interval)

    if interval_index == 4:
        interval_index = 0
    else:
        interval_index += 1

    interval = interval_options[interval_index]

    return interval


def down_pushed(lowlight):
    lowlight = False if lowlight else True

    return lowlight


def left_pushed(orientation):
    orientation_options = (0, 90, 180, 270)
    orientation_index = orientation_options.index(orientation)

    if orientation_index == 3:
        orientation_index = 0
    else:
        orientation_index += 1

    orientation = orientation_options[orientation_index]

    return orientation


def middle_pushed(randomize):
    randomize = False if randomize else True

    return randomize


def middle_held():
    if os.geteuid() == 0:
        LOGGER.info('Program terminated by user.')
    print('Program terminated by user.')

    SENSE.clear()

    sys.exit()
