REQUIREMENTS
===========

This script is written to run in Python 2. It may work in Python 3, but it has not been tested
and will likely need some modifications.

This script requires python-stix, libtaxii, and their dependancies. You can install these using
the instructions located at 

   https://github.com/STIXProject/python-stix 

and

   http://libtaxii.readthedocs.org/en/latest/installation.html

The script also requires pytz for date/time parsing - http://pytz.sourceforge.net/

DESCRIPTION
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

LICENSE
===========

Copyright (c) 2013 IBM

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in 
compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is 
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and limitations under the License.
