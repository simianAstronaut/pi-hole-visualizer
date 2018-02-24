# trafficGraph
Usage: dns_stats.py [options]

Generates a chart to display network traffic on the sense-hat RGB display. This script utilizes the FTL daemon, a component of the Pi-hole ecosystem, to retrieve statistics about DNS queries. For more information, visit the following [link](https://github.com/pi-hole/FTL)

Options:  
&nbsp;&nbsp;-h&nbsp; show this help message and exit  
&nbsp;&nbsp;-c&nbsp; use color to indicate level of network traffic  
&nbsp;&nbsp;-a&nbsp; LOCALADDRESS&nbsp; specify address of dns server, defaults to localhost
  
To run the script and update the chart continuously (one minute intervals):
1.  Type 'sudo crontab -e'  
2.  Append '* * * * * your_file_path/dns_stats.py -c' to the end of the file

![sense-hat display](https://github.com/monkeyWithKeyboard/trafficGraph/blob/master/images/sense-hat_2.jpg)
