import socket
import struct
from threading import Thread
import time
from DataUnpackers import *
from DescriptionUnpackers import *
from typing import Any, Union, List, Tuple, Callable
import datatable as dt

from pprint import pprint

def trace( *args ):
    # uncomment the one you want to use
    #print( "".join(map(str,args)) )
    pass

#Used for Data Description functions
def trace_dd( *args ):
    # uncomment the one you want to use
    #print( "".join(map(str,args)) )
    pass

#Used for MoCap Frame Data functions
def trace_mf( *args ):
    # uncomment the one you want to use
    #print( "".join(map(str,args)) )
    pass

def get_message_id(bytestream: bytes) -> int:
    message_id = int.from_bytes( bytestream[0:2], byteorder='little' )
    return message_id


class NatNetClient:






    # print_level = 0 off
    # print_level = 1 on
    # print_level = >1 on / print every nth mocap frame
    print_level = 20
    
    def __init__( self ) -> None:

        self.frame_num = 1
        self.desc_num = 1
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


        # Change this value to the IP address of the NatNet server.
        self.settings = {
            "server_ip": "127.0.0.1",
            # Change this value to the IP address of your local network interface
            "local_ip": "127.0.0.1",
            # This should match the multicast address listed in Motive's streaming settings.
            "multicast": "239.255.42.99",
            # NatNet Command channel
            "command_port": 1510,
            # NatNet Data channel
            "data_port": 1511,
            "use_multicast": True,
            # Set Application Name
            "apllication_name": "Not Set",
            # NatNet stream version server is capable of. This will be updated during initialization only.
            "nat_net_stream_version_server": [0,0,0,0],
            # NatNet stream version. This will be updated to the actual version the server is using during runtime.
            "nat_net_requested_version": [0,0,0,0],
            # server stream version. This will be updated to the actual version the server is using during initialization.
            "server_version": [0,0,0,0],
            # Lock values once run is called
            "is_locked": False,
            # Server has the ability to change bitstream version
            "can_change_bitstream_version": False
        }

        # Flags determining which assets to return in the frame data
        self.return_frame_data = {
            PREFIX: True,
            MARKER_SET: True,
            LABELED_MARKER: True,
            LEGACY_MARKER_SET: True,
            RIGID_BODY: True,
            SKELETON: True,
            ASSET_RIGID_BODY: True,
            ASSET_MARKER: True,
            FORCE_PLATE: False,
            DEVICE: False,
            CAMERA: True,
            SUFFIX: True
        } 

        # Flags determining which assets to return in the data descriptions
        self.return_description = {
            MARKER_SET: True,
            RIGID_BODY: True,
            SKELETON: True,
            FORCE_PLATE: False,
            DEVICE: False,
            CAMERA: True,
            ASSET_RIGID_BODY: True,
            ASSET_MARKER: True
        }

        self.frame_data_listener = None
        self.description_listener = None

        self.command_thread = None
        self.data_thread = None
        self.command_socket = None
        self.data_socket = None

        self.stop_threads=False


    # Constants corresponding to Client/server message ids
    NAT_CONNECT               = 0
    NAT_SERVERINFO            = 1
    NAT_REQUEST               = 2
    NAT_RESPONSE              = 3
    NAT_REQUEST_MODELDEF      = 4
    NAT_MODELDEF              = 5
    NAT_REQUEST_FRAMEOFDATA   = 6
    NAT_FRAMEOFDATA           = 7
    NAT_MESSAGESTRING         = 8
    NAT_DISCONNECT            = 9
    NAT_KEEPALIVE             = 10
    NAT_UNRECOGNIZED_REQUEST  = 100
    NAT_UNDEFINED             = 999999.9999

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

    # Functions for unpacking frame data, called by __unpack_frame_data #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __unpack_asset_count_and_size(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> Tuple[int, int, int]:
        asset_count = int.from_bytes( bytestream[offset:offset+4], byteorder='little')
        offset += 4
        asset_bytesize = int.from_bytes( bytestream[offset:offset+4], byteorder='little')
        offset += 4

        return offset, asset_count, asset_bytesize
    
    def __unpack_prefix_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        prefix = prefixData(bytestream, offset, NatNetStreamVersion)
        self.frame_data.log("Prefix", prefix.export())

        print(f'\n\nPrefix log:\n')
        pprint(self.frame_data._framedata['Prefix'])

        offset += prefix.relative_offset()

        return offset

    def __unpack_legacy_marker_sets_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        #offset, num_legacy_marker_sets, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)
        # print(f"\n\nnum_legacy: {num_legacy_marker_sets}\n\n")

        #for i in range( 0, num_legacy_marker_sets ):
        legacy_marker_set = legacyMarkerSetData(bytestream, offset, NatNetStreamVersion)
        self.frame_data.log("LegacyMarkerSet", legacy_marker_set.export())
        pprint(self.frame_data._framedata["LegacyMarkerSet"])
        offset += legacy_marker_set.relative_offset()
 
        return offset

    def __unpack_labeled_marker_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_labeled_markers, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_labeled_markers ):
            labeled_marker = labeledMarkerData(bytestream, offset, NatNetStreamVersion)
            self.frame_data.log("LabeledMarker", labeled_marker.export())
            pprint(self.frame_data._framedata['LabeledMarker'])
            offset += labeled_marker.relative_offset()

        return offset
    
    def __unpack_marker_sets_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        
        offset, num_marker_sets, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)

        for i in range( 0, num_marker_sets ):
            marker_set = markerSetData(bytestream, offset, NatNetStreamVersion)
            self.frame_data.log("MarkerSet", marker_set.export())
            pprint(self.frame_data._framedata['MarkerSet'])
            offset += marker_set.relative_offset()

        return offset

    def __unpack_rigid_bodies_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_rigid_bodies, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_rigid_bodies ):
            rigid_body = rigidBodyData(bytestream, offset, NatNetStreamVersion)
            self.frame_data.log("RigidBody", rigid_body.export())
            pprint(self.frame_data._framedata['RigidBody'])
            offset += rigid_body.relative_offset()

        return offset

    def __unpack_skeletons_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_skeletons, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_skeletons ):
            skeleton = skeletonData(bytestream, offset, NatNetStreamVersion)
            self.frame_data.log("Skeleton", skeleton.export())
            pprint(self.frame_data._framedata['Skeleton'])
            offset += skeleton.relative_offset()

        return offset

    def __unpack_assets_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset, num_assets, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        # for i in range( 0, num_assets ):
        asset = assetData(bytestream, offset, NatNetStreamVersion)
        self.frame_data.log("AssetRigidBody", asset.export("AssetRigidBody"))
        pprint(self.frame_data._framedata['AssetRigidBody'])
        self.frame_data.log("AssetMarker", asset.export("AssetMarker"))
        pprint(self.frame_data._framedata['AssetMarker'])
        print(f"\nAsset relative offset: {asset.relative_offset()}\n")
        offset += (asset.relative_offset() + 2)

        return offset

    def __unpack_force_plates_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_force_plates, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_force_plates ):
            force_plate_data = forcePlateData(bytestream[offset:])
            self.frame_data.log("ForcePlate", force_plate_data.export())
            offset += force_plate_data.relative_offset()

        return offset

    def __unpack_devices_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_devices, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_devices ):
            device_data = deviceData(bytestream[offset:])
            self.frame_data.log("Device", device_data.export())
            offset += device_data.relative_offset()

        return offset

    def __unpack_frame_suffix_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        suffix = suffixData(bytestream, offset, NatNetStreamVersion)
        self.frame_data.log("Suffix", suffix.export())
        pprint(self.frame_data['Suffix'])
        offset += suffix.relative_offset()

        return offset

    def __unpack_frame_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        bytestream = memoryview(bytestream)

        offset += 4

        # with open(f"frame_data_bytestream_{self.frame_num}.bin", 'wb') as f:
        #     f.write(bytestream)

        self.frame_num += 1

        self.frame_data = frameData()

        unpack_functions = [
            self.__unpack_prefix_data,
            self.__unpack_marker_sets_data,
            self.__unpack_legacy_marker_sets_data,
            self.__unpack_rigid_bodies_data,
            self.__unpack_skeletons_data,
            self.__unpack_assets_data,
            # self.__unpack_labeled_marker_data,
            # self.__unpack_force_plates_data,
            # self.__unpack_devices_data,
            # self.__unpack_frame_suffix_data
        ]

        for unpack_function in unpack_functions:
            offset = unpack_function(bytestream, offset, NatNetStreamVersion)

        frames = {
            'Prefix':dt.Frame(), 
            'MarkerSet':dt.Frame(), 
            'LegacyMarkerSet':dt.Frame(),
            'RigidBody':dt.Frame(), 
            'Skeleton':dt.Frame(),
            'AssetRigidBody':dt.Frame(),
            'AssetMarker':dt.Frame()
        }

        data = self.frame_data.export()

        for asset_type in data.keys():
            for asset_data in data[asset_type]:
                frames[asset_type].rbind(dt.Frame(asset_data))
                print(frames[asset_type])

        data
            

        # frame = self.frame_data.export((
        #     asset_type for asset_type in self.return_frame_data.keys() 
        #     if self.return_frame_data[asset_type]
        # ))
            


        #self.frame_data_listener(self.frame_data.export())
        
        return offset
    
    def manual_unpack_frame_data(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                bytestream = f.read()

                self.__unpack_frame_data(bytestream, 0, None)

        except Exception as e:
            print(f"Error: {e}")


    def __unpack_marker_set_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        marker_set_desc = markerSetDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("MarkerSet", marker_set_desc.export())
        pprint(f"MarkerSet Log:\n{self.frame_data._framedata['MarkerSet']}")
        offset += marker_set_desc.relative_offset()

        return offset

    def __unpack_rigid_body_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        #offset += 4
        rigid_body_desc = rigidBodyDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("RigidBody", rigid_body_desc.export())

        pprint(f"Rigid Body Log:\n{self.frame_data._framedata['RigidBody']}")
        offset += rigid_body_desc.relative_offset()

        return offset

    def __unpack_skeleton_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        skeleton_desc = skeletonDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("Skeleton", skeleton_desc.export())
        pprint(f"Skeleton Log:\n{self.frame_data._framedata['Skeleton']}")
        offset += skeleton_desc.relative_offset()

        return offset

    def __unpack_force_plate_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        force_plate_desc = forcePlateDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("ForcePlate", force_plate_desc.export())
        offset += force_plate_desc.relative_offset()
    
        return offset

    def __unpack_device_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        device_desc = deviceDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("Device", device_desc.export())
        offset += device_desc.relative_offset()

        return offset

    def __unpack_camera_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        camera_desc = cameraDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("Camera", camera_desc.export())
        offset += camera_desc.relative_offset()

        return offset

    def __unpack_asset_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        asset_desc = assetDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("Asset", asset_desc.export())
        pprint(f"Asset Log:\n{self.frame_data._framedata['Asset']}")
        offset += asset_desc.relative_offset()

        return offset

    def __unpack_descriptions(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        self.descriptions = Descriptions()

        # with open(f"descriptions_frame_{self.desc_num}.bin", 'wb') as f:
        #     f.write(bytestream[offset:])
        
        # # of data sets to process
        dataset_count = int.from_bytes( bytestream[offset:offset+4], byteorder='little' )
        offset += 4

        unpack_functions = {
            0: self.__unpack_marker_set_description,
            1: self.__unpack_rigid_body_description,
            2: self.__unpack_skeleton_description,
            3: self.__unpack_force_plate_description,
            4: self.__unpack_device_description,
            5: self.__unpack_camera_description,
            6: self.__unpack_asset_description
        }

        for i in range( 0, dataset_count ):
            data_type = int.from_bytes( bytestream[offset:offset+4], byteorder='little' )
            offset += 4

            try:
                if data_type in unpack_functions:
                    offset += 4
                    offset += unpack_functions[data_type](bytestream, offset, NatNetStreamVersion)
            except KeyError:
                print(f"NatNetClient.__unpack_descriptions | Decode Error; Supplied unknown asset type: {data_type}")


        # description = self.descriptions.export((
        #     asset_type for asset_type in self.return_description.keys() 
        #     if self.return_description[asset_type]
        # ))

        # self.description_listener(description)
        
        return offset

    def manual_unpack_description_data(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                bytestream = f.read()

                self.__unpack_descriptions(bytestream, 0, None)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    nnc = NatNetClient()
    nnc.manual_unpack_frame_data("../frame_data_bytestream_1.bin")
    #nnc.manual_unpack_description_data("../descriptions_frame_1.bin")
