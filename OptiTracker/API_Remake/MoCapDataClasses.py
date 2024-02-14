# TODO: Document

from construct import Struct
from .MoCapDataStructures import MOCAP_DATA_STRUCTS


# 
# Parent class for asset-specific child classes
#
class DataAsset:
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        self.natnet_version = natnet_version      # Unlikely to be implemented
        self._structure = self._get_structure()   # Bespoke Asset-specific Construct Structure
        self._data = None                         # Container for parsed data

        # Parse data if provided during instantiation
        if bytestream is not None:
            self.parse(bytestream)

    # Fetch structure corresponding to asset type
    def _get_structure(self) -> Struct:
        return MOCAP_DATA_STRUCTS[type(self)]
    
    # Returns landing position in datastream after parsing, or 0 prior to parsing
    def offset(self) -> int:
        if self._data is not None:
            return self._data['offset']
        
        # TODO: expected offset might be handy; not sure if possible
        return 0
    
    # Shadows Construct.Struct.parse() method
    def parse(self, bytestream) -> None:
        self._data = self._structure.parse(bytestream)

    # Coerces data parcels into list[dict]; bundling procedure varies by asset type
    #       NOTE: Children drop terminal entries (1 = obj addr, -1 = offset)
    def data(self) -> list[dict]:
        raise NotImplementedError("AssetDataStruct.dump() | Must be implemented by child class.")




#
# Asset type specific data classes
#
    
# Frame number (int)
class DataPrefix(DataAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)     
        
    def data(self) -> list[dict]:
        return [dict(list(self._data.items())[1:-1])]



# N-i MarkerSets, each composed of N-j Markers 
# (set name, xyz position)
class DataMarkerSets(DataAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def data(self) -> list[dict]:
        # TODO: hopefully this can be simplified one day
        # Sets <- Set <- Markers <- Marker; marker(s) are data units.
        return [dict(list(marker.items())[1:]) 
                for marker_set in self._data.marker_sets 
                    for marker in marker_set.markers]



# N-i rigid bodies NOT integral to skeletons, each composed of N-j rigid body(s) 
# (id_self, xyz position, wxyz quaternion, error, tracking validity)
class DataRigidBodies(DataAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def data(self) -> list[dict]:
        # rigid_bodies <- rigid_body; rigid_body(s) are data unit
        return [dict(list(rigid_body.items())[1:]) 
                for rigid_body in self._data.rigid_bodies]



# N-i skeletons, each skeleton composed of N-j rigid bodies, each composed of N-k rigid body(s)
# (id_self, id_parent, xyz position, wxyz quaternion, error, tracking validity)
class DataSkeletons(DataAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def data(self) -> list[dict]:
        # skeletons <- skeleton <- rigid_bodies <- rigid_body; rigid_body(s) are data unit
        # rigid_body(s) here are labeled with skeleton id
        return [dict(list(rigid_body.items())[1:]) 
                for skeleton in self._data.skeletons 
                    for rigid_body_set in skeleton.rigid_body_sets
                        for rigid_body in rigid_body_set.rigid_bodies]



# N-i labeled markers
# (set name, xyz position)
class DataLabeledMarkers(DataAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)
        # NOTE: vesitigial; maybe does something.
        #   if str(type(size)) == "<class 'tuple'>": self.size=size[0]

    def data(self) -> list[dict]:
        return [dict(list(marker.items())[1:]) 
                for marker in self._data.labeled_markers]



# N-i force plates, each composed of N-j channels containing N-k frames
#(id_parent, frame value)
class DataForcePlates(DataAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def data(self) -> list[dict]:
        return [dict(list(frame.items())[1:]) 
                for plate in self._data.force_plates 
                    for channel in plate.channels
                        for frame in channel.frames]



# N-i devices, each composed of N-j channels containing N-k frames
# (id_parent, frame value)
class DataDevices(DataAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def data(self) -> list[dict]:
        return [dict(list(frame.items())[1:]) 
                for device in self._data.devices 
                    for channel in device.channels
                        for frame in channel.frames]



# Frame suffix data
# (too items to list, see MoCapDataStructures.py for details)
class DataSuffix(DataAsset):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def data(self) -> list[dict]:
        return [dict(list(self._data.items())[1:-1])]
    



# Aggregate frame data
class MoCapFrame:
    def __init__(self) -> None:
        
        # Aggregate Frame Data
        self._data = {
            'Prefix': None, 
            'MarkerSets': None, 
            'RigidBodies': None, 
            'Skeletons': None, 
            'LabeledMarkerSets': None, 
            'ForcePlates': None, 
            'Devices': None, 
            'Suffix': None
        }
    
    # Log frame data for a given asset type
    def log(self, asset_type, asset_data) -> None:
        self._data[asset_type] = asset_data

    # Export frame data for desired asset types; also allows for omission
    def export(self, desired = None, omit = None) -> dict[list]:
        if isinstance(desired, str):
            desired = [desired]

        if isinstance(omit, str):
            omit = [omit]

        if desired is not None and omit is not None:
                return {k: v for k, v in self._data.items() if k in desired and k not in omit}
        
        if desired is not None:
            return {k: v for k, v in self._data.items() if k in desired}
        
        if omit is not None:
            return {k: v for k, v in self._data.items() if k not in omit}
            
        return self._data

