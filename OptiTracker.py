import sys
import os
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
        self.descriptions = {}
        self.frame = {}

    # Create NatNetClient instance
    def init_client(self) -> object:
        
        # Spawn client
        client = NatNetClient()
        client.full_description_listener = self.get_full_description
        #client.skeleton_description_listener = self.get_skeleton_descriptions
        #client.rigid_body_description_listener = self.get_rigid_body_descriptions
        client.rigid_bodies_frame_listener = self.get_rigid_bodies_frame_data
        client.skeletons_frame_listener = self.get_skeletons_frame_data

        return client
    
    def start_client(self) -> bool:
        return self.client.run()

    def stop_client(self) -> None:
        self.client.shutdown()

    def get_skeletons_frame_data(self, frame_data) -> None:
        self.frame['skeletons'] = frame_data

    def get_rigid_bodies_frame_data(self, frame_data) -> None:
        self.frame['rigid_bodies'] = frame_data
    
    def get_full_description(self, desc_dict) -> None:
        self.descriptions['full'] = desc_dict

    def get_skeleton_descriptions(self, desc_dict) -> None:
        self.descriptions['skeletons'] = desc_dict

    def get_rigid_body_descriptions(self, desc_dict) -> None:
        self.descriptions['rigid_bodies'] = desc_dict










