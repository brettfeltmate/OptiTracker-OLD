#Copyright © 2021 Naturalpoint
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


# OptiTrack NatNet direct depacketization sample for Python 3.x
#


# Uses the Python NatNetClient.py library to establish a connection (by creating a NatNetClient),
# and receive data via a NatNet connection and decode it using the NatNetClient library.



from construct import Struct

from .StructureDicts import DATA_STRUCT_DICT

# #
# Asset Data Objs
# #     Internal methods for setting structure using Construct Structs
#       External methods for parsing, exporting, and returning pointer offsets
# # 

# Parent class for all asset data structures
class AssetDataStruct:
    def __init__(self, motive_version, data = None) -> None:
        self.motive_version = motive_version  # Determines which structure to use
        self._structure = self._structure()   # Asset specific Construct Struct
        self._parsed = None                   # To store parsed data

        # Parse data if provided during instantiation
        if data is not None:
            self.parse(data)

    # Returns Construct Struct corresponding to calling child's asset data type
    def _structure(self) -> Struct:
        struct_dict = DATA_STRUCT_DICT[type(self)]
        return struct_dict.get(self.motive_version, struct_dict['default'])
    
    # Returns end position in bytestream after parsing
    def offset(self) -> int:
        if self._parsed is not None:
            return self._parsed['offset']
    
    # Parses data using Construct Struct
    def parse(self, data) -> None:
        self._parsed = self._structure.parse(data)

    # Returns parsed data, implemented by child class
    def dump(self) -> dict:
        raise NotImplementedError("AssetDataStruct.dump() | Must be implemented by child class.")


# Parses frame number; seems unnecessary
class FramePrefix(AssetDataStruct):
    def __init__(self, motive_version, data = None) -> None:
        super().__init__(motive_version, data)     
        
    def dump(self) -> int:
        # TODO: not sure if offset gets returned
        return dict(list(self._parsed.items())[1:-1])


# Parses N MarkerSets, each composed of N Markers
class MarkerSets(AssetDataStruct):
    def __init__(self, motive_version, data = None) -> None:
        super().__init__(motive_version, data)

    def dump(self) -> list:
        # (sorry for the mouthfull; upper levels for parsing, innermost stores data)
        # Each dict a marker, with 1st entry (obj addr) dropped
        return [dict(list(marker.items())[1:]) 
                for marker_set in self._parsed.marker_sets 
                for marker in marker_set.markers]


# Parses rigid bodies not associated with skeletons
class RigidBodies(AssetDataStruct):
    def __init__(self, motive_version, data = None) -> None:
        super().__init__(motive_version, data)

    def dump(self) -> list:
        # Coerce each RB to dict for easy table insertion
        # Drop first entry (obj addr) from each RB
        return [dict(list(rb.items())[1:]) for rb in self._parsed['rigid_bodies']]


# Parses N Skeletons, each composed of N RigidBodies
class Skeletons(AssetDataStruct):
    def __init__(self, motive_version, data = None) -> None:
        super().__init__(motive_version, data)

    def dump(self) -> list:
        # Each dict a rigid body, labeled by skeleton_id, with 1st entry (obj addr) dropped
        return [dict(list(rb.items())[1:]) 
                for skeleton in self._parsed.skeletons 
                for rigid_body in skeleton.rigid_bodies_list
                for rb in rigid_body.rigid_bodies]


# Parses labeled markers
# ... TODO: wtf, what is the point if these don't contain labels??? Fix this.
class LabeledMarkers(AssetDataStruct):
    def __init__(self, motive_version, data = None) -> None:
        super().__init__(motive_version, data)
        # if str(type(size)) == "<class 'tuple'>": self.size=size[0]

    def dump(self) -> list:
        # Each dict a marker, with 1st entry (obj addr) dropped
        return [dict(list(marker.items())[1:]) for marker in self._parsed.labeled_markers]


# TODO: Add support for remaining classes
class ForcePlateChannelData:
    def __init__(self):
        self.frame_list=[]

    def dump(self) -> list:
        pass

class ForcePlate:
    def __init__(self, new_id=0):
        self.id_num = new_id
        self.channel_data_list=[]

    def dump(self) -> list:
        pass

class ForcePlateData:
    def __init__(self):
        self.force_plate_list=[]

    def dump(self) -> list:
        pass

class DeviceChannelData:
    def __init__(self):
        self.frame_list=[]

    def dump(self) -> list:
        pass

class Device:
    def __init__(self, new_id):
        self.id_num=new_id
        self.channel_data_list = []

    def dump(self) -> list:
        pass

class DeviceData:
    def __init__(self):
        self.device_list=[]

    def dump(self) -> list:
        pass

# timestamps and other metadata
class FrameSuffix(AssetDataStruct):
    def __init__(self, motive_version, data = None) -> None:
        super().__init__(motive_version, data)

    def dump(self) -> dict:
        # Each dict a suffix, 1st (obj addr) and last (offset) entries dropped
        return dict(list(self._parsed.items())[1:-1])
    
# Aggregate frame data
# TODO: Is this even necessary?
class Frame:
    def __init__(self) -> None:
        
        # Aggregate Frame Data
        self._frame = {
            'Prefix': [], 'MarkerSets': [], 'RigidBodies': [], 'Skeletons': [], 'LabeledMarkerSets': [], 'ForcePlates': [], 'Devices': [], 'Suffix': []
        }

