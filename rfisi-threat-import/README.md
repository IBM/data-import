ABOUT
=====

These two scripts provide a sample for creating the common threat intelligence reference collections as described @ https://ibm.biz/rfisi_threat_intel

REQUIREMENTS
===========

This script is written to run in Python 3. It may work in Python 2.7, but to date it has only been tested with 3.4.. 

Note that QRadar does not currently ship with Python 3, so the intention is that this script will be run offboard from the QRadar appliance. This would be normal in any sort of production environment anyway.

This script depends on the python requests library which is available on most python installations by default.

DETAILED DESCRIPTION
===========

The two scripts here relate to the Ready For IBM Security Intelligence partner program's approach to unified threat feeds. The first script (threat_reference_collections.py) will create the common collections as defined @ https://ibm.biz/rfisi_threat_intel. The second is a _very_ short sample of populating the collections as recommended.

Neither script takes any arguments but they both use the configuration file (threat_reference_config) which provides the hostname (or IP) of the QRadar console and the Authorized Services Token that will be used to authenticate. You can create this token in the Admin tab of the QRadar UI (see QRadar Admin Guide for details).

EXAMPLE USE
===========

To create the reference collections (one time only)
---------------------------------------------------
```./threat_reference_collections.py```

Add a single entry into the "Spam Senders" set and table
--------------------------------------------------------

```./threat_reference_sample.py```

LICENSE
===========

Copyright (c) 2015 IBM

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in 
compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is 
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and limitations under the License.

