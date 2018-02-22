#!/usr/bin/python3
import urllib.request, json
from sense_hat import SenseHat

def dns_request():
        domainInfo10mins = []
        domainInfoHourly = []
        domains = 0
        ads = 0

        with urllib.request.urlopen("http://192.168.1.200/admin/api.php?overTimeData10mins") as url:
                data = json.loads(url.read().decode())
        for key in sorted(data['domains_over_time'].keys(), reverse=True):
                domainInfo10mins.append([data['domains_over_time'][key],data['ads_over_time'][key]])
        for i in range(len(domainInfo10mins)):
                if i > 0 and i % 6 == 0:
                        domainInfoHourly.append([domains, ads])
                        domains = 0
                        ads = 0
                domains += domainInfo10mins[i][0]
                ads += domainInfo10mins[i][1]
        domainInfoHourly = domainInfoHourly[:24]
        return domainInfoHourly

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

def generateChart(data):
        domainInfoChart = []
        min = data[0][0]
        max = data[0][0]

        for hour in data:
                if hour[0] > max:
                        max = hour[0]
                elif hour[0] < min:
                        min = hour[0]
        chartInterval = (max - min) / 8
        for hour in data:
                domainInfoChart.append(int((hour[0] - min) / chartInterval))
        domainInfoChart = domainInfoChart[:8]

        sense = SenseHat()
        sense.clear()

        for col in range(0,8):
            if domainInfoChart[col] > 0:
                for row in range(0,domainInfoChart[col]):
                    sense.set_pixel(row,col,colorDict(domainInfoChart[col]))
        
def main():
    domainInfoHourly = dns_request()
    generateChart(domainInfoHourly)

if __name__ == '__main__':
    main()
