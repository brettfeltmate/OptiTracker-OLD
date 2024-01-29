# TODO: Document

from construct import Struct
from .MoCapDataStructures import MOCAP_DATA_STRUCTS


# 
# Parent class for asset-specific child classes
#       NOTE: These classes parse & ship frame-wise data.
#       NOTE: Asset descriptions are defined in MoCapDescriptionClasses.py
class DataAsset:
    def __init__(self, motive_version, bytestream = None) -> None:
        self.motive_version = motive_version  # Determines which structure to use
        self._structure = self._structure()   # Asset specific Construct Struct
        self._parsed = None                   # To store parsed data

        # Parse data if provided during instantiation
        if bytestream is not None:
            self.parse(bytestream)

    # Fetches child-appropriate data Struct(), conditioned on motive version
    def _structure(self) -> Struct:
        struct_dict = MOCAP_DATA_STRUCTS[type(self)]
        return struct_dict.get(self.motive_version, struct_dict['default'])
    
    # TODO: Determining expected offset a priori might be handy; not sure how to do this
    # Returns landing position in datastream after parsing
    def offset(self) -> int:
        # NOTE: Offset pruned out when dump()ing data 
        if self._parsed is not None:
            return self._parsed['offset']
    
    # Shadows Construct.Struct.parse() method
    def parse(self, bytestream) -> None:
        self._parsed = self._structure.parse(bytestream)

    # Coerces data parcels into list[dict]; bundling procedure varies by child
    #       NOTE: Children drop terminal entries (1 = obj addr, -1 = offset)
    def dump(self) -> list[dict]:
        raise NotImplementedError("AssetDataStruct.dump() | Must be implemented by child class.")

#
# AssetData Child classes
#
    
# Parses frame number; seems overkill
class DataPrefix(DataAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)     
        
    def dump(self) -> list[dict]:
        return [dict(list(self._parsed.items())[1:-1])]


# Parses N-i MarkerSets, each composed of N-j Markers
class DataMarkerSets(DataAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        # TODO: hopefully this can be simplified one day
        # Sets <- Set <- Markers <- Marker; marker(s) are data units.
        return [dict(list(marker.items())[1:]) 
                for marker_set in self._parsed.marker_sets 
                for marker in marker_set.markers]


# Parses N-i rigid bodies NOT integral to skeletons, each composed of N-j rigid body(s)
class DataRigidBodies(DataAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        # rigid_bodies <- rigid_body; rigid_body(s) are data unit
        return [dict(list(rb.items())[1:]) 
                for rb in self._parsed.rigid_bodies]


# Parses N-i skeletons, each composed of N-j rigid bodies, each composed of N-k rigid body(s)
class DataSkeletons(DataAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        # skeletons <- skeleton <- rigid_bodies <- rigid_body; rigid_body(s) are data unit
        # rigid_body(s) here are labeled with skeleton id
        return [dict(list(rb.items())[1:]) 
                for skeleton in self._parsed.skeletons 
                for rb_set in skeleton.rigid_body_sets
                for rb in rb_set.rigid_bodies]


# TODO: I suspect I'll find out these are the same as Markers, but more detailed (EXCEPT LABELS???)
# Parses N-i labeled marker sets, each composed of N-j labeled markers
class DataLabeledMarkers(DataAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)
        # NOTE: vesitigial; maybe does something.
        #   if str(type(size)) == "<class 'tuple'>": self.size=size[0]

    def dump(self) -> list[dict]:
        # labeled_markers <- labeled_marker; marker(s) are data unit
        return [dict(list(marker.items())[1:]) 
                for marker in self._parsed.labeled_markers]


# Parses N-i force plates, each plate composed of N-j channels  
class DataForcePlates(DataAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(channel.items())[1:]) 
                for plate in self._parsed.force_plates 
                for channel in plate.channels]

# Parses N-i devices, each device composed of N-j channels
class DataDevices(DataAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(channel.items())[1:]) 
                for device in self._parsed.devices 
                for channel in device.channels]


# Parses frame suffix data (e.g. timecode, timestamp, etc.; see MoCapDataStructures.py)
class DataSuffix(DataAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(self._parsed.items())[1:-1])]
    
# Aggregate frame data
# TODO: Is this even necessary?
class Frame:
    def __init__(self) -> None:
        
        # Aggregate Frame Data
        self._frame = {
            'Prefix': [], 'MarkerSets': [], 'RigidBodies': [], 'Skeletons': [], 'LabeledMarkerSets': [], 'ForcePlates': [], 'Devices': [], 'Suffix': []
        }

