# TODO: Document

from construct import Struct
from .DataStructures import FRAMEDATA_STRUCTS


# # # # # # # # # # # # # # # # # # # # # # #
# Parent class for asset-specific upackers  #
# # # # # # # # # # # # # # # # # # # # # # #

class dataUnpacker:
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        self.natnet_version = natnet_version      # Unlikely to be implemented
        self._structure = self._get_structure()   # Bespoke Asset-specific Construct Structure
        self._framedata = None                         # Container for parsed data

        # Parse data if provided during instantiation
        if bytestream is not None & offset is not None:
            self.parse(bytestream, offset)

    # Fetch structure corresponding to asset type
    def _get_structure(self) -> Struct:
        return FRAMEDATA_STRUCTS[type(self)]
    
    # Returns landing position in datastream after parsingg
    def relative_offset(self) -> int:
        if self._framedata is not None:
            return self._framedata.relative_offset
        
        return 0
    
    # Shadows Construct.Struct.parse() method
    def parse(self, bytestream: bytes, offset: int, return_data: bool = True) -> list[dict] | None:
        self._framedata = self._structure.parse(bytestream[offset:])
        if return_data:
            self.export()

    # Coerces data parcels into list[dict]; bundling procedure varies by asset type
    #       NOTE: Children drop terminal entries (1 = obj addr, -1 = offset)
    def export(self) -> list[dict]:
        raise NotImplementedError("AssetDataStruct.dump() | Must be implemented by child class.")




# # # # # # # # # # # # # #
# Unpackers by asset type #
# # # # # # # # # # # # # # 
    
class prefixData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)     
        
    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(self._framedata.items())[1:-1])]


class markerSetData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(marker.items())[1:]) 
                                        for marker in self._framedata.children]
    

class labeledMarkerData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(self._framedata.items())[1:-1])]


class legacyMarkerSetData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(legacyMarker.items())[1:]) 
                                        for legacyMarker in self._framedata.children]


class rigidBodyData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(self._framedata.items())[1:-1])]


class skeletonData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(rigidBody.items())[1:-1]) 
                                        for rigidBody in self._framedata.children]
    
class assetData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self, asset_type) -> list[dict]:
        if (asset_type == "AssetRigidBodies"):
            return self.relative_offset(), [dict(list(assetRigidBody.items())[1:]) 
                                            for assetRigidBody in self._framedata.rigid_bodies]
        elif (asset_type == "AssetMarkers"):
            return self.relative_offset(), [dict(list(assetMarker.items())[1:]) 
                                            for assetMarker in self._framedata.markers]
        else:
            raise ValueError(f"assetData.export() | asset_type must be 'AssetRigidBodies' or 'AssetMarkers'; type supplied: {asset_type}")



class forcePlateData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(frame.items())[1:]) 
                                        for channel in self._framedata.children 
                                        for frame in channel.children]


class deviceData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(frame.items())[1:]) 
                                        for channel in self._framedata.children
                                        for frame in channel.children]


class suffixData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, natnet_version: str = None) -> None:
        super().__init__(natnet_version, bytestream)

    def export(self) -> list[dict]:
        return self.relative_offset(), [dict(list(self._framedata.items())[1:-1])]
    


# # # # # # # # # # # # #
# Frame data container  #
# # # # # # # # # # # # #
    
class frameData:
    def __init__(self) -> None:
        
        # Aggregate Frame Data
        self._framedata = {
            'Prefix': None, 
            'MarkerSet': None, 
            'LabeledMarker': None,
            'LegacyMarkerSet': None,
            'RigidBody': None, 
            'Skeleton': None,
            'AssetRigidBody': None,
            'AssetMarker': None,
            'ForcePlate': None, 
            'Devices': None, 
            'Suffix': None
        }
    
    # Log frame data for a given asset type
    def log(self, asset_type: str, asset_data: list[dict]) -> None:
        self._framedata[asset_type] = asset_data

    # Export frame data for desired asset types; also allows for omission
    def export(self, include: list = None, exclude: list = None) -> dict[list]:
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
                return {k: v for k, v in self._framedata.items() if k in include and k not in exclude}
        
        if include is not None:
            return {k: v for k, v in self._framedata.items() if k in include}
        
        if exclude is not None:
            return {k: v for k, v in self._framedata.items() if k not in exclude}
            
        return self._framedata

