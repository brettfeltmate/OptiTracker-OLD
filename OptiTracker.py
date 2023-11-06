import sys
import os
import csv
from functools import reduce
from Resources.API.Official.PythonClient import NatNetClient

# TODO: is this necessary?
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

class OptiTracker:
    def __init__(self) -> None:
        self.client = self.init_client()
        self.desc_dict = None

    # Create NatNetClient instance
    def init_client(self) -> object:
        
        # Spawn client
        client = NatNetClient()
        client.data_description_listener = self.get_description

        return client
    
    def start_client(self):
        self.client.run()

    def stop_client(self):
        self.client.shutdown()

    def get_description(self, desc_dict):
        self.desc_dict = desc_dict

    def save_description(self):
        if self.desc_dict is None:
            print("crap")
        else:
            keys = reduce(set.union, map(set, self.desc_dict.values()))
            print('keys')
            with open('out\desc_dict.csv', 'w') as file:
                print("file opened")
                w = csv.writer(file, delimiter = '\t')
                w.writerow([''] + self.desc_dict.keys())
                for key in keys:
                    w.writerow(
                        [key] + [subdict.get(key, '') for subdict in self.desc_dict.values()]
                    )








