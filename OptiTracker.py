import sys
import os
import csv
from collections import OrderedDict
import json
import copy 
from Resources.APIs.Official.PythonClient.NatNetClient import NatNetClient

# TODO: is this necessary?
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

def isinstance_namedtuple(obj) -> bool:
    return (
            isinstance(obj, tuple) and
            hasattr(obj, '_asdict') and
            hasattr(obj, '_fields')
    )

class OptiTracker:
    def __init__(self) -> None:
        self.client = self.init_client()
        self.descriptions = OrderedDict()
        self.frame = None

    # Create NatNetClient instance
    def init_client(self) -> object:
        
        # Spawn client
        client = NatNetClient()
        #client.full_description_listener = self.get_full_description
        #client.skeleton_description_listener = self.get_skeleton_descriptions
        client.rigid_body_description_listener = self.get_rigid_body_descriptions
        client.new_frame_listener = self.get_mocap_frame

        return client
    
    def start_client(self) -> bool:
        return self.client.run()

    def stop_client(self) -> None:
        self.client.shutdown()

    def get_mocap_frame(self, data_dict, mocap_data):
        self.frame = data_dict
    
    def get_full_description(self, desc_dict) -> None:
        self.descriptions['full'] = desc_dict
        self.client.full_description_listener = None

    def get_skeleton_descriptions(self, desc_dict) -> None:
        self.descriptions['skeletons'] = desc_dict
        self.client.skeleton_description_listener = None

    def get_rigid_body_descriptions(self, desc_dict) -> None:
        print(f"Type of desc_dict is {type(desc_dict)}")
        self.descriptions['rigid_bodies'] = desc_dict
        self.client.rigid_body_description_listener = None

    def dump_to_json(self, to_dump) -> None:
        dump = copy.deepcopy(self.descriptions[to_dump])

        for key in dump.keys():
            if isinstance_namedtuple(dump[key]):
                dump[key] = dump[key]._asdict()

        with open('out\data.json', 'w') as json_file:
            json.dump(dump, json_file)

    def save_description(self, desc_type) -> None:
        print(f"Attempting to write {desc_type}...\n")
        if self.descriptions[desc_type] is None:
            print(f"Description of {desc_type} is None")
        else:
            print(f"{desc_type} is not None\nAttempting to write...\n")
            try:
                with open(f'out\{desc_type}_desc_dict.csv', 'w') as file:
                    print("file opened")
                    w = csv.writer(file, delimiter = '\t')
                    w.writerow([''] + list(self.descriptions[desc_type].keys()))
                    for key in self.descriptions[desc_type].keys():
                        for value in self.descriptions[desc_type].values():
                            if type(value):pass
                            
                        w.writerow(
                            [key] + [subdict.get(key.encode('utf-8'), '') for subdict in self.descriptions[desc_type].values()]
                        )
            except OSError:
                print("Failed to open file!")









