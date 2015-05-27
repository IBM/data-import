# quick and simple extraction of tor nodes from directory
# with insert into QRadar reference collections. 
# 
# you'll need the TorCtl python package 
# from https://gitweb.torproject.org/pytorctl.git/
# and you'll need to have tor installed on the same
# host where this script runs.
# in the config file (tor_reference_config) find common 
# paths for the Tor bundle on Windows or Mac. You'll 
# have to (un)comment and/or edit these to suit your 
# environment.
#
# author: Yossi Gilad
# edits: Rory Bray


import sys
import subprocess
import time
from TorCtl import TorCtl
import requests
# do as I say, not as I do
requests.packages.urllib3.disable_warnings()

config = {}
exec(open('tor_reference_config').read(), config)

qradarIpAddress = config.get('qradarIP')
qradarSecToken = config.get('qradarAPIToken')

TASKLIST=config.get('TASKLIST')
TOR_PATH=config.get('TOR_PATH')
TOR_PS_NAME=config.get('TOR_PS_NAME')
CONTROL_PORT=config.get('CONTROL_PORT')

def download_network_view():
        global VIDALIA_PATH
        global CONTROL_PORT
        global AUTH_PASS
		
        start_tor=True
        ps_list = subprocess.Popen(TASKLIST, stdout=subprocess.PIPE).communicate()[0]
	for ps in ps_list:
                if ps.startswith(TOR_PS_NAME):
			start_tor = False
	if start_tor:
                print "Initializing TOR.."
                subprocess.Popen([TOR_PATH])
                time.sleep(20)
        
	print "starting.."
        # open the TOR connection
        conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=CONTROL_PORT)
        all_nodes = conn.get_network_status()

        print "wrapping it up."
        conn.close()
        return all_nodes

def create_reference_set(name,elmType,ttl):
	url='https://' + qradarIpAddress + '/api/reference_data/sets'
	headers={'SEC': qradarSecToken, 'Version': '4.0', 'Accept': 'application/json'}
	data={'name': name, 'element_type': elmType, 'time_to_live': ttl, 'timeout_type': 'LAST_SEEN'}

	try:
		response=requests.get(url+'/'+name,headers=headers,verify=False)
		if response.status_code == 404:
			response=requests.post(url,headers=headers,data=data,verify=False)
			print('reference set   ' + str(name) + '      creation HTTP status: ' + str(response.status_code))
	except requests.exceptions.RequestException as exception:
		print(str(exception) + ', exiting.\n')

def add_tor_node(set_name,ip):

	headers={'SEC': qradarSecToken, 'Version': '4.0', 'Accept': 'application/json'}

	set_url='https://' + qradarIpAddress + '/api/reference_data/sets/' + set_name
	set_data={'name': set_name, 'value': ip, 'source': 'tor_reference_import'}

	try:
		response=requests.post(set_url,headers=headers,data=set_data,verify=False)
		if response.status_code > 201:
			print('tor node ' + str(ip) + ' insertion HTTP status: ' + str(response.status_code))
	except requests.exceptions.RequestException as exception:
		print(str(exception) + ', exiting.\n')

def main():
	# check for and create reference collections in QRadar
	create_reference_set('tor_exit_nodes','IP','7 days')
	create_reference_set('tor_guard_nodes','IP','7 days')
	create_reference_set('tor_intermediary_nodes','IP','7 days')
        # Guard, Exit
        guards = set()
        exits = set()
        intermediaries = set()
        all_nodes = download_network_view()
        for node in all_nodes:
                middle = True
                if "Guard" in node.flags:
                        guards.add(node.ip)
                        middle = False
                if "Exit" in node.flags:
                        exits.add(node.ip)
                        middle = False
                if (middle):
                        intermediaries.add(node.ip)
	print('adding guard nodes ... ')
        for node in guards:
                add_tor_node('tor_guard_nodes',node)
		sys.stdout.write('.')
		sys.stdout.flush()
        print(' done.\n')
	print('adding exit nodes ... ')
        for node in exits:
                add_tor_node('tor_exit_nodes',node)
		sys.stdout.write('.')
		sys.stdout.flush()
        print(' done.\n')
	print('adding intermediary nodes ... ')
        for node in intermediaries:
                add_tor_node('tor_intermediary_nodes',node)
		sys.stdout.write('.')
		sys.stdout.flush()
        print(' done.\n')

if __name__ == "__main__":
        main()


