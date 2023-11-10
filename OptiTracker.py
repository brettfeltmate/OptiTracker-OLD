# Get script directory to allow for relative imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import sys
import os

# Import native API class
from Resources.APIs.Official.PythonClient.NatNetClient import NatNetClient

# Wrapper for NatNetClient API class
class OptiTracker:
    def __init__(self) -> None:
        # NatNetClient instance
        self.client = self.init_client()

        # Initialize data containers
        self.descriptions = {}  # Model descriptions, keys denote model types
        self.frames = {}        # Frame data, keys denote frame numbers

    # Create NatNetClient instance
    def init_client(self) -> object:
        
        # Spawn client instance
        client = NatNetClient()

        # Set frame listeners
        client.rigid_bodies_frame_listener = self.get_rigid_bodies_frame_data
        client.skeletons_frame_listener = self.get_skeletons_frame_data

        # Set description listeners
        client.skeleton_description_listener = self.get_skeleton_descriptions
        client.rigid_body_description_listener = self.get_rigid_body_descriptions

        return client
    
    # Start NatNetClient, returns True if successful, False otherwise
    def start_client(self) -> bool:
        return self.client.run()

    # Stop NatNetClient
    def stop_client(self) -> None:
        self.client.shutdown()

    # Get frame data for skeletons
    def get_skeletons_frame_data(self, frame_number, frame_data) -> None:
        # Store skeleton frame data
        self.frames[frame_number]['skeletons'] = frame_data

    # Get frame data for rigid bodies
    def get_rigid_bodies_frame_data(self, frame_number, frame_data) -> None:
        # Store rigid body frame data
        self.frames[frame_number]['rigid_bodies'] = frame_data

    # Get model descriptions for skeletons
    def get_skeleton_descriptions(self, desc_dict) -> None:
        # Store skeleton descriptions
        self.descriptions['skeletons'] = desc_dict

    # Get model descriptions for rigid bodies
    def get_rigid_body_descriptions(self, desc_dict) -> None:
        # Store rigid body descriptions
        self.descriptions['rigid_bodies'] = desc_dict










