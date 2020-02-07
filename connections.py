import json
import requests
from scrut_api import ReportAPI, Requester


#gather data from microsoft, and convert it to JSON. 


scrutinizer_requester = Requester(
    authToken="your_auth_token",
    hostname="your_scrutinizer_hostname"
)


#simple way of remove all duplicate IP Adddresses from the multiple lists. 

report_params = ReportAPI()
report_params.report_options(reportTypeLang="connections")
report_params.make_object()
print('Request being made, painting a plixer....')
data = scrutinizer_requester.make_request(report_params)
print('data has been received')

#dictionary used to store all unique ip addresses. We will later check this has as we got through the data. If an IP has not be seen, we add it, if it has we update the number of connections and total KB

total_connections = 0
connection_hash = {
    

}


for row in data['report']['table']['inbound']['rows']:
    source_port = row[2]['label']
    source_ip = row[3]['label']
    protocal = row[4]['label']
    dest_ip = row[5]['label']
    dest_port = row[6]['label']
    bits = row[11]['rawValue']
    #math used to convert bits to kilobyte)
    kilobyte = (int(row[11]['rawValue']) * 8) / 8000
    bits_formated = row[11]['label']

    try:
        #check to see if IP is already in hash, if it is add this connections kilobytes and increment connection count by 1
        if source_ip in connection_hash:
            connection_hash[source_ip]['total_kb'] += kilobyte
            connection_hash[source_ip]['connections'] +=1
            total_connections +=1
        else:
        #if IP isn't in hash, add it to it with connection count of 1. 
            connection_hash[source_ip] = {
                'source_port':source_port,
                'destination_port':dest_port,
                'desination_ip':dest_ip,
                'protocal':protocal,
                'connections':1,
                'total_kb':kilobyte
                }
            total_connections +=1
    except:
        pass

#print some data about how many total connections was made. 
print(total_connections, 'connections found. Checking to see if anyone source voilates the policy.')

## loop over results and see if any single IP has more then 4000 connections, with an average connection size of 50 kB. you can adjust these values below. 
for connection in connection_hash:
    #check for the number of connections
    if connection_hash[connection]['connections'] > 4000:
        total_kb = connection_hash[connection]['total_kb']
        total_connections = connection_hash[connection]['connections']
        average_kb = total_kb / total_connections
        #check if average kB is greater then a value.
        if (average_kb) > 50:
            print(connection, connection_hash[connection]['connections'], 'Average kB', average_kb)
            