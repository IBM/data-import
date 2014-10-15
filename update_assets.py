# This script is used to run an AQL Query and then load the results into a reference set or reference table
import sys, os
import json, time
from urllib2 import Request
from urllib2 import urlopen
from urllib2 import HTTPError
from optparse import OptionParser
from optparse import BadOptionError
from optparse import AmbiguousOptionError

# A simple HTTP client that can be used to access the REST API
class RestApiClient:

    # Constructor for the RestApiClient Class
    def __init__(self,args):

        # Gets configuration information from config.ini. See ReadConfig
        # for more details.

        # Set up the default HTTP request headers
        self.headers = {b'Accept': 'application/json' }
        self.headers['Version'] = '3.0' 
        self.headers['Content-Type'] = 'application/json' 

        # Set up the security credentials. We can use either an encoded
        # username and password or a security token
        self.auth = {'SEC': args[0].token}

        self.headers.update(self.auth)

        # Set up the server's ip address and the base URI that will be used for
        # all requests
        self.server_ip = args[0].ip
        self.base_uri = '/api/'

	self.quiet = not args[0].verbose;

    # This method is used to set up an HTTP request and send it to the server
    def call_api(self, endpoint, method, headers=None, params=[], data=None, quiet=False):

        path = self.parse_path(endpoint, params)

        # If custom headers are not specified we can merge the default headers
        if not headers:
            headers = self.headers
	else:
	    for key, value in self.headers.items():
	        if headers.get( key,'') == '':
		    headers[ key ] = value

        # Send the request and receive the response
        if not self.quiet:
            print('\nSending ' + method + ' request to: ' + 'https://' +self.server_ip+self.base_uri+path+'\n')

        request = Request(
            'https://'+self.server_ip+self.base_uri+path, headers=headers)
        request.get_method = lambda: method
        try:
            #returns response object for opening url.
            return urlopen(request, data)
        except HTTPError as e:
            #an object which contains information similar to a request object
            return e

    # This method constructs the query string
    def parse_path(self, endpoint, params):

        path = endpoint + '?'

        if isinstance(params, list):

            for kv in params:
                if kv[1]:
                    path += kv[0]+'='+(kv[1].replace(' ','%20')).replace(',','%2C')+'&'

        else:
            for k, v in params.items():
                if params[k]:
                    path += k+'='+v.replace(' ','%20').replace(',','%2C')+'&'

        # removes last '&' or hanging '?' if no params.
        return path[:len(path)-1]

class PassThroughOptionParser(OptionParser):
	def _process_args(self, largs, rargs, values):
		while rargs:
			try:
				OptionParser._process_args(self,largs,rargs,values)

			except (BadOptionError,AmbiguousOptionError) as e:
				largs.append(e.opt_str)
def get_parser():

	parser = PassThroughOptionParser(add_help_option=False)
	parser.add_option('-h', '--help', help='Show help message', action='store_true')
	parser.add_option('-i', '--ip', default="127.0.0.1", help='IP or Host of the QRadar console, or localhost if not present', action='store')
	parser.add_option('-t', '--token', help='QRadar authorized service token', action='store')
	parser.add_option('-f', '--file', help='File with assets to load.', action='store')
	parser.add_option('-d', '--fields', help='Display asset model fields',action='store_true')
	parser.add_option('-v', '--verbose', help='Verbose output',action='store_true')
	
	return parser

