#!/usr/bin/env python3
#
# Really simple reference set and table creation
# for threat intelligence integration. This script
# will create the standard reference collections
# as described at https://ibm.biz/rfisi_threat_intel
#
# This is meant to be used as a sample starting
# point only. The sample lacks key features of a
# production-ready solution such as certificate
# validation on SSL/TLS connections and robust
# exception handling.

import time
import requests
# do as I say, not as I do
requests.packages.urllib3.disable_warnings()

config = {}
exec(open('threat_reference_config').read(), config)

# QRadar specific.
global qradarIpAddress
global qradarSecToken

qradarIpAddress = config.get('qradarIP')
qradarSecToken = config.get('qradarAPIToken')

def addSpamSender(ip,provider,confidence,first_seen_date,last_seen_date):
	referenceSetName='Spam Senders'

	headers={'SEC': qradarSecToken, 'Version': '4.0', 'Accept': 'application/json'}

	set_url='https://' + qradarIpAddress + '/api/reference_data/sets/' + referenceSetName
	set_data={'name': referenceSetName, 'value': ip, 'source': 'sample script'}

	table_name=referenceSetName+' Data'
	table_url='https://' + qradarIpAddress + '/api/reference_data/tables/' + table_name
	table_source='sample script'
	fields=[{'name':'Provider','value':provider},\
			{'name':'Confidence','value':confidence},\
			{'name':'First Seen Date','value':first_seen_date},\
			{'name':'Last Seen Date','value':last_seen_date}]
	
	try:
		response=requests.post(set_url,headers=headers,data=set_data,verify=False)
		for i in fields:
			data={'name': table_name, 'outer_key':ip, 'inner_key':i['name'], 'value':i['value'], 'source': 'sample script'}
			response=requests.post(table_url,headers=headers,data=data,verify=False)
		print('Spam Sender ' + str(ip) + ' insertion HTTP status: ' + str(response.status_code))
	except requests.exceptions.RequestException as exception:
		print(str(exception) + ', exiting.\n')

def main():
	timestamp=int(time.time())*1000
	addSpamSender('192.0.2.1','fake provider',99,timestamp,timestamp)

if __name__ == '__main__':
	main()

