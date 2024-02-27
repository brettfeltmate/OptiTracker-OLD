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

       # Functions for unpacking frame data, called by __unpack_frame_data #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def __unpack_prefix_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:        
        prefix = prefixData(unparsed_bytestream, NatNetStreamVersion)
        self.frame_data.log("Prefix", prefix.data())

        return prefix.relative_offset()

    def __unpack_legacy_marker_set_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        if Int32ul.parse(unparsed_bytestream) == 0:
            return 8
        # Peak ahead to get packet size, TODO: add optional flag to skip, seeking forward in stream
        nBytes = Int32ul.parse(unparsed_bytestream[4:])

        legacy_marker_set = legacyMarkerSetData(unparsed_bytestream, NatNetStreamVersion)
        self.frame_data.log("LegacyMarkerSet", legacy_marker_set.data())
 
        return legacy_marker_set.relative_offset()

    def __unpack_labeled_marker_set_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        # Peak ahead to get packet size, TODO: add optional flag to skip, seeking forward in stream
        nBytes = Int32ul.parse(unparsed_bytestream[4:])

        labeled_marker_set = labeledMarkerSetData(unparsed_bytestream, NatNetStreamVersion)
        self.frame_data.log("LabeledMarkerSet", labeled_marker_set.data())
        

        return labeled_marker_set.relative_offset()
    
    def __unpack_marker_sets_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        if Int32ul.parse(unparsed_bytestream) == 0:
            return 8
        # Peak ahead to get packet size, TODO: add optional flag to skip, seeking forward in stream
        nBytes = Int32ul.parse(unparsed_bytestream[4:])

        marker_sets = markerSetsData(unparsed_bytestream, NatNetStreamVersion)
        self.frame_data.log("MarkerSets", marker_sets.data())

        return marker_sets.relative_offset()

    def __unpack_rigid_bodies_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        if Int32ul.parse(unparsed_bytestream) == 0:
            return 8
        # Peak ahead to get packet size, TODO: add optional flag to skip, seeking forward in stream
        nBytes = Int32ul.parse(unparsed_bytestream[4:])

        rigid_bodies = rigidBodiesData(unparsed_bytestream, NatNetStreamVersion)
        self.frame_data.log("RigidBodies", rigid_bodies.data())

        return rigid_bodies.relative_offset()

    def __unpack_skeletons_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        # Peak ahead to get packet size, TODO: add optional flag to skip, seeking forward in stream
        nBytes = Int32ul.parse(unparsed_bytestream[4:])


        skeletons = skeletonsData(unparsed_bytestream, NatNetStreamVersion)
        self.frame_data.log("Skeletons", skeletons.data())

        return skeletons.relative_offset()

    def __unpack_assets_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        # Peak ahead to get packet size, TODO: add optional flag to skip, seeking forward in stream
        count = Int32ul.parse(unparsed_bytestream)
        nBytes = Int32ul.parse(unparsed_bytestream[4:])

        assets = assetsData(unparsed_bytestream, NatNetStreamVersion)
        self.frame_data.log("AssetRigidBodies", assets.data("AssetRigidBodies"))
        self.frame_data.log("AssetMarkers", assets.data("AssetMarkers"))

        return assets.relative_offset()

    def __unpack_force_plates_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        # Peak ahead to get packet size, TODO: add optional flag to skip, seeking forward in stream
        nBytes = Int32ul.parse(unparsed_bytestream[4:])


        force_plates = forcePlatesData(unparsed_bytestream)
        self.frame_data.log("ForcePlates", force_plates.data())

        return force_plates.relative_offset()

    def __unpack_devices_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        # Peak ahead to get packet size, TODO: add optional flag to skip, seeking forward in stream
        nBytes = Int32ul.parse(unparsed_bytestream[4:])

        devices = devicesData(unparsed_bytestream)
        self.frame_data.log("Devices", devices.data())

        return devices.relative_offset()

    def __unpack_frame_suffix_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        suffix = suffixData(unparsed_bytestream, NatNetStreamVersion)
        self.frame_data.log("Suffix", suffix.data())

        return suffix.relative_offset()

    def __unpack_frame_data(self, unparsed_bytestream: bytes, NatNetStreamVersion: List[int] = None) -> int:
        unparsed_bytestream = memoryview(unparsed_bytestream)
        packet_size_maybe = Int32ul.parse(unparsed_bytestream)

        self.frame_offset = 4

        # with open(f"frame_data_bytestream_{self.frame_num}.bin", 'wb') as f:
        #     f.write(bytestream)



        self.frame_data = frameData()

        unpack_functions = [
            self.__unpack_prefix_data,
            self.__unpack_marker_sets_data,
            self.__unpack_legacy_marker_set_data,
            self.__unpack_rigid_bodies_data,
            self.__unpack_skeletons_data,
            self.__unpack_assets_data,
            self.__unpack_labeled_marker_set_data,
            # self.__unpack_force_plates_data,
            # self.__unpack_devices_data,
            # self.__unpack_frame_suffix_data
        ]

        for unpack_function in unpack_functions:
            self.frame_offset += unpack_function(unparsed_bytestream[self.frame_offset:], NatNetStreamVersion)


        print(f'\n\nPacket Size Maybe: {packet_size_maybe}, Packet Size unpacked: {self.frame_offset}\n\n')

        # frame = self.frame_data.export((
        #     asset_type for asset_type in self.return_frame_data.keys() 
        #     if self.return_frame_data[asset_type]
        # ))
            
        frames = {
            'Prefix':dt.Frame(), 
            'MarkerSets':dt.Frame(), 
            'LegacyMarkerSet':dt.Frame(),
            'RigidBodies':dt.Frame(), 
            'Skeletons':dt.Frame(),
            'AssetRigidBodies':dt.Frame(),
            'AssetMarkers':dt.Frame(),
            'LabeledMarkerSet':dt.Frame(),
        }

        data = self.frame_data.export()

        for asset_type in data.keys():
            for asset_data in data[asset_type]:
                frames[asset_type].rbind(dt.Frame(asset_data))
                print(frames[asset_type])

        for key in frames.keys():
            frames[key].to_csv(f"{key}_frame_redux.csv")
            

        # frame = self.frame_data.export((
        #     asset_type for asset_type in self.return_frame_data.keys() 
        #     if self.return_frame_data[asset_type]
        # ))
            


        #self.frame_data_listener(self.frame_data.export())
        
        return self.frame_offset
    
    def manual_unpack_frame_data(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                bytestream = f.read()

                self.__unpack_frame_data(bytestream, None)

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
