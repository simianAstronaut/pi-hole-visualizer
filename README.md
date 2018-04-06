# Pi-hole Visualizer  
Pi-hole Visualizer is a Python script used to display DNS traffic in a colorful and informative way on the Raspberry Pi Sense-HAT. It depends on the Pi-hole ecosystem to retrieve statistics about DNS queries and ads blocked on the local network.    

![sense-hat display](https://github.com/simianAstronaut/pi-hole-visualizer/blob/master/images/sense_hat.gif)  

### Details  
- Pi-hole Visualizer alternates between displaying a bar chart of DNS traffic and a spiral graph representing overall percentage of ads blocked.  

- Column height in the bar chart represents the relative level of DNS traffic generated for a specific time interval in the previous 24-hour timeframe. The selected time interval ranges from 10 minutes to 2 hours. Color can be used to represent the intensity of DNS traffic or the percentage of ads blocked.  

- In the spiral graph, the overall percentage of ads blocked in the previous 24-hour timeframe is represented by the number of red pixels displayed. 

- Additional options include specifying the orientation of the display and low-light mode.  

- Each option corresponds to a joystick direction that can alter program behavior while running.  

- Pi-hole Visualizer is either manually run from the command line or enabled as a systemd service to run automatically at boot.  
---  
  
### Requirements
* To install Pi-hole, run `curl -sSL https://install.pi-hole.net | bash`.
* The Sense-HAT package can be installed with `sudo apt-get install sense-hat`.  
 
---  
  
### Usage
**`dns_stats.py [OPTION]`**  

#### Options  
`-h, --help`  
Show this help message and exit.  

`-i {10, 30, 60, 120, 180}, --interval {10, 30, 60, 120, 180}`  
Specify interval time in minutes. Defaults to one hour.

`-c {basic, traffic, ads}, --color {basic, traffic, ads}`  
Specify 'basic' to generate the default red chart, 'traffic' to represent the level of network traffic, or 'ads' to represent the percentage of ads blocked.    

`-a ADDRESS, --address ADDRESS`  
Specify address of dns server, defaults to localhost.

`-o {0, 90, 180, 270}, --orientation {0, 90, 180, 270}`  
Specify orientation of display so that RPi may be installed in non-default orientation.

`-ll, --lowlight`  
Lower LED matrix brightness for use in low light environments.  

#### Joystick Controls  
- _UP - PUSH_  
Cycle color mode.  

- _RIGHT - PUSH_  
Cycle interval selection.  

- _DOWN - PUSH_  
Toggle low-light mode.  

- _LEFT - PUSH_  
Cycle display orientation.  

- _MIDDLE - HOLD_  
Exit program.  
 
---  
  
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
