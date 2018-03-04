# Pi-hole Visualizer  
Pi-hole Visualizer is a Python script used to display DNS traffic in a colorful and informative way on the Sense-HAT. It depends on the Pi-hole ecosystem and specifically the FTL daemon to retrieve statistics about DNS queries and ads blocked on the local network.  

Column height represents the relative level of traffic generated for a specific hourly interval in the previous 24-hour timeframe. Color is used to represent either the aforementioned traffic level or the relative percentage of ads blocked. Pi-hole visualizer can also alternate between the color coding systems at regular intervals. The program is either manually run from the command line or enabled as a systemd service to run automatically at boot.  

## Requirements
* To install Pi-hole, run `curl -sSL https://install.pi-hole.net | bash`
* The Sense-HAT package can be installed with `sudo apt-get install sense-hat`  

## Usage
Usage: dns_stats.py [-h] [-c {traffic, ads}] [-a ADDRESS]  

Options:  
&nbsp;&nbsp;-h, --help&nbsp; show this help message and exit  
&nbsp;&nbsp;-c {traffic, ads}, --color {traffic, ads}&nbsp; specify 'traffic' to color code based on level of network traffic, or 'ads' to color code based on percentage of ads blocked  
&nbsp;&nbsp;-a ADDRESS, --address ADDRESS&nbsp; specify address of dns server, defaults to localhost

 

![sense-hat display](https://github.com/simianAstronaut/pi-hole-visualizer/blob/master/images/sense-hat_2.jpg)
