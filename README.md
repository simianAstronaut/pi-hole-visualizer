# Pi-hole Visualizer  
Pi-hole Visualizer is a Python script used to display DNS traffic in a colorful and informative way on the Sense-HAT. It depends on the Pi-hole ecosystem and specifically the FTL daemon to retrieve statistics about DNS queries and ads blocked on the local network.  

Column height represents the relative level of traffic generated for a specific hourly interval in the previous 24-hour timeframe. Color is used to represent either the aforementioned traffic level or the relative percentage of ads blocked. Pi-hole visualizer can also alternate between the color coding systems at regular intervals. If you desire a more 'aesthetic' experience try the ripple option. The program is either manually run from the command line or enabled as a systemd service to run automatically at boot.  

![sense-hat display](https://github.com/simianAstronaut/pi-hole-visualizer/blob/master/images/sense_hat.gif)

### Requirements
* To install Pi-hole, run `curl -sSL https://install.pi-hole.net | bash`
* The Sense-HAT package can be installed with `sudo apt-get install sense-hat`  

### Usage
**`dns_stats.py [-h] [-c {traffic, ads, alternate}] [-r] [-a ADDRESS] [-o {0, 90, 180, 270}] [-ll]`**  

#### Options  
`-h, --help`  
Show this help message and exit  

`-c {traffic, ads, alternate}, --color {traffic, ads, alternate}`  
Specify 'traffic' to color code based on level of network traffic, 'ads' to color code based on percentage of ads blocked, or 'alternate' to switch between both  

`-r, --ripple`  
Generates a ripple effect when producing the chart  

`-a ADDRESS, --address ADDRESS`  
Specify address of dns server, defaults to localhost

`-o {0, 90, 180, 270}, --orientation {0, 90, 180, 270}`  
Specify orientation of display so that RPi may be installed in non-default orientation

`-ll, --lowlight`  
Lower LED matrix brightness for use in low light environments.

 ### To Install As a System Service  
 1. Make the script and unit file executable:  
 `sudo chmod +x dns_stats.py`  
 `sudo chmod +x dns_stats.service`  
 
 2. Check that the path in the unit file after `ExecStart` matches the path of your script.  
 
 3. Copy the unit file to the system directory:  
 `sudo cp dns_stats.service /lib/systemd/system`  
 
 4. Enable the service to run at startup:  
 `sudo systemctl enable dns_stats`  
 
 5. Reboot:  
 `sudo reboot`  
 
 6. To check the status of the service:  
 `sudo systemctl status dns_stats`
