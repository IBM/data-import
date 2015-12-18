#!/usr/bin/python2

import collections
import datetime
import getpass
import io
import json
import pprint
import sys
import time
import urllib2
from optparse import AmbiguousOptionError
from optparse import BadOptionError
from optparse import OptionParser

import libtaxii as t
import libtaxii.clients as tc
import libtaxii.messages_11 as tm11
import pytz
from stix.common import vocabs
from stix.common.vocabs import IndicatorType
from stix.utils.parser import EntityParser


def extractObservable(args, obs, values):
	typ = obs["properties"]["xsi:type"]

	if args[0].type and args[0].type != typ:
		return

	val = None

	if typ == "AddressObjectType":

		# Handle if Address_Value is a plain string or one with datatype
		if isinstance(obs["properties"]["address_value"], basestring):
			val = obs["properties"]["address_value"]
		elif 'value' in obs["properties"]["address_value"]:
			val = obs["properties"]["address_value"]["value"]

	elif typ == "URIObjectType" or typ == "DomainNameObjectType" or typ == "HostnameObjectType":
		val = obs["properties"]["value"]

	elif typ == "UserAccountObjectType":
		val = obs["properties"]["username"]

	elif typ == "FileObjectType":
		val = []
		for myHash in obs["properties"]["hashes"]:
			val.append(myHash["simple_hash_value"]["value"])

	if val:
		if (not isinstance(val, basestring)) and isinstance(val, collections.Iterable):
			for addr in val:
				values.append(addr)
		else:
			values.append(val)
	else:
		if args[0].strict:
			raise Exception("Encountered unsupported CybOX observable type: " + typ)
		else:
			print >> sys.stderr, "Encountered unsupported CybOX observable type: " + typ + ", ignoring..."


def extractObservables(args, indicators):
	values = []

	for indicator in indicators:

		# Check if we were passed a list of indicators, or observables
		obs = indicator
		if "observable" in indicator:
			obs = indicator["observable"]

		try:
			if 'object' in obs:
				extractObservable(args, obs["object"], values)
			elif 'observable_composition' in obs:
				for observable in obs["observable_composition"]["observables"]:
					if 'object' in observable:
						extractObservable(args, observable["object"], values)

		except:

			print >> sys.stderr, "Could not handle observable/indicator:\n"
			pprint.pprint(indicator, sys.stderr)
			raise

	return values


class PassThroughOptionParser(OptionParser):
	def _process_args(self, largs, rargs, values):
		while rargs:
			try:
				OptionParser._process_args(self, largs, rargs, values)

			except (BadOptionError, AmbiguousOptionError) as e:
				largs.append(e.opt_str)


def get_parser():
	parser = PassThroughOptionParser(add_help_option=False)

	parser.add_option('-h', '--help', help='Show help message', action='store_true')
	parser.add_option('-r', '--referenceset',
					  help='Name of the reference set to import into. This set must already exist. Either set or map is required',
					  action='store')
	parser.add_option('-i', '--ip', default="127.0.0.1", help='IP or Host of the QRadar console',
					  action='store')
	parser.add_option('-t', '--token', help='QRadar authorized service token', action='store')
	parser.add_option('-f', '--file',
					  help='STIX file to import. Either this parameter or a STIX file is required',
					  action='store')
	parser.add_option('-y', '--type', help='Only import this type of indicator', action='store')
	parser.add_option('--strict', action="store_true",
					  help="Raise an error on an unsupported indicator. Defaults to simply printing to stderr.")
	parser.add_option('--verbose', action="store_true",
					  help="Print various inputs and outputs to STDERR")

	parser.add_option('-x', '--taxii',
					  help='TAXII Server Endpoint. Either this parameter or a STIX file is required.',
					  action='store')
	parser.add_option('-p', '--taxiiport', default="80", help='Port for the TAXII Server',
					  action='store')
	parser.add_option('-c', "--collection", default="default",
					  help="TAXII Data Collection to poll. Defaults to 'default'.")
	parser.add_option('--taxii_endpoint',
					  help='TAXII Service Endpoint. Required if -x is provided.', action='store')
	parser.add_option("--taxii_ssl", default=None,
					  help="Set this to use SSL for the TAXII request")
	parser.add_option("--taxii_username", default=None,
					  help="Set this to the username for TAXII BASIC authentication, if any")
	parser.add_option("--taxii_password", default=None,
					  help="Set this to use password for TAXII BASIC authentication, if any")

	parser.add_option("--taxii_start_time", dest="begin_ts", default=None,
					  help="The start timestamp (YYYY-MM-dd HH:MM:SS) in UTC " +
						   "for the taxii poll request. Defaults to None.")

	parser.add_option("--taxii_end_time", dest="end_ts", default=None,
					  help="The end timestamp (YYYY-MM-dd HH:MM:SS) in UTC " +
						   "for the taxii poll request. Defaults to None.")

	return parser


def print_help(parser):
	print >> sys.stderr, "\nA utility that imports STIX documents from either a TAXII server collection or a file.\n"
	print >> sys.stderr, "All indicators and observables in the STIX document(s) will be imported into the specified reference set.\n"
	print >> sys.stderr, parser.format_help().strip()


