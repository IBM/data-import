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

        # If custom headers are not specified we can use the default headers
        if not headers:
            headers = self.headers
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
	parser.add_option('-r', '--referenceset', help='Name of the reference set or table to import into. This set must already exist. Required', action='store')
	parser.add_option('-i', '--ip', default="127.0.0.1", help='IP or Host of the QRadar console, or localhost if not present', action='store')
	parser.add_option('-t', '--token', help='QRadar authorized service token', action='store')
	parser.add_option('-f', '--file', help='File with AQL to execute.', action='store')
	parser.add_option('-k', '--column', help='Column in result set that is the key column in the reference table or the column to be loaded into the reference set',action='store')
	parser.add_option('-d', '--type', help='Either table or set, to define if target is a reference table or set',action='store')
	parser.add_option('-p', '--purge', help='Purge the data in the reference set or table before loading new data',action='store_true')
	parser.add_option('-v', '--verbose', help='Verbose output',action='store_true')
	
	return parser

def main():

    parser = get_parser()
    args = parser.parse_args()

    if args[0].help or not args[0].referenceset or not args[0].file or not args[0].ip or not args[0].token or not args[0].column or not (args[0].type == 'set' or args[0].type == 'table'):
        print >> sys.stderr, "A simple utility to run an AQL query and puts the results in a reference set or table"
        print >> sys.stderr, "When loading a reference table the query result column names MUST match those in the reference table"
	print >> sys.stderr, parser.format_help().strip() 
        exit(0)

    # Creates instance of APIClient. It contains all of the API methods.
    api_client = RestApiClient(args)

    # open file and get query
    file = open(args[0].file, 'r')

    # This is the AQL expression to send for the search.
    query_expression = file.readline();
    
    # Use the query parameters above to call a method. This will call
    # POST /searches on the Ariel API. (look at arielapiclient for more
    # detail).  A response object is returned. It contains  
    # successful or not successful search information.
    # The searchID corresponding to this search is contained in
    # the JSON object.

    print("Running query");
    response = api_client.call_api('ariel/searches', 'POST',None, {'query_expression':query_expression},None)

    # Each response contains an HTTP response code.
    # Response codes in the 200 range indicate that your request succeeded.
    # Response codes in the 400 range indicate that your request failed due to
    # incorrect input.
    # Response codes in the 500 range indicate that there was an error on the
    # server side.
    response_json = json.loads(response.read().decode('utf-8'))
    if response.code != 201:
        print("When running query is: " + str(response.code))
        print(json.dumps(response_json, indent=2, separators=(',', ':')))
	exit(1)
    
    # Prints the contents of the dictionary.
    if (args[0].verbose):
        print(response_json)

    # Retrieves the searchID of the query from the dictionary.

    search_id = response_json['search_id']

    # This block of code calls GET /searches/{searchID} on the Ariel API
    # to determine if the search is complete. This block of code will repeat
    # until the status of the search is 'COMPLETE' or there is an error.
    #response = api_client.get_search(search_id)
    response = api_client.call_api('ariel/searches/'+search_id, 'GET',None, {},None)
    error = False

    while (response_json['status'] != 'COMPLETED') and not error:
        if (response_json['status'] == 'EXECUTE') | \
                (response_json['status'] == 'SORTING') | \
                (response_json['status'] == 'WAIT'):
            time.sleep(1);
            response = api_client.call_api('ariel/searches/'+search_id, 'GET',None, {},None)
            response_json = json.loads(response.read().decode('utf-8'))
        else:
            print(response_json['status'])
            error = True

    # After the search is complete, call the GET /searches/{searchID} to obtain
    # the result of the search. 
    # Depending on whether the "application/json" or "application/csv" 
    # method is given, return search results will be in JSON form or CSV form.
    response = api_client.call_api('ariel/searches/'+search_id+'/results', 'GET',None, {},None)
    if response.code != 200:
        print("When retrieving query result is " + str(response.code))
        body = response.read().decode('utf-8')
        body_json = json.loads(body)
        print(json.dumps(body_json, indent=2, separators=(',', ':')))
        exit(1)

    body = response.read().decode('utf-8')
    body_json = json.loads(body)

    # print out data if in verbose mode
    if (args[0].verbose):
        print(json.dumps(body_json))
    data = list()
	
    if (args[0].type == 'table'):	
        print("Processing reference data of type table")
	
        # purge first
	if( args[0].purge ):
            print("Purging reference table " + args[0].referenceset);
            response = api_client.call_api('reference_data/tables/'+args[0].referenceset, 'DELETE',None,{'purge_only':'true'},None)
            if response.code != 200:
                print("When purging reference set " +  args[0].referenceset + " is: " + str(response.code))				
                body = response.read().decode('utf-8')
                body_json = json.loads(body)
                print(json.dumps(body_json, indent=2, separators=(',', ':')))
		
        if isinstance(body_json['events'], list):
		
            # loop over results and update reference table
			
            for kv in body_json['events']:
                for key,val in kv.items():
                     if key != args[0].column:
                         response = api_client.call_api('reference_data/tables/'+args[0].referenceset, 'POST',None, 
                             {'outer_key':kv[args[0].column],
						'inner_key':key,
						'value':val},None)
                         if response.code != 200:
                              print("When writing reference data is: " + str(response.code))
                              print("Writing key = " + kv[args[0].column] + " Column = " + key + " Value = " + val + "\n")
                              body = response.read().decode('utf-8')
                              body_json = json.loads(body)
                              print(json.dumps(body_json, indent=2, separators=(',', ':')))
    elif ( args[0].type == 'set'):
        print("Processing reference data of type set")
        # purge first
        if( args[0].purge ):
            print("Purging reference table " + args[0].referenceset);
            response = api_client.call_api('reference_data/sets/'+args[0].referenceset, 'DELETE',None,{'purge_only':'true'},None)
            if response.code != 200:
                 print("When purging reference set " +  args[0].referenceset + " is: " + str(response.code))
                 body = response.read().decode('utf-8')
                 body_json = json.loads(body)
                 print(json.dumps(body_json, indent=2, separators=(',', ':')))
				
        #build new list to load
        if isinstance(body_json['events'], list):
            for kv in body_json['events']:
                data.append( kv[args[0].column] );
		
        # bulk load entries
        response = api_client.call_api('reference_data/sets/bulk_load/'+args[0].referenceset, 'POST',None, {},json.dumps(data))
        if response.code != 200:
            print("When writing reference set " +  args[0].referenceset + " is: " + str(response.code))
            body = response.read().decode('utf-8')
            body_json = json.loads(body)
            print(json.dumps(body_json, indent=2, separators=(',', ':')))
        else:
            print("Wrote " + str(len(data)) + " to reference set ")

    

if __name__ == "__main__":
    main()
