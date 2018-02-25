#!/usr/bin/python3
import sys
import json
import optparse
import urllib.request
from sense_hat import SenseHat

def dns_request(local_address):
    domain_info_mins = []
    domain_info_hourly = []
    domains = 0
    ads = 0

    #retrieve and decode json data from pi-hole ftl daemon
    try:
        with urllib.request.urlopen("http://%s/admin/api.php?overTimeData10mins" % \
        local_address) as url:
            data = json.loads(url.read().decode())
    except urllib.error.URLError:
        print("Error: Invalid address for DNS server. Try again.")
        sys.exit(1)

    #sort and reverse data so that latest time intervals appear first in list
    for key in sorted(data['domains_over_time'].keys(), reverse=True):
        domain_info_mins.append([data['domains_over_time'][key], data['ads_over_time'][key]])

    #aggregate data into hourly intervals
    for i in range(len(domain_info_mins)):
        if i > 0 and i % 6 == 0:
            domain_info_hourly.append([domains, ads])
            domains = 0
            ads = 0
        domains += domain_info_mins[i][0]
        ads += domain_info_mins[i][1]

    #extract a slice of the previous 24 hours
    domain_info_hourly = domain_info_hourly[:24]

    return domain_info_hourly

#color codes hourly interval based on relative level of dns traffic
def color_dict(level):
    return {
        1 : (0, 128, 255),
        2 : (0, 255, 255),
        3 : (255, 128, 0),
        4 : (0, 255, 0),
        5 : (128, 255, 0),
        6 : (255, 255, 0),
        7 : (255, 128, 0),
        8 : (255, 0, 0),
    }[level]

def generate_chart(data, flag):
    domain_info_chart = []
    minimum = data[0][0]
    maximum = data[0][0]

    #calculate minimum, maximum, and interval values to scale graph appropriately
    for hour in data:
        if hour[0] > maximum:
            maximum = hour[0]
        elif hour[0] < minimum:
            minimum = hour[0]
    chart_interval = (maximum - minimum) / 8

    #append final scaled values to new list
    for hour in data:
        domain_info_chart.append(int((hour[0] - minimum) / chart_interval))
    domain_info_chart = list(reversed(domain_info_chart[:8]))

    sense = SenseHat()
    sense.clear()

    #set pixel values on rgb display
    for col in range(0, 8):
        if domain_info_chart[col] > 0:
            for row in range(0, domain_info_chart[col]):
                #if flag not set, default to color red for all values
                sense.set_pixel(row, col, color_dict(domain_info_chart[col]) if flag else \
                                (255, 0, 0))

def main():
    parser = optparse.OptionParser(description="Generates a chart to display network traffic on the sense-hat RGB display")
    parser.add_option('-c', action="store_true", dest="color_flag", help="use color to indicate level of network traffic")
    parser.add_option('-a', action="store", dest="local_address", type="string", help="specify address of DNS server, defaults to localhost")
    parser.set_defaults(color_flag=False, local_address='127.0.0.1')
    opt, args = parser.parse_args()

    domain_info_hourly = dns_request(opt.local_address)
    generate_chart(domain_info_hourly, opt.color_flag)

if __name__ == '__main__':
    main()
