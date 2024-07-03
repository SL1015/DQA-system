from pymongo import MongoClient
import re

# Connect to the local MongoDB instance
client = MongoClient("mongodb://localhost:27017/")

# Access database
mydb = client["DQA"]

# Access collection
col_csv = mydb["csv"]
col_netflow = mydb["netflow"]

csv_file_path = r'c:\UZH\datasets\botnet13\capture20110811.binetflow'
netflow_file_path = r'c:\UZH\datasets\botnet13\capture20110811.pcap.netflow.labeled'

with open(netflow_file_path, 'r') as file:
    #fields = file.readline().strip().split('	') 
    # headers_raw = file.readline().strip().split('	')  # Assuming the first line is the header
    # for header in headers_raw:
    #     headers = header.strip().split('  ')

    # for line in file:
    #     fields_raw = line.strip().split('	')
    #     for field in fields_raw:
    #         fields = line.strip().split('\t')

    pattern = '[ \t,;]+'
    line = file.readline().strip()
    headers = re.split(pattern, line)
    print(headers)
    
    # Define a pattern to split on multiple delimiters
    # This example uses commas, tabs, and semicolons as possible delimiters


    for line in file:
        line = line.strip()
        fields = re.split(pattern, line)
        document = {}
        for index, field in enumerate(fields):
            if index < len(headers):
                document[headers[index]] = field
            else:
                if 'extra_fields' not in document:
                    document['extra_fields'] = []
                document['extra_fields'].append(field)
        col_netflow.insert_one(document)

    print('done')