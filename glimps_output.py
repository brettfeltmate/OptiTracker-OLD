import sys
import os
import time
import csv
from functools import reduce

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# Import MoCap interface
from Resources.API.Official.PythonClient import NatNetClient


def get_descriptions(desc_dict):
    keys = reduce(set.union, map(set, desc_dict.values()))
    with open('desc_dict.csv', 'wb') as file:
        w = csv.writer(file, delimiter = '\t')
        w.writerow([''] + desc_dict.keys())
        for key in keys:
            w.writerow([key] + [subdict.get(key, '') for subdict in desc_dict.values()])

client = NatNetClient()
client.data_description_listener = get_descriptions
client.run()
client.shutdown()
exit()