# Processes a STIX package dictionary and adds all indicators and observables to a QRadar reference set
def process_package_dict(args, stix_dict):
	values = []
	if "observables" in stix_dict:
		values.extend(extractObservables(args, stix_dict["observables"]["observables"]))

	if "indicators" in stix_dict:
		values.extend(extractObservables(args, stix_dict["indicators"]))

	if len(values) > 0:
		if args[0].ip:
			serverIP = args[0].ip
		else:
			serverIP = '127.0.0.1'

		url = 'https://' + serverIP + '/api/referencedata/sets/bulkLoad/' + args[0].referenceset

		headers = {'Accept': 'application/json', 'Content-type': 'application/json',
				   'version': '0.1', 'SEC': args[0].token}

		data = json.dumps(values)
		data = data.encode('utf-8')

		if args[0].verbose:
			print >> sys.stderr, "POSTING DATA:\n" + data + "\n"

		req = urllib2.Request(url, data, headers)
		try:
			response = urllib2.urlopen(req)
			body = response.read().decode('utf-8')

		except urllib2.HTTPError, err:
			body = err.read()
			print >> sys.stderr, "Error posting data " + data + "\n"
			print >> sys.stderr, body
			raise

		response_json = json.loads(body)

		if args[0].verbose:
			print >> sys.stderr, "RECIEVED RESPONSE:\n" + (
				json.dumps(response_json, indent=2, separators=(',', ':'))) + "\n"

	return len(values)


def main():
	# This is a work-around for the fact that the 1.0 indicator type was removed from the STIX python
	# library, even though it is the essentially the same as the 1.1 type. We want to still support 1.0
	# indicators since they are out there, and there is no difference for the purposes of this script.
	vocabs._VOCAB_MAP["stixVocabs:IndicatorTypeVocab-1.0"] = IndicatorType

	# Create XML parser that can strip namespaces
	xmlParser = EntityParser()

	stix_package = None

	argParser = get_parser()
	args = argParser.parse_args()

	if args[0].help:
		print_help(argParser)

	# Import from a TAXII server
	elif args[0].referenceset and args[0].taxii:
		begin_ts = None
		end_ts = None

		try:
			if args[0].begin_ts:
				structTime = time.strptime(args[0].begin_ts, '%Y-%m-%d %H:%M:%S')
				begin_ts = datetime.datetime(*structTime[:6])
				begin_ts = begin_ts.replace(tzinfo=pytz.UTC)
			else:
				begin_ts = None

			if args[0].end_ts:
				structTime = time.strptime(args[0].end_ts, '%Y-%m-%d %H:%M:%S')
				end_ts = datetime.datetime(*structTime[:6])
				end_ts = end_ts.replace(tzinfo=pytz.UTC)
			else:
				end_ts = None

		except ValueError:
			print >> sys.stderr, "Could not parse either start or end time"
			raise

		poll_req = tm11.PollRequest(message_id=tm11.generate_message_id(),
									collection_name=args[0].collection,
									exclusive_begin_timestamp_label=begin_ts,
									inclusive_end_timestamp_label=end_ts,
									poll_parameters=tm11.PollRequest.PollParameters())

		poll_req_xml = poll_req.to_xml()

		client = tc.HttpClient()

		if args[0].taxii_ssl:
			client.setUseHttps(True)

		if args[0].taxii_username:
			client.setAuthType(1)

			if not args[0].taxii_password:
				args[0].taxii_password = getpass.getpass("Enter your taxii password: ")

			client.setAuthCredentials(
					{'username': args[0].taxii_username, 'password': args[0].taxii_password})

		resp = client.callTaxiiService2(args[0].taxii, args[0].taxii_endpoint + "/poll/",
										t.VID_TAXII_XML_11, poll_req_xml, args[0].taxiiport)

		response_message = t.get_message_from_http_response(resp, '0')

		response_dict = response_message.to_dict();

		indicators = 0

		if 'content_blocks' in response_dict:
			for content in response_dict["content_blocks"]:
				bindingId = content["content_binding"]["binding_id"]

				if bindingId and bindingId.startswith("urn:stix.mitre.org:xml"):
					if args[0].verbose:
						print >> sys.stderr, "RECIEVED STIX DATA:\n"
						print >> sys.stderr, content["content"]

					try:
						# This string replace is a workaround for some invalid documents in my test server, if you don't need it, remove it
						xmlString = content["content"].replace('low', 'Low').replace('medium',
																					 'Medium').replace(
								'high', 'High')
						stix_package = xmlParser.parse_xml(io.BytesIO(xmlString), False)
						indicators += process_package_dict(args, stix_package.to_dict())

					except ValueError:
						print >> sys.stderr, "Could not parse STIX document: "
						print >> sys.stderr, content["content"]
						raise

			print "Imported", indicators, "indicators into reference set", args[0].referenceset
		else:
			print >> sys.stderr, "Invalid reponse from TAXII server"
			pprint.pprint(response_dict, sys.stderr)
			exit(255)

	# Import from a XML file on disk
	elif args[0].referenceset and args[0].file:

		stix_package = xmlParser.parse_xml(args[0].file, False)

		indicators = process_package_dict(args, stix_package.to_dict())

		print "Imported", indicators, "indicators into reference set", args[0].referenceset

	else:
		print >> sys.stderr, "Invalid arguments. Type 'python stix_import.py --help' for usage.\n"


if __name__ == "__main__":
	main()
