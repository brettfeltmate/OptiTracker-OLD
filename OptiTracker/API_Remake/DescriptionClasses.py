# TODO: document

from construct import Struct
from .DescriptionStructures import DESCRIPTION_STRUCTS

class descriptionUnpacker:
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        self.natnet_version = natnet_version        # Determines which structure to use
        self._structure = self._get_structure()     # Asset specific Construct Struct
        self._description = None                           # To store parsed description

        # Parse data if provided during instantiation
        if bytestream is not None:
            self.unpack(bytestream)

    # Fetches child-appropriate description Struct(), conditioned on motive version
    def _get_structure(self) -> Struct:
        try:
            return DESCRIPTION_STRUCTS[type(self)]
        except KeyError:
            raise ValueError(f"MoCapAsset._get_structure() | Unrecognized asset type.\n\tExpected: {DESCRIPTION_STRUCTS.keys()}\n\tSupplied: {type(self)}")
    
    # Returns landing position in datastream after parsing
    def relative_offset(self) -> int:
        # NOTE: Offset pruned out when dump()ing data 
        if self._description is not None:
            return self._description['relative_offset']
        

        # TODO: Expected offset might be handy
        return 0
        
    # Shadows Construct.Struct.parse() method
    def unpack(self, bytestream, return_data = True) -> list[dict] | None:
        self._description = self._structure.parse(bytestream)

        if return_data:
            self.export()

    # Coerces description parcels into list[dict]; bundling procedure varies by child
    #       NOTE: Children drop terminal entries (1 = obj addr, -1 = offset)
    def export(self) -> list[dict]:
        raise NotImplementedError("AssetDescriptionStruct.dump() | Must be implemented by child class.")
    
#
# DescriptionAsset Child classes
#
    
    
# Parses N-i MarkerSets, each composed of N-j Markers
class markerSetDescription(descriptionUnpacker):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return [dict(list(marker.items())[1:]) 
                for marker in self._description.children]
    

# Parses N-i RigidBodies NOT integral to skeletons, each composed of N-j RigidBody(s)
class rigidBodyDescription(descriptionUnpacker):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return [dict(list(rigidBodyMarker.items())[1:]) 
                for rigidBodyMarker in self._description.children]
    
# Parses N-i Skeletons, each composed of N-j RigidBodies, each composed of N-k RigidBody(s)
class skeletonDescription(descriptionUnpacker):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return [dict(list(rigidBodyMarker.items())[1:]) 
                for rigidBody in self._description.children
                for rigidBodyMarker in rigidBody.children]
    

class assetDescription(descriptionUnpacker):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self, asset_type) -> list[dict]:
        if (asset_type == "RigidBodies"):
            return [dict(list(rigidBodyMarker.items())[1:])
                    for rigidBody in self._description.rigid_body_children
                        for rigidBodyMarker in rigidBody.children]
        elif (asset_type == "Markers"):
            return [dict(list(marker.items())[1:])
                    for marker in self._description.marker_children]
        else:
            raise ValueError(f"assetDescription.export() | asset_type must be 'RigidBodies' or 'Markers'; type supplied: {asset_type}")
    
# Parses N-i ForcePlates, each plate composed of N-j Channel(s)
class forcePlateDescription(descriptionUnpacker):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        # TODO: Figuring out tidy way of returning matrices is Future Brett's problem
        pass
        return [dict(list(channel.items())[1:]) 
                for plate in self._description.children
                for channel in plate.children]
    

# Parses N-i Devices, each device composed of N-j Channel(s)
class deviceDescription(descriptionUnpacker):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return [dict(list(channel.items())[1:]) 
                for device in self._description.children
                for channel in device.children]
    

class cameraDescription(descriptionUnpacker):
    def __init__(self, natnet_version = None, bytestream = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return [dict(list(camera.items())[1:]) 
                for camera in self._description.children]
    
    # Aggregate frame data
class Descriptions:
    def __init__(self) -> None:
        
        # Aggregate Frame Data
        self._descriptions = {
            'MarkerSet': None, 
            'RigidBody': None, 
            'Skeleton': None,
            'AssetRigidBody': None,
            'AssetMarker': None,
            'ForcePlate': None, 
            'Device': None, 
            'Camera': None
        }
    
    # Log frame data for a given asset type
    def log(self, asset_type, asset_description) -> None:
        self._descriptions[asset_type] = asset_description

    # Export frame data for desired asset types; also allows for omission
    def export(self, include = None, exclude = None) -> dict[list[dict]]:
        # Check if include or exclude are anything but str or list
        if not (isinstance(include, str) or isinstance(include, list)):
            raise TypeError("include must be str or list")
        
        if not (isinstance(exclude, str) or isinstance(exclude, list)):
            raise TypeError("exclude must be str or list")

        if isinstance(include, str):
            include = [include]

        if isinstance(exclude, str):
            exclude = [exclude]

        if include is not None and exclude is not None:
                return {k: v for k, v in self._descriptions.items() if k in include and k not in exclude}
        
        if include is not None:
            return {k: v for k, v in self._descriptions.items() if k in include}
        
        if exclude is not None:
            return {k: v for k, v in self._descriptions.items() if k not in exclude}
            
        return self._descriptions
    