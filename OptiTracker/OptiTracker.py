import sys
import os
import datatable as dt
from typing import Tuple, Dict

# Get script directory to allow for relative imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


# Import native API class
from API_Remake.NatNetClient import NatNetClient

# Constants denoting asset types
PREFIX = "Prefix"
MARKER_SET = "MarkerSet"
LABELED_MARKER = "LabeledMarker"
LEGACY_MARKER_SET = "LegacyMarkerSet"
RIGID_BODY = "RigidBody"
SKELETON = "Skeleton"
ASSET_RIGID_BODY = "AssetRigidBody"
ASSET_MARKER = "AssetMarker"
FORCE_PLATE = "ForcePlate"
DEVICE = "Device"
CAMERA = "Camera"
SUFFIX = "Suffix"


# Wrapper for NatNetClient API class
class OptiTracker:
    def __init__(self) -> None:
        # NatNetClient instance
        self.client = self.init_client()

        self.frame_listeners = {
            PREFIX: True, MARKER_SET: True, LABELED_MARKER: True,
            LEGACY_MARKER_SET: True, RIGID_BODY: True, SKELETON: True,
            ASSET_RIGID_BODY: True, ASSET_MARKER: True, FORCE_PLATE: False,
            DEVICE: False, CAMERA: True, SUFFIX: True
        }

        self.description_listeners = {
            MARKER_SET: True, RIGID_BODY: True, SKELETON: True, FORCE_PLATE: False, 
            DEVICE: False, CAMERA: True, ASSET_RIGID_BODY: True, ASSET_MARKER: True
        }

        # Create dt.Frame dictionary
        self.frames = {
             'Prefix':dt.Frame(), 
            'MarkerSet':dt.Frame(), 
            'LabeledMarker':dt.Frame(),
            'LegacyMarkerSet':dt.Frame(),
            'RigidBody':dt.Frame(), 
            'Skeleton':dt.Frame(),
            'AssetRigidBody':dt.Frame(),
            'AssetMarker':dt.Frame(),
            'ForcePlate':dt.Frame(), 
            'Device':dt.Frame(), 
            'Suffix': dt.Frame()
        }

        self.descriptions = {
            asset_type: dt.Frame() for asset_type, store_value in self.description_listeners.items() if store_value
        }

    # Create NatNetClient instance
    def init_client(self) -> object:
        
        # Spawn client instance
        client = NatNetClient()

        # Set frame listeners
        client.frame_data_listener = self.collect_frame
        client.description_listener = self.collect_descriptions
        # client.rigid_bodies_frame_listener = self.get_rigid_bodies_frame_data
        # client.skeletons_frame_listener = self.get_skeletons_frame_data

        # # Set description listeners
        # client.skeleton_description_listener = self.get_skeleton_descriptions
        # client.rigid_body_description_listener = self.get_rigid_body_descriptions

        return client
    
    # Start NatNetClient, returns True if successful, False otherwise
    def start_client(self) -> bool:
        return self.client.startup()

    # Stop NatNetClient
    def stop_client(self) -> None:
        self.client.shutdown()

    # Get new frame data
    def collect_frame(self, frame_data: Dict[str, Tuple[Dict, ...]]) -> None:
        # Store frame data
        for asset_type, asset_data in frame_data.items():
            self.frames[asset_type].rbind(dt.Frame(asset_data))

    # Get new model descriptions
    def collect_descriptions(self, descriptions: Dict[str, Tuple[Dict, ...]]) -> None:
        for asset_type, asset_description in descriptions.items():
            self.descriptions[asset_type].rbind(dt.Frame(asset_description))
    
    # Get frame data for skeletons
    def get_skeletons_frame_data(self, frame_number, frame_data) -> None:
        # Store skeleton frame data
        self.frames['skeletons'][str(frame_number)] = frame_data

    # Get frame data for rigid bodies
    def get_rigid_bodies_frame_data(self, frame_number, frame_data) -> None:
        # Store rigid body frame data
        self.frames['rigid_bodies'][str(frame_number)] = frame_data

    # Get model descriptions for skeletons
    def get_skeleton_descriptions(self, desc_dict) -> None:
        # Store skeleton descriptions
        self.descriptions['skeletons'][desc_dict['name']] = desc_dict

    # Get model descriptions for rigid bodies
    def get_rigid_body_descriptions(self, desc_dict) -> None:
        # Store rigid body descriptions
        self.descriptions['rigid_bodies'][desc_dict['sz_name']] = desc_dict









