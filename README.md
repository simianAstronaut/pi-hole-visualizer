# Pi-hole Visualizer  
Pi-hole Visualizer is a Python script used to display DNS traffic in a colorful and informative way on the Sense-HAT. It depends on the Pi-hole ecosystem and specifically the FTL daemon to retrieve statistics about DNS queries and ads blocked on the local network.  

Column height represents the relative level of traffic generated for a specific hourly interval in the previous 24-hour timeframe. Color is used to represent either the aforementioned traffic level or the relative percentage of ads blocked. Pi-hole visualizer can also alternate between the color coding systems at regular intervals. The program is either manually run from the command line or enabled as a systemd service to run automatically at boot.  

![sense-hat display](https://github.com/simianAstronaut/pi-hole-visualizer/blob/master/images/sense-hat_2.jpg)

### Requirements
* To install Pi-hole, run `curl -sSL https://install.pi-hole.net | bash`
* The Sense-HAT package can be installed with `sudo apt-get install sense-hat`  

### Usage
Usage: dns_stats.py [-h] [-c {traffic, ads}] [-a ADDRESS]  

Options:  
&nbsp;&nbsp;-h, --help&nbsp; show this help message and exit  
&nbsp;&nbsp;-c {traffic, ads}, --color {traffic, ads}&nbsp; specify 'traffic' to color code based on level of network traffic, or 'ads' to color code based on percentage of ads blocked  
&nbsp;&nbsp;-a ADDRESS, --address ADDRESS&nbsp; specify address of dns server, defaults to localhost

 ### To Install As a System Service  
 1. Make the script and unit file executable:  
 `sudo chmod +x dns_stats.py`  
 `sudo chmod +x dns_stats.service`  
 
 2. Check that the path in the unit file after `ExecStart` matches the path of your script.  
 
 3. Copy the unit file to the system directory:  
 `sudo cp dns_stats.service /lib/systemd/system`  
 
 4. Enable the service to run at startup:  
 `sudo systemctl enable dns_stats`  
 
 5. Reboot.  
 `sudo reboot`  
 
 6. To check the status of the service:  
 `sudo systemctl status dns_stats`
