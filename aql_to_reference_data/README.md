AQL To Reference Data
========================

This script allows you to run an AQL query and use the result to populate a reference set or reference table.

Usage
========================

Usage: aql_to_reference_data.py [options]

Options:
  -h, --help            Show help message
  -r REFERENCESET, --referenceset=REFERENCESET
                        Name of the reference set or table to import into.
                        This set must already exist. Required
  -i IP, --ip=IP        IP or Host of the QRadar console, or localhost if not
                        present
  -t TOKEN, --token=TOKEN
                        QRadar authorized service token
  -f FILE, --file=FILE  File with AQL to execute.
  -k COLUMN, --column=COLUMN
                        Column in result set that is the key column in the
                        reference table or the column to be loaded into the
                        reference set
  -d TYPE, --type=TYPE  Either table or set, to define if target is a
                        reference table or set
  -p, --purge           Purge the data in the reference set or table before
                        loading new data
  -v, --verbose         Verbose output

