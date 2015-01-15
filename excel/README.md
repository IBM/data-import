An example excel spreadsheet used to retrieve and update the contents of a radar reference table and map of sets.

Please note the reference table or the map of sets must have already been created.

Reference tables are a great way of bringing in additional context information about users etc. such as
fullname, department, manager and then using this information in searches and correlation rules.

Maps of sets are a great way to list what IPs or assets users are allowed to accessed. The correlation engine can then 
generate incidents when certain accounts access servers that they are not supposed to.

The spreadsheet is very straightforward. On the  first work sheet, called "Config", you configure:

- the QRadar service IP address,
- the security token to use to access the server (created from the "Authorized services" icon in the admin tab)
- the reference table name and name of the worksheet into which/from
- the reference data will be populated in your work book.
 
Once you have done this, simply hit the 'retrieve table' button, which invokes a macro called "retrievereferencetable"
 and it will retrieve the contents of the reference table into the configure work sheet.
 
After the reference table has been updated, simply hit th3 "Update table" button which invokes the "updatereferencetable"
 macro and the data in the worksheet is loaded into the reference table.