ABOUT
=====
This is a simple script that can be used to import IP addresses of active TOR relay nodes into reference sets in QRadar. 

It is a work in progress, meant as a sample or starting point; it is missing complete error handling and probably should be converted to use the bulk load API endpoints for performance.


REQUIREMENTS
===========

This script will run in Python 2.7+ and higher. It may work in Python 3, but that has not been tested. It is written to user version 4.0 of the QRadar API and therefore requires QRadar 7.2.4. However, with minor edits it should work with older versions as well. 

Note that QRadar does not currently ship with Python 2.7, so this script can normally not be run directly on the QRadar console. Additionally, it expects to find and execute the TOR Browser bundle (modified Firefox) and therefore is best run on a desktop (Mac, Windows, Linux) that has the Tor Bundle installed. With proper knowledge of Tor's workings, one could modify it to run the anonymizing proxy directly to enable 'headless' execution.  I haven't even tried that, yet.

This script requires TorCtl which can be found here:

   https://gitweb.torproject.org/pytorctl.git


DETAILED DESCRIPTION
===========

This is a simple script that can be used to import IP addresses of active TOR relay nodes into reference sets in QRadar. It creates 3 reference sets: tor_guard_nodes, tor_intermediate_nodes, and tor_exit_nodes. For explanations of the node types, refer to the FAQs on torproject.org. The script will start the TOR Browser Bundle application and then use the active TOR proxy to connect to the service and enumerate the nodes in the directory. The discovered nodes are then inserted into the appropriate reference collection. The reference sets are configured to expire the entries after 7 days from the 'last-seen' time so that as nodes come and go over time the imported IP address lists remain relevant. If you actually use some form of this script in production, that expiry could be dropped to 2 days and the script executed daily.

The authentication details for the QRadar API are configured in a text file (tor_reference_config), you'll need the IP or hostname of the QRadar console and an Authorized Service Token. For instructions on creating and managing the tokens, consult Authorized Services section in the QRadar Admin Guide.

Also in the configuration file are some path and port details for the TOR Browser and proxy. If you are using MacOSX then the defaults may work for you as-is. There are also pre-populated settings (commented out) for Windows. In either case, confirm the file path(s) for your installation of TOR.

When it executes the scripts will show the results of creating the reference set collections (will indicate error if they already exist), then you'll see the output from TOR starting up and finally importing to the 3 reference sets.

Also included here is an xml file (tor-rules.xml) that contains some sample QRadar Custom Rules that use the collections. Again, these are simple and meant as starting points but illustrate potential uses of these reference sets. There are two in the Policy rule grouping and one the the Threats grouping ('Policy: Internal Tor Use', 'Policy: Operating a Tor Relay', and 'Threat: Remote Tor User' respectively). Importing these is completely optional.


EXAMPLE USE
===========

To import TOR Nodes
-------------------------------
```python tor_reference_import.py```

To import the tor-rules content
-------------------------------
```/opt/qradar/bin/contentManagement.pl --action import --file tor-rules.xml```

LICENSE
===========

Copyright (c) 2015 IBM

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in 
compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is 
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and limitations under the License.

