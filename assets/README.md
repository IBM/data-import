Update asset properties
========================

A simple utility to load a CSV file with asset information into the QRadar asset model based on IP address (which must exist in QRadar)
The first column of the first line of the file must be 'ipaddress'
The remaining columns of the file must contain field name headers that match the asset properties being loaded
The asset with the most recent occurrence of the ip address is updated with the remaining fields on the line

example:

ipaddress,Technical Owner,Location,Description
172.16.129.128,Chris Meenan,UK,Email Server
172.16.129.129,Joe Blogs,Altanta,Customer Database Server
172.16.129.130,Jason Corbin,Boston,Application Server


Usage
========================

<pre>

Usage: update_assets.py [options]

Options:
  -h, --help            	Show help message
  -i IP, --ip=IP        	IP or Host of the QRadar console, or localhost if not
							present
  -t TOKEN, --token=TOKEN	QRadar authorized service token
  -f FILE, --file=FILE  	File with assets to load.
  -d, --fields          	Display asset model fields
  -v, --verbose         	Verbose output

</pre>
