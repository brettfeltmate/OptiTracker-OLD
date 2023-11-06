import sys
import os
import csv
from collections import OrderedDict
from Resources.APIs.Official.PythonClient.NatNetClient import NatNetClient

# TODO: is this necessary?
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

class OptiTracker:
    def __init__(self) -> None:
        self.client = self.init_client()
        self.descriptions = OrderedDict()

    # Create NatNetClient instance
    def init_client(self) -> object:
        
        # Spawn client
        client = NatNetClient()
        client.full_description_listener = self.get_full_description
        client.skeleton_description_listener = self.get_skeleton_descriptions
        client.rigid_body_description_listener = self.get_rigid_body_descriptions

        return client
    
    def start_client(self):
        return self.client.run()

    def stop_client(self):
        self.client.shutdown()

    def get_full_description(self, desc_dict):
        self.descriptions['full'] = desc_dict

    def get_skeleton_descriptions(self, desc_dict):
        self.descriptions['skeletons'] = desc_dict

    def get_rigid_body_descriptions(self, desc_dict):
        self.descriptions['rigid_bodies'] = desc_dict

    def save_description(self, desc_type):
        print(f"Attempting to write {desc_type}...\n")
        if self.descriptions[desc_type] is None:
            print(f"Description of {desc_type} is None")
        else:
            print(f"{desc_type} is not None\nAttempting to write...\n")
            try:
                with open(f'out\{desc_type}_desc_dict.csv', 'w') as file:
                    print("file opened")
                    w = csv.writer(file, delimiter = '\t')
                    w.writerow([''] + self.descriptions[desc_type].keys())
                    for key in self.descriptions[desc_type].keys():
                        w.writerow(
                            [key] + [subdict.get(key, '') for subdict in self.descriptions[desc_type].values()]
                        )
            except OSError:
                print("Failed to open file!")

        # import json
        # save_file = open('save_file', 'w')
        # save_file.write( json.dumps(dico) )







