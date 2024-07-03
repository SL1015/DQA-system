import json
from scapy.all import rdpcap, Ether, PcapReader

def read_pcap(file_path):
    # Load packets from the pcap file
    packets = rdpcap(file_path) 
    # Print basic information about each packet
    for packet in packets:
        print(packet.summary())

def pcap_to_json(pcap_file):
    packets = rdpcap(pcap_file)
    json_data = []

    for packet in packets:
        # Convert each packet to a dictionary
        packet_dict = dict(packet.fields)
        
        # Some packet parts like payloads can be binary data, which need special handling
        # Here we just convert them to a string representation for simplicity
        for field in packet_dict:
            if isinstance(packet_dict[field], bytes):
                packet_dict[field] = packet_dict[field].decode('utf-8', 'ignore')
        
        # Append the dictionary to our list
        json_data.append(packet_dict)
    
    # Convert list to JSON
    json_output = json.dumps(json_data, indent=4)
    return json_output

# Replace 'example.pcap' with the path to your PCAP file
pcap_file = read_pcap('c:\UZH\MSC THESIS\data assessment system_reputation system\datasets\botnet13\capture20110811.pcap.netflow.labeled')
json_output = pcap_to_json(pcap_file)
print(json_output)