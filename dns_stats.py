#!/usr/bin/python3
import optparse
import urllib.request, json
from sense_hat import SenseHat

def dns_request():
        domainInfo10mins = []
        domainInfoHourly = []
        domains = 0
        ads = 0

        #retrieve and decode json data from pi-hole ftl daemon
        with urllib.request.urlopen("http://192.168.1.200/admin/api.php?overTimeData10mins") as url:
                data = json.loads(url.read().decode())

        #sort and reverse data so that latest time intervals appear first in list
        for key in sorted(data['domains_over_time'].keys(), reverse=True):
                domainInfo10mins.append([data['domains_over_time'][key],data['ads_over_time'][key]])

        #aggregate data into hourly intervals
        for i in range(len(domainInfo10mins)):
                if i > 0 and i % 6 == 0:
                        domainInfoHourly.append([domains, ads])
                        domains = 0
                        ads = 0
                domains += domainInfo10mins[i][0]
                ads += domainInfo10mins[i][1]

        #extract a slice of the previous 24 hours
        domainInfoHourly = domainInfoHourly[:24]

        return domainInfoHourly

#color codes hourly interval based on relative level of dns traffic
def colorDict(x):
    return {
        1 : (0,128,255),
        2 : (0,255,255),
        3 : (255,128,0),
        4 : (0,255,0),
        5 : (128,255,0),
        6 : (255,255,0),
        7 : (255,128,0),
        8 : (255,0,0),
    }[x]

def generateChart(data, flag):
        domainInfoChart = []
        min = data[0][0]
        max = data[0][0]

        #calculate minimum, maximum, and interval values to scale graph appropriately
        for hour in data:
                if hour[0] > max:
                        max = hour[0]
                elif hour[0] < min:
                        min = hour[0]
        chartInterval = (max - min) / 8

        #append final scaled values to new list 
        for hour in data:
                domainInfoChart.append(int((hour[0] - min) / chartInterval))
        domainInfoChart = list(reversed(domainInfoChart[:8]))

        sense = SenseHat()
        sense.clear()

        #set pixel values on rgb display
        for col in range(0,8):
            if domainInfoChart[col] > 0:
                for row in range(0,domainInfoChart[col]):
                    #if flag not set, default to color red for all values
                    sense.set_pixel(row,col,colorDict(domainInfoChart[col]) if flag else (255,0,0))
        
def main():
    parser = optparse.OptionParser(description='Generates a chart to display network traffic on the sense-hat RGB display')
    parser.add_option('-c', action="store_true", dest="colorFlag", help="Uses color to indicate level of network traffic")
    parser.set_defaults(colorFlag=False)
    opt, args = parser.parse_args()

    domainInfoHourly = dns_request()
    generateChart(domainInfoHourly, opt.colorFlag)

if __name__ == '__main__':
    main()
