# TODO: document

from construct import Struct
from .MoCapDescriptionStructures import MOCAP_DESCRIPTION_STRUCTS

class DescriptionAsset:
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        self.natnet_version = natnet_version  # Determines which structure to use
        self._structure = self._get_structure()   # Asset specific Construct Struct
        self._data = None                   # To store parsed description

        # Parse data if provided during instantiation
        if bytestream is not None:
            self.parse(bytestream)

    # Fetches child-appropriate description Struct(), conditioned on motive version
    def _get_structure(self) -> Struct:
        return MOCAP_DESCRIPTION_STRUCTS[type(self)]
    
    # Returns landing position in datastream after parsing
    def offset(self) -> int:
        # NOTE: Offset pruned out when dump()ing data 
        if self._data is not None:
            return self._data['offset']
        

        # TODO: Expected offset might be handy
        return 0
        
    # Shadows Construct.Struct.parse() method
    def parse(self, bytestream) -> None:
        self._data = self._structure.parse(bytestream)

    # Coerces description parcels into list[dict]; bundling procedure varies by child
    #       NOTE: Children drop terminal entries (1 = obj addr, -1 = offset)
    def dump(self) -> list[dict]:
        raise NotImplementedError("AssetDescriptionStruct.dump() | Must be implemented by child class.")
    
#
# DescriptionAsset Child classes
#
    
# Parses frame number; seems overkill
class DescriptionPrefix(DescriptionAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)     
        
    def dump(self) -> list[dict]:
        return [dict(list(self._data.items())[1:-1])]
    

# Parses N-i MarkerSets, each composed of N-j Markers
class DescriptionMarkerSets(DescriptionAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(marker.items())[1:]) 
                for marker_set in self._data.marker_sets
                    for marker in marker_set.markers]
    

# Parses N-i RigidBodies NOT integral to skeletons, each composed of N-j RigidBody(s)
class DescriptionRigidBodies(DescriptionAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(rb.items())[1:]) 
                for rb in self._data.rigid_bodies]
    
# Parses N-i Skeletons, each composed of N-j RigidBodies, each composed of N-k RigidBody(s)
class DescriptionSkeletons(DescriptionAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(rb.items())[1:]) 
                for skeleton in self._data.skeletons
                for rb_set in skeleton.rigid_body_sets
                for rb in rb_set.rigid_bodies]
    

# NOTE: JFC labeled markers ARE just regular markers...
# Parses N-i LabeledMarkers, each composed of N-j Marker(s)
# class DescriptionLabeledMarkers(DescriptionAsset):
#     def __init__(self, natnet_version = None, bytestream = None) -> None:
#         super().__init__(natnet_version, bytestream)

#     def dump(self) -> list[dict]:
#         return [dict(list(marker.items())[1:]) 
#                 for marker in self._parsed.labeled_markers]
    
# Parses N-i ForcePlates, each plate composed of N-j Channel(s)
class DescriptionForcePlates(DescriptionAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def dump(self) -> list[dict]:
        # TODO: Figuring out tidy way of returning matrices is Future Brett's problem
        pass
        return [dict(list(channel.items())[1:]) 
                for plate in self._data.force_plates
                for channel in plate.channels]
    

# Parses N-i Devices, each device composed of N-j Channel(s)
class DescriptionDevices(DescriptionAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(channel.items())[1:]) 
                for device in self._data.devices
                for channel in device.channels]
    

class DescriptionCameras(DescriptionAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(camera.items())[1:]) 
                for camera in self._data.cameras]
    