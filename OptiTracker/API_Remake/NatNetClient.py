#Copyright © 2018 Naturalpoint
#
#Licensed under the Apache License, Version 2.0 (the "License")
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

# OptiTrack NatNet direct depacketization library for Python 3.x

import socket
import struct
from threading import Thread
import time
from .DataUnpackers import *
from .DescriptionUnpackers import *
from typing import Any, Union, List, Tuple, Callable

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
        prefix_data = prefixData(bytestream, offset, NatNetStreamVersion)
        self.frame_data.log("Prefix", prefix_data.export())

        print(f'\n\nPrefix log:\n')
        pprint(self.frame_data._framedata['Prefix'])

        offset += prefix_data.relative_offset()

        return offset

    def __unpack_legacy_marker_sets_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset, num_legacy_marker_sets, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)
        # print(f"\n\nnum_legacy: {num_legacy_marker_sets}\n\n")

        # for i in range( 0, num_legacy_marker_sets ):
        legacy_marker_set_data = legacyMarkerSetData(bytestream, offset, NatNetStreamVersion)
        self.frame_data.log("LegacyMarkerSet", legacy_marker_set_data.export())
        pprint(self.frame_data._framedata["LegacyMarkerSet"])
        offset += legacy_marker_set_data.relative_offset()
 
        return offset

    def __unpack_labeled_marker_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_labeled_markers, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_labeled_markers ):
            labeled_marker_data = labeledMarkerData(bytestream, offset, NatNetStreamVersion)
            self.frame_data.log("LabeledMarker", labeled_marker_data.export())
            offset += labeled_marker_data.relative_offset()

        return offset
    
    def __unpack_marker_sets_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        print(f'\n\n\nunpack_marker_sets_data; passed offset = {offset}\n\n\n')
        
        offset, num_marker_sets, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)
  

        print(f'\n\nnum_marker_sets: {num_marker_sets}\n\n')

        for i in range( 0, num_marker_sets ):
            marker_set_data = markerSetData(bytestream, offset, NatNetStreamVersion)
            self.frame_data.log("MarkerSet", marker_set_data.export())
            offset += marker_set_data.relative_offset()

        return offset

    def __unpack_rigid_bodies_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_rigid_bodies, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_rigid_bodies ):
            rigid_body_data = rigidBodyData(bytestream, offset, NatNetStreamVersion)
            self.frame_data.log("RigidBody", rigid_body_data.export())
            offset += rigid_body_data.relative_offset()

        return offset

    def __unpack_skeletons_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_skeletons, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_skeletons ):
            skeleton_data = skeletonData(bytestream[offset:])
            self.frame_data.log("Skeleton", skeleton_data.export())
            offset += skeleton_data.relative_offset()

        return offset

    def __unpack_assets_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        offset, num_assets, _ = self.__unpack_asset_count_and_size(bytestream, offset, NatNetStreamVersion)


        for i in range( 0, num_assets ):
            asset_data = assetData(bytestream, offset, NatNetStreamVersion)
            self.frame_data.log("Asset", asset_data.export())
            offset += asset_data.relative_offset()

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
        frame_suffix_data = suffixData(bytestream, offset, NatNetStreamVersion)
        self.frame_data.log("Suffix", frame_suffix_data.export())
        offset += frame_suffix_data.relative_offset()

        return offset

    def __unpack_frame_data(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        bytestream = memoryview(bytestream)

        with open(f"frame_data_bytestream_{self.frame_num}.bin", 'wb') as f:
            f.write(bytestream)

        self.frame_num += 1

        self.frame_data = frameData()

        unpack_functions = [
            self.__unpack_prefix_data,
            self.__unpack_marker_sets_data,
            self.__unpack_legacy_marker_sets_data,
            self.__unpack_rigid_bodies_data,
            self.__unpack_skeletons_data,
            self.__unpack_assets_data,
            self.__unpack_labeled_marker_data,
            self.__unpack_force_plates_data,
            self.__unpack_devices_data,
            self.__unpack_frame_suffix_data
        ]

        for unpack_function in unpack_functions:
            offset = unpack_function(bytestream, offset, NatNetStreamVersion)

        # frame = self.frame_data.export((
        #     asset_type for asset_type in self.return_frame_data.keys() 
        #     if self.return_frame_data[asset_type]
        # ))
            


        self.frame_data_listener(self.frame_data.export())
        
        return offset


    # Functions for unpacking descriptions, called by __unpack_descriptions #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __unpack_marker_set_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        marker_set_desc = markerSetDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("MarkerSet", marker_set_desc.export())
        offset += marker_set_desc.relative_offset()

        return offset

    def __unpack_rigid_body_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        rigid_body_desc = rigidBodyDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("RigidBody", rigid_body_desc.export())
        offset += rigid_body_desc.relative_offset()

        return offset

    def __unpack_skeleton_description(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        # offset += 4
        skeleton_desc = skeletonDescription(bytestream, offset, NatNetStreamVersion)
        self.descriptions.log("Skeleton", skeleton_desc.export())
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
        offset += asset_desc.relative_offset()

        return offset

    def __unpack_descriptions(self, bytestream: bytes, offset: int, NatNetStreamVersion: List[int] = None) -> int:
        self.descriptions = Descriptions()

        with open(f"descriptions_frame_{self.desc_num}.bin", 'wb') as f:
            f.write(bytestream[offset:])
        
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

            if data_type in unpack_functions:
                offset += 4
                offset += unpack_functions[data_type](bytestream, offset, NatNetStreamVersion)
            else:
                print(f"NatNetClient.__unpack_descriptions | Decode Error; Supplied unknown asset type: {data_type}")


        description = self.descriptions.export((
            asset_type for asset_type in self.return_description.keys() 
            if self.return_description[asset_type]
        ))

        self.description_listener(description)
        
        return offset



    # Private Utility functions #
    # # # # # # # # # # # # # # #

    def __handle_response_message(self, bytestream: bytes, offset: int, packet_size: int, message_id: int) -> int:
        if message_id == self.NAT_RESPONSE:
            if packet_size == 4:
                command_response = int.from_bytes(bytestream[offset:offset+4], byteorder='little')
                trace(f"Command response: {command_response} - {[bytestream[offset+i] for i in range(4)]}")
                offset += 4
            else:
                message, _, _ = bytes(bytestream[offset:]).partition(b'\0')
                if message.decode('utf-8').startswith('Bitstream'):
                    nn_version = self.__unpack_bitstream_info(bytestream[offset:], packet_size)
                    # Update the server version
                    self.settings["nat_net_stream_version_server"] = [int(v) for v in nn_version] + [0]*(4 - len(nn_version))
                trace(f"Command response: {message.decode('utf-8')}")
                offset += len(message) + 1
        elif message_id == self.NAT_UNRECOGNIZED_REQUEST:
            trace(f"Message ID:{message_id:.1f} (NAT_UNRECOGNIZED_REQUEST)")
            trace(f"Packet Size: {packet_size}")
        elif message_id == self.NAT_MESSAGESTRING:
            trace(f"Message ID:{message_id:.1f} (NAT_MESSAGESTRING), Packet Size: {packet_size}")
            message, _, _ = bytes(bytestream[offset:]).partition(b'\0')
            trace(f"\n\tReceived message from server: {message.decode('utf-8')}")
            offset += len(message) + 1

        return offset

    # Create a command socket to attach to the NatNet stream
    def __create_command_socket(self) -> Union[socket.socket, None]:
        try:
            if self.settings['use_multicast']:
                # Multicast case
                result = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
                result.bind(('', 0))
                result.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            else:
                # Unicast case
                result = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                result.bind((self.settings["local_ip"], 0))

            # Common settings for both cases
            result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result.settimeout(2.0)  # set timeout to allow for keep alive messages
            return result

        except socket.error as msg:
            print(f"ERROR: command socket error occurred:\n{msg}")
            print(f"Check Motive/Server mode requested mode agreement. You requested {'Multicast' if self.settings['use_multicast'] else 'Unicast'}")
        except (socket.herror, socket.gaierror):
            print("ERROR: command socket herror or gaierror occurred")
        except socket.timeout:
            print("ERROR: command socket timeout occurred. Server not responding")

        return None

    # Create a data socket to attach to the NatNet stream
    def __create_data_socket(self, port: int) -> socket.socket:
        try:
            result = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            if self.settings["use_multicast"]:
                # Multicast case
                result.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.settings['multicast']) + socket.inet_aton(self.settings["local_ip"]))
                result.bind((self.settings["local_ip"], port))
            else:
                # Unicast case
                result.bind(('', 0))
                if self.settings["multicast"] != "255.255.255.255":
                    result.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.settings['multicast']) + socket.inet_aton(self.settings["local_ip"]))

            return result

        except socket.error as msg:
            print(f"ERROR: data socket error occurred:\n{msg}")
            print(f"Check Motive/Server mode requested mode agreement. You requested {'Multicast' if self.settings['use_multicast'] else 'Unicast'}")
        except (socket.herror, socket.gaierror):
            print("ERROR: data socket herror or gaierror occurred")
        except socket.timeout:
            print("ERROR: data socket timeout occurred. Server not responding")

        return None

    # For local use; updates NatNet version and server capabilities
    def __unpack_server_info(self, bytestream: bytes, offset: int) -> int:
        # Server name
        self.settings["application_name"], _, _ = bytes(bytestream[offset:offset+256]).partition(b'\0')
        self.settings["application_name"] = str(self.settings["application_name"], "utf-8")

        # Server Version info
        self.settings["server_version"] = struct.unpack('BBBB', bytestream[offset+256:offset+260])

        # NatNet Version info
        self.settings["nat_net_stream_version_server"] = struct.unpack('BBBB', bytestream[offset+260:offset+264])

        if self.settings["nat_net_requested_version"][:2] == [0, 0]:
            print(f"Resetting requested version to {self.settings['nat_net_stream_version_server']} from {self.settings['nat_net_requested_version']}")
            self.settings["nat_net_requested_version"] = self.settings["nat_net_stream_version_server"]
            # Determine if the bitstream version can be changed
            self.settings["can_change_bitstream_version"] = self.settings["nat_net_stream_version_server"][0] >= 4 and not self.settings["use_multicast"]

        trace_mf(f"Sending Application Name: {self.settings['application_name']}")
        trace_mf(f"NatNetVersion: {self.settings['nat_net_stream_version_server']}")
        trace_mf(f"ServerVersion: {self.settings['server_version']}")
        return offset + 264

    # For local use; updates server bitstream version
    def __unpack_bitstream_info(self, bytestream: bytes) -> list[int]:
        nn_version=[]
        inString = bytestream.decode('utf-8')
        messageList = inString.split(',')
        if( len(messageList) > 1 ):
            if( messageList[0] == 'Bitstream'):
                nn_version=messageList[1].split('.')
        return nn_version

    def __command_thread_function(self, in_socket: socket.socket, stop: Callable, gprint_level: int) -> int:
        message_id_dict = {}
        if not self.settings["use_multicast"]:
            in_socket.settimeout(2.0)

        # 64k buffer size
        recv_buffer_size = 64 * 1024
        while not stop():
            # Block for input
            try:
                bytestream, addr = in_socket.recvfrom(recv_buffer_size)
            except (socket.error, socket.herror, socket.gaierror, socket.timeout) as e:
                if stop() or isinstance(e, socket.timeout) and self.use_multicast:
                    print(f"ERROR: command socket access error occurred:\n{e}")
                if isinstance(e, socket.error):
                    print("shutting down")
                return 1

            if bytestream:
                # peek ahead at message_id
                message_id = get_message_id(bytestream)
                tmp_str = f"mi_{message_id:.1f}"
                message_id_dict[tmp_str] = message_id_dict.get(tmp_str, 0) + 1

                print_level = gprint_level()
                if message_id == self.NAT_FRAMEOFDATA and print_level > 0:
                    print_level = 1 if message_id_dict[tmp_str] % print_level == 0 else 0

                message_id = self.__process_message(bytestream)
                bytestream = bytearray()

            if not self.settings['use_multicast'] and not stop():
                self.send_keep_alive(in_socket, self.settings["server_ip"], self.settings["command_port"])

        return 0

    def __data_thread_function(self, in_socket: socket.socket, stop: Callable, gprint_level: Callable) -> int:
        message_id_dict = {}
        # 64k buffer size
        recv_buffer_size = 64 * 1024

        while not stop():
            # Block for input
            try:
                bytestream, addr = in_socket.recvfrom(recv_buffer_size)
            except (socket.error, socket.herror, socket.gaierror, socket.timeout) as e:
                if not stop() or isinstance(e, socket.timeout):
                    print(f"ERROR: data socket access error occurred:\n{e}")
                return 1

            if bytestream:
                # peek ahead at message_id
                message_id = get_message_id(bytestream)
                tmp_str = f"mi_{message_id:.1f}"
                message_id_dict[tmp_str] = message_id_dict.get(tmp_str, 0) + 1

                print_level = gprint_level()
                if message_id == self.NAT_FRAMEOFDATA and print_level > 0:
                    print_level = 1 if message_id_dict[tmp_str] % print_level == 0 else 0

                message_id = self.__process_message(bytestream)
                bytestream = bytearray()

        return 0

    def __process_message(self, bytestream: bytes) -> int:
        message_id = get_message_id(bytestream)
        packet_size = int.from_bytes(bytestream[2:4], byteorder='little')

        # skip the 4 bytes for message ID and packet_size
        offset = 4
        if message_id == self.NAT_FRAMEOFDATA:
            offset += self.__unpack_frame_data(bytestream, offset, NatNetStreamVersion=None)

        elif message_id == self.NAT_MODELDEF:
            offset += self.__unpack_descriptions(bytestream, offset, NatNetStreamVersion=None)

        elif message_id == self.NAT_SERVERINFO:
            trace(f"Message ID: {message_id:.1f} (NAT_SERVERINFO), packet size: {packet_size}")
            offset += self.__unpack_server_info(bytestream, offset)

        elif message_id in [self.NAT_RESPONSE, self.NAT_UNRECOGNIZED_REQUEST, self.NAT_MESSAGESTRING]:
            offset = self.__handle_response_message(bytestream, offset, packet_size, message_id)
        
        else:
            trace(f"Message ID: {message_id:.1f} (UNKNOWN)")
            trace(f"ERROR: Unrecognized packet type of size: {packet_size}")

        trace("End Packet\n-----------------")
        return message_id



    # Public Utility Functions  #
    # # # # # # # # # # # # # # #

    def set_client_address(self, local_ip_address: str) -> None:
        if not self.settings["is_locked"]:
            self.settings["local_ip"] = local_ip_address

    def get_client_address(self) -> str:
        return self.settings["local_ip"]

    def set_server_address(self, server_ip_address: str) -> None:
        if not self.settings["is_locked"]:
            self.settings["server_ip"] = server_ip_address

    def get_server_address(self) -> str:
        return self.settings["server_ip"]

    def set_use_multicast(self, use_multicast: bool = True) -> None:
        if not self.settings["is_locked"]:
            self.use_multicast = use_multicast

    def can_change_bitstream_version(self) -> bool:
        return self.settings["can_change_bitstream_version"]

    def set_nat_net_version(self, NatNetRequestedVersion: list) -> None:
        """checks to see if stream version can change, then changes it with position reset"""
        if self.settings["can_change_bitstream_version"] and (NatNetRequestedVersion[0:2] != self.settings["nat_net_requested_version"][0:2]):
            sz_command = f"Bitstream {NatNetRequestedVersion[0]}.{NatNetRequestedVersion[1]}"
            if self.send_command(sz_command) >= 0:
                self.settings["nat_net_requested_version"] = NatNetRequestedVersion
                print("changing bitstream MAIN")

                # force frame send and play reset
                self.send_command("TimelinePlay")
                time.sleep(0.1)
                self.send_commands(["TimelinePlay", "TimelineStop","SetPlaybackCurrentFrame,0", "TimelineStop"], False)
                time.sleep(2)
                return 0
            else:
                print("Bitstream change request failed")
        return -1

    def get_application_name(self) -> str:
        return self.settings['application_name']

    def get_nat_net_requested_version(self) -> str:
        return self.settings["nat_net_requested_version"]

    def get_nat_net_version_server(self) -> str:
        return self.settings["nat_net_stream_version_server"]

    def get_server_version(self) -> str:
        return self.settings["server_version"]

    def get_command_port(self) -> int:
        return self.settings["command_port"]



    # Server Communication Functions  #
    # # # # # # # # # # # # # # # # # #

    def connected(self) -> bool:
        return not (
            self.command_socket is None
            or self.data_socket is None
            or self.get_application_name() == "Not Set"
            or self.settings["server_version"] == [0,0,0,0]
        )

    def send_request(self, in_socket: socket.socket, command: int, command_str: str, address: Tuple[Any, ...]):
        if command in [self.NAT_REQUEST_MODELDEF, self.NAT_REQUEST_FRAMEOFDATA, self.NAT_KEEPALIVE]:
            packet_size = 0
        else:
            packet_size = len(command_str) + 1

        data = command.to_bytes(2, byteorder='little') + packet_size.to_bytes(2, byteorder='little')

        if command == self.NAT_CONNECT:
            command_str = [80, 105, 110, 103] + [0]*260 + [4, 1, 0, 0]
            print(f"NAT_CONNECT to Motive with {command_str[-4:]}\n")
            data += bytearray(command_str)
        else:
            data += command_str.encode('utf-8')

        data += b'\0'
        return in_socket.sendto(data, address)

    def send_command( self, command_str: str) -> int:
        #print("Send command %s"%command_str)
        nTries = 3
        ret_val = -1
        for tries in range(nTries):
            ret_val = self.send_request( self.command_socket, self.NAT_REQUEST, command_str,  (self.settings["server_ip"], self.settings["command_port"]) )
            if (ret_val != -1):
                break;
        return ret_val

        #return self.send_request(self.data_socket,    self.NAT_REQUEST, command_str,  (self.server_ip_address, self.command_port) )

    def send_commands(self, tmpCommands: list[str], print_results: bool = True) -> None:
        for sz_command in tmpCommands:
            return_code = self.send_command(sz_command)
            if(print_results):
                print("Command: %s - return_code: %d"% (sz_command, return_code) )

    def send_keep_alive(self,in_socket: socket.socket, server_ip_address: str, server_port: int):
        return self.send_request(in_socket, self.NAT_KEEPALIVE, "", (server_ip_address, server_port))

    def refresh_configuration(self) -> None:
        #query for application configuration
        #print("Request current configuration")
        sz_command = "Bitstream"
        return_code = self.send_command(sz_command)
        time.sleep(0.5)


    # Have You Tried Turning It Off And On Again? #
    # # # # # # # # # # # # # # # # # # # # # # # #
        
    def startup(self) -> bool:
        # Create the data socket
        self.data_socket = self.__create_data_socket( self.settings["data_port"] )
        if self.data_socket is None :
            print( "Could not open data channel" )
            return False

        # Create the command socket
        self.command_socket = self.__create_command_socket()
        if self.command_socket is None :
            print( "Could not open command channel" )
            return False
        self.settings["is_locked"] = True

        self.stop_threads = False
        # Create a separate thread for receiving data packets
        self.data_thread = Thread( target = self.__data_thread_function, args = (self.data_socket, lambda : self.stop_threads, lambda : self.print_level, ))
        self.data_thread.start()

        # Create a separate thread for receiving command packets
        self.command_thread = Thread( target = self.__command_thread_function, args = (self.command_socket, lambda : self.stop_threads, lambda : self.print_level,))
        self.command_thread.start()

        # Required for setup
        # Get NatNet and server versions
        self.send_request(self.command_socket, self.NAT_CONNECT, "",  (self.settings["server_ip"], self.settings["command_port"]) )



        ##Example Commands
        ## Get NatNet and server versions
        self.send_request(self.command_socket, self.NAT_REQUEST_FRAMEOFDATA, "", (self.settings['server_ip'], self.settings['command_port']) )
        ## Request the model definitions
        self.send_request(self.command_socket, self.NAT_REQUEST_MODELDEF, "",  (self.settings['server_ip'], self.settings['command_port']) )
        return True

    def shutdown(self) -> None:
        print("shutdown called")
        self.stop_threads = True
        # closing sockets causes blocking recvfrom to throw
        # an exception and break the loop
        self.command_socket.close()
        self.data_socket.close()
        # attempt to join the threads back.
        self.command_thread.join()
        self.data_thread.join()