def main():

	parser = get_parser()
	args = parser.parse_args()

	if args[0].help or not (args[0].file or args[0].fields) or not args[0].ip or not args[0].token :
		print >> sys.stderr, "A simple utility to load a CSV file with asset information into the QRadar asset model based on IP address (which must exist in QRadar)"
		print >> sys.stderr, "The first column of the first line of the file must be 'ipaddress'"
		print >> sys.stderr, "The remaining columns of the file must contain field name headers that match the asset properties being loaded"
		print >> sys.stderr, "The asset with the most recent occurrence of the ip address is updated with the remaining fields on the line"
		print >> sys.stderr, "";
		print >> sys.stderr, "example:"
		print >> sys.stderr, "";
		print >> sys.stderr, "ipaddress,Technical Owner,Location,Description"
		print >> sys.stderr, "172.16.129.128,Chris Meenan,UK,Email Server"
		print >> sys.stderr, "172.16.129.129,Joe Blogs,Altanta,Customer Database Server"
		print >> sys.stderr, "172.16.129.130,Jason Corbin,Boston,Application Server"
		print >> sys.stderr, "";
		print >> sys.stderr, parser.format_help().strip() 
		exit(0)

	# Creates instance of APIClient. It contains all of the API methods.
	api_client = RestApiClient(args)

	# retrieve all the asset fields
	print("Retrieving asset fields");
	response = api_client.call_api('asset_model/properties', 'GET',None, {},None)
    
	# Each response contains an HTTP response code.
	response_json = json.loads(response.read().decode('utf-8'))
	if response.code != 200:
		print("When retrieving assets : " + str(response.code))
		print(json.dumps(response_json, indent=2, separators=(',', ':')))
		exit(1)

	asset_field_lookup = {}
	if ( args[0].fields ):
		print("Asset fields:")
	for asset_field in response_json:
		asset_field_lookup[ asset_field['name' ] ] = asset_field['id']
		if ( args[0].fields ):
			print(asset_field['name' ])

	if( not args[0].file ):
		exit(1)

	# open file and get query
	file = open(args[0].file, 'r')

	if file == None:
		print("File not found " + args[0].file)
		exit(1)

	# This is the asset data to load, need to check all the names exist
	columnnames = file.readline().strip();
	fields = columnnames.split(',');

	asset_file_fields = {}
	field_index = 0;
	is_error = 0;
	for fname in fields:
		if (fname <> 'ipaddress') and (asset_field_lookup.get(fname,'')==''):
			print("Field = " + fname + " does not exist")
			is_error = 1
		elif( fname == 'ipaddress' ):
			asset_file_fields[ field_index ] = 0 
		else:
			asset_file_fields[ field_index ] = asset_field_lookup[ fname ]
		field_index = field_index + 1;

	# if there was an error print out the field
	if is_error == 1:
		print("Assets field: ")
		for k, v in asset_field_lookup.items():
			print(k)
		exit(1)
		
	# retrieve all the assets
	print("Retrieving assets from QRadar");
	response = api_client.call_api('asset_model/assets', 'GET',None, {},None)


	# Each response contains an HTTP response code.
	response_json = json.loads(response.read().decode('utf-8'))
	if response.code != 200:
		print("When retrieving assets : " + str(response.code))
		print(json.dumps(response_json, indent=2, separators=(',', ':')))
		exit(1)
    
	print( str(len(response_json)) + " assets retrieved");
	# loop over assets and add to a lookup table
	ip_assetid_lookup = {}
	ip_lastseen_lookup = {}

	for asset in response_json:
		interfaces = asset['interfaces'];
		for interface in interfaces:
			for ipaddresses in interface['ip_addresses']:

				# get the largest last seen we have from this asset
				max_last_seen = ipaddresses['last_seen_scanner']
				if ( ipaddresses['last_seen_profiler'] > max_last_seen ):
					max_last_seen = ipaddresses['last_seen_profiler']

				# look to see if we have seen this IP address before
				last_seen = ip_lastseen_lookup.get( ipaddresses['value'] ,-1);
				if (last_seen == -1) or (last_seen < max_last_seen):
					ip_lastseen_lookup[ ipaddresses['value'] ] = max_last_seen
					ip_assetid_lookup[ ipaddresses['value'] ] = asset['id']

	# now we have loaded the assets and mapped ip address to asset id 
	# we can loop over the file
	data = file.readline().strip()
	
	update_success = 0;
	current_line = 2;
	while data <> '':
		
		# split values
		data_fields = data.split(',')

		json_string = "{ \"properties\": [ "
		index = 0;
		ip_address = '';
		if( len(data_fields) != len(asset_file_fields)):
			print("Error : Missing or extra fields at line " + str(current_line) )
		else:
			ip_address_found=0
			for data_field in data_fields:
				data_field = data_field.strip()
				# this is the IP address
				if index ==0:
					ip_address = data_field
					if( ip_assetid_lookup.get(ip_address,'') == '' ):
						print("Error : IP address " + ip_address + " at line " + str(current_line) + " does not exist in QRadar Asset DB")
					else:
						ip_address_found = 1
				else:
					json_string = json_string + "{ \"type_id\":" + str(asset_file_fields[index]) + ",\"value\":\"" + data_field + "\"}"

				index = index + 1;
				if (index < len(data_fields)) and (index <> 1):
					json_string = json_string + ","

			if ip_address_found == 1:
				json_string = json_string + "]}"

				#print(" JSON = " + json_string)			
				# create JSON object
		
				response = api_client.call_api('asset_model/assets/'+str(ip_assetid_lookup[ip_address]), 'POST',{b'Accept': 'text/plain' },{},json_string)
				# Each response contains an HTTP response code.
				if response.code != 200:
					response_json = json.loads(response.read().decode('utf-8'))
					print("When updating asset : " + str(ip_assetid_lookup[ip_address]) + " " + ip_address)
					print(" JSON = " + json_string)			
					print(json.dumps(response_json, indent=2, separators=(',', ':')))
					exit(1)
				update_success = update_success + 1
    
		data = file.readline().strip()
		current_line = current_line + 1
	print( str(update_success) + " assets sucessfully updated")
if __name__ == "__main__":
    main()
