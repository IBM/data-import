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


def createReferenceSet(name, elmType, ttl):
    url='https://' + qradarIpAddress + '/api/reference_data/sets'
    headers={'SEC': qradarSecToken, 'Version': '4.0', 'Accept': 'application/json'}
    data={'name': name, 'element_type': elmType, 'time_to_live': ttl, 'timeout_type': 'LAST_SEEN'}

    try:
        response=requests.post(url,headers=headers,data=data,verify=False)
        print('reference set   ' + str(name) + '      creation HTTP status: ' + str(response.status_code))
    except requests.exceptions.RequestException as exception:
        print(str(exception) + ', exiting.\n')


def createReferenceTable(name, keyName, keyType, defaultElmType, fieldNamesAndTypes, ttl):
    url = 'https://' + qradarIpAddress + '/api/reference_data/tables'
    headers = {'SEC': qradarSecToken, 'Version': '4.0', 'Accept': 'application/json'}
    data = {'name': name, 'element_type': defaultElmType, 'outer_key_label': keyType, 'key_name_types': fieldNamesAndTypes, 'time_to_live': ttl, 'timeout_type': 'LAST_SEEN'}

    try:
        response = requests.post(url,headers=headers,data=data,verify=False)
        print('reference table ' + str(name) + ' creation HTTP status: ' + str(response.status_code))
    except requests.exceptions.RequestException as exception:
        print(str(exception) + ', exiting.\n')


def main():
    # field sets for various table types
    generic_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
                           '{"key_name":"Confidence","element_type":"NUM"},' \
                           '{"key_name":"First Seen Date","element_type":"DATE"},' \
                           '{"key_name":"Last Seen Date","element_type":"DATE"}' \
                           ']'

    malware_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
                           '{"key_name":"Confidence","element_type":"NUM"},' \
                           '{"key_name":"First Seen Date","element_type":"DATE"},' \
                           '{"key_name":"Last Seen Date","element_type":"DATE"},' \
                           '{"key_name":"Malware Family","element_type":"ALNIC"},' \
                           '{"key_name":"Identifier","element_type":"NUM"},' \
                           '{"key_name":"Portal URL","element_type":"ALNIC"},' \
                           '{"key_name":"Report URL","element_type":"ALNIC"},' \
                           '{"key_name":"Brand","element_type":"ALNIC"},' \
                           '{"key_name":"Infrastructure Type","element_type":"ALNIC"}' \
                           ']'

    phishing_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
                            '{"key_name":"Confidence","element_type":"NUM"},' \
                            '{"key_name":"First Seen Date","element_type":"DATE"},' \
                            '{"key_name":"Last Seen Date","element_type":"DATE"}' \
                            '{"key_name":"Identifier","element_type":"DATE"},' \
                            '{"key_name":"Portal URL","element_type":"DATE"},' \
                            '{"key_name":"Report URL","element_type":"DATE"},' \
                            '{"key_name":"Brand","element_type":"DATE"}' \
                            ']'

    botnet_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
                          '{"key_name":"Confidence","element_type":"NUM"},' \
                          '{"key_name":"First Seen Date","element_type":"DATE"},' \
                          '{"key_name":"Last Seen Date","element_type":"DATE"},' \
                          '{"key_name":"Botnet Name","element_type":"ALNIC"}' \
                          ']'

    anon_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
                        '{"key_name":"Confidence","element_type":"NUM"},' \
                        '{"key_name":"First Seen Date","element_type":"DATE"},' \
                        '{"key_name":"Last Seen Date","element_type":"DATE"},' \
                        '{"key_name":"Anonymizer Name","element_type":"ALNIC"}' \
                        ']'

    # Phishing Senders
    createReferenceSet('Phishing Senders', 'IP', '7 days')
    createReferenceTable('Phishing Senders Data', 'PhishingIP', 'IP', 'ALNIC', generic_table_fields, '7 days')

    # Phishing Subjects
    createReferenceSet('Phishing Subjects', 'ALNIC', '7 days')
    createReferenceTable('Phishing Subjects Data', 'PhishingSubject', 'ALNIC', 'ALNIC', generic_table_fields, '7 days')

    # Phishing URLs
    createReferenceSet('Phishing URLs', 'ALN', '7 days')
    createReferenceTable('Phishing URLs Data', 'PhishingURL', 'ALN', 'ALNIC', phishing_table_fields, '7 days')

    # Phishing IPs
    createReferenceSet('Phishing IPs', 'IP', '7 days')
    createReferenceTable('Phishing IPs Data', 'PhishingIP', 'IP', 'ALNIC', phishing_table_fields, '7 days')

    # Spam Senders
    createReferenceSet('Spam Senders', 'IP', '7 days')
    createReferenceTable('Spam Senders Data', 'SpamIP', 'IP', 'ALNIC', generic_table_fields, '7 days')

    # Malware Senders
    createReferenceSet('Malware Senders', 'IP', '7 days')
    createReferenceTable('Malware Senders Data', 'MalwareIP', 'IP', 'ALNIC', malware_table_fields, '7 days')

    # Malware URLs
    createReferenceSet('Malware URLs', 'ALN', '7 days')
    createReferenceTable('Malware URLs Data', 'MalwareURL', 'ALN', 'ALNIC', malware_table_fields, '7 days')

    # Malware Hostnames
    createReferenceSet('Malware Hostnames', 'ALN', '7 days')
    createReferenceTable('Malware Hostnames Data', 'MalwareHost', 'ALN', 'ALNIC', malware_table_fields, '7 days')

    # Malware IPs
    createReferenceSet('Malware IPs', 'IP', '7 days')
    createReferenceTable('Malware IPs Data', 'MalwareIP', 'IP', 'ALNIC', malware_table_fields, '7 days')

    # Malicious URLs
    createReferenceSet('Malicious URLs', 'ALN', '7 days')
    createReferenceTable('Malicious URLs Data', 'MalwareURL', 'ALN', 'ALNIC', generic_table_fields, '7 days')

    # Botnet IPs
    createReferenceSet('Botnet IPs', 'IP', '7 days')
    createReferenceTable('Botnet IPs Data', 'BotnetIP', 'IP', 'ALNIC', botnet_table_fields, '7 days')

    # Botnet C&C IPs
    createReferenceSet('Botnet C&C IPs', 'IP', '7 days')
    createReferenceTable('Botnet C&C IPs Data', 'BotnetIP', 'IP', 'ALNIC', botnet_table_fields, '7 days')

    # Anonymizer IPs
    createReferenceSet('Anonymizer IPs', 'IP', '7 days')
    createReferenceTable('Anonymizer IPs Data', 'AnonymizerIP', 'IP', 'ALNIC', anon_table_fields, '7 days')

    # Malware Hashes MD5
    createReferenceSet('Malware Hashes MD5', 'ALN', '7 days')
    createReferenceTable('Malware Hashes MD5 Data', 'MalwareHash', 'ALN', 'ALNIC', malware_table_fields, '7 days')

    # Malware Hashes SHA
    createReferenceSet('Malware Hashes SHA', 'ALN', '7 days')
    createReferenceTable('Malware Hashes SHA Data', 'MalwareHash', 'ALN', 'ALNIC', malware_table_fields, '7 days')

    # Rogue Process Names
    createReferenceSet('Rogue Process Names', 'ALN', '7 days')
    createReferenceTable('Rogue Process Names Data', 'ProcessName', 'ALN', 'ALNIC', generic_table_fields, '7 days')

if __name__ == '__main__':
    main()
