# trafficGraph
Usage: dns_stats.py [options]

Generates a chart to display network traffic on the sense-hat RGB display

Options:  
&nbsp;&nbsp;-h&nbsp; show this help message and exit  
&nbsp;&nbsp;-c&nbsp; uses color to indicate level of network traffic  

  
To run the script and update the chart continuously (one minute intervals):
1.  Type 'sudo crontab -e'  
2.  Append '* * * * * your_file_path/dns_stats.py -c' to the end of the file
3.  Reboot
