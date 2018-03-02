# trafficGraph

Generates a chart to display network traffic on the sense-hat RGB display. This script utilizes the FTL daemon, a component of the Pi-hole ecosystem, to retrieve statistics about DNS queries. For instructions on how to download and install Pi-hole, visit the main [website](https://pi-hole.net/). For additional information on the FTL engine, check out the following [link](https://github.com/pi-hole/FTL).

Usage: dns_stats.py [-h] [-c {traffic, ads}] [-a ADDRESS]  

Options:  
&nbsp;&nbsp;-h, --help&nbsp; show this help message and exit  
&nbsp;&nbsp;-c {traffic, ads}, --color {traffic, ads}&nbsp; specify 'traffic' to color code based on level of network traffic, or 'ads' to color code based on percentage of ads blocked  
&nbsp;&nbsp;-a ADDRESS, --address ADDRESS&nbsp; specify address of dns server, defaults to localhost
  
To run the script and update the chart continuously (one minute intervals):
1.  Type 'sudo crontab -e'  
2.  Append '* * * * * your_file_path/dns_stats.py [-c {traffic, ads}] [-a ADDRESS]' to the end of the file

![sense-hat display](https://github.com/monkeyWithKeyboard/trafficGraph/blob/master/images/sense-hat_2.jpg)
