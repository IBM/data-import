ABOUT
=====
This is a simple script that can be used to import data from STIX and/or TAXII repositories into QRadar reference sets. 

It is a work in progress, and does not yet support all available STIX indicators.


REQUIREMENTS
===========

This script is written to run in Python 2.7.6 and higher (a dependancy of the STIX library). It may work in Python 3, but it has not been tested by myself and will likely need some modifications. 

Note that QRadar does not currently ship with Python 2.7, so this script can normally not be run directly on the QRadar console without extensive workarounds.

This script requires python-stix, libtaxii, and their dependancies. You can install these using pip, or following the instructions located at 

   https://github.com/STIXProject/python-stix 

and

   http://libtaxii.readthedocs.org/en/latest/installation.html

The script also requires pytz for date/time parsing. You can install using pip, or instructions at http://pytz.sourceforge.net/

DETAILED DESCRIPTION
===========

This is a sample script that utilizes the QRadar REST API to import observable data from either 
a local STIX document or a TAXII server, into an already existing reference set. Sets should be in ALN, 
ALNIC, or IP type (only use IP type if all observable data is assured to be IP addresses). As with
any use of the QRadar REST API, you should have previously generated an authorized server token to
access the QRadar console. You can see the QRadar admin guide for information on how to generate an
authorized service token.

The first defined method (extractObservable) extracts the values from the indicators in the document that
should be imported into the set. Currently the script supports the observable types of AddressObjectType,
URIObjectType, DomainNameObjectType, UserAccountObjectType, or HostnameObjectType. If you want to support 
additional types, you can very simply add the required parsing to this method.

EXAMPLE USE
===========

To import from a TAXII server
-----------------------------
```./stix_import.py -x MyTaxiiServer.com --taxii_username MyUserName --taxii_password MyPassword --taxii_endpoint /taxii-discovery-service --taxii_start_time '2014-05-26 12:00:00' -c testCollection -i 1.2.3.4 -t XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX -r MyReferenceSet```

An example using the 'hailataxii.com' test service and the Zeus tracker:
-----------------------------

```./stix_import.py -i 1.2.3.4 -t XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX -x 'hailataxii.com' --taxii_endpoint '/taxii-discovery-service' -c guest.Abuse_ZeusTracker -r ZeusTracker -y AddressObjectType --taxii_start_time "`date -d yesterday '+%Y-%m-%d %H:%M:%S'`" --taxii_end_time "`date '+%Y-%m-%d %H:%M:%S'`"```

To import from a local STIX document
------------------------------------

```./stix_import.py -f STIXDocument.xml i 192.168.56.2 -t XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX -r MyReferenceSet```

To display help
---------------

```
./stix_import.py --help

A utility that imports STIX documents from either a TAXII server collection or a file.

All indicators and observables in the STIX document(s) will be imported into the specified reference set.

Usage: stix_import.py [options]

Options:
  -h, --help            Show help message
  -r REFERENCESET, --referenceset=REFERENCESET
                        Name of the reference set to import into. This set
                        must already exist. Required
  -i IP, --ip=IP        IP or Host of the QRadar console, or localhost if not
                        present
  -t TOKEN, --token=TOKEN
                        QRadar authorized service token
  -f FILE, --file=FILE  STIX file to import. Either this parameter or a STIX
                        file is required
  --strict              Raise an error on an unsupported indicator. Defaults
                        to simply printing to stderr.
  --verbose             Print various inputs and outputs to STDERR
  -x TAXII, --taxii=TAXII
                        TAXII Server Endpoint. Either this parameter or a STIX
                        file is required.
  -p TAXIIPORT, --taxiiport=TAXIIPORT
                        Port for the TAXII Server
  -c COLLECTION, --collection=COLLECTION
                        TAXII Data Collection to poll. Defaults to 'default'.
  --taxii_endpoint=TAXII_ENDPOINT
                        TAXII Service Endpoint. Required if -x is provided.
  --taxii_ssl=TAXII_SSL
                        Set this to use SSL for the TAXII request
  --taxii_username=TAXII_USERNAME
                        Set this to the username for TAXII BASIC
                        authentication, if any
  --taxii_password=TAXII_PASSWORD
                        Set this to use password for TAXII BASIC
                        authentication, if any
  --taxii_start_time=BEGIN_TS
                        The start timestamp (YYYY-MM-dd HH:MM:SS) in UTC for
                        the taxii poll request. Defaults to None.
  --taxii_end_time=END_TS
                        The end timestamp (YYYY-MM-dd HH:MM:SS) in UTC for the
                        taxii poll request. Defaults to None.
```

LICENSE
===========

Copyright (c) 2013 IBM

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in 
compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is 
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and limitations under the License.
