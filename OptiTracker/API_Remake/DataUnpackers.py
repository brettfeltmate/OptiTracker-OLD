# TODO: Document

from construct import Struct
from .DataStructures import FRAMEDATA_STRUCTS
from typing import Tuple, List, Dict, Union


# # # # # # # # # # # # # # # # # # # # # # #
# Parent class for asset-specific upackers  #
# # # # # # # # # # # # # # # # # # # # # # #

class dataUnpacker:
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        self.natnet_version = NatNetStreamVersion      # Unlikely to be implemented
        self._structure = self._get_structure()   # Bespoke Asset-specific Construct Structure
        self._framedata = None                         # Container for parsed data

        # Parse data if provided during instantiation
        if (bytestream, offset) != (None, None):
            self.parse(bytestream, offset)

    # Fetch structure corresponding to asset type
    def _get_structure(self) -> Struct:
        """
        Returns the Struct corresponding to the type of this instance
        from the FRAMEDATA_STRUCTS mapping.
        """
        return FRAMEDATA_STRUCTS[type(self)]
    
    # Returns landing position in datastream after parsingg
    def relative_offset(self) -> int:
        if self._framedata is not None:
            return self._framedata.relative_offset
        
        return 0
    
    # Shadows Construct.Struct.parse() method
    def parse(self, bytestream: bytes, offset: int, return_data: bool = True) -> Union[Tuple[Dict] | None]:
        self._framedata = self._structure.parse(bytestream[offset:])
        if return_data:
            self.export()

    # Coerces data parcels into list[dict]; bundling procedure varies by asset type
    #       NOTE: Children drop terminal entries (1 = obj addr, -1 = offset)
    def export(self) -> Tuple[int, Tuple[Dict, ...]]:
        raise NotImplementedError("AssetDataStruct.dump() | Must be implemented by child class.")




# # # # # # # # # # # # # #
# Unpackers by asset type #
# # # # # # # # # # # # # # 
    
class prefixData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)     
        
    def export(self) ->Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), [dict(list(self._framedata.items())[1:-1])]


class markerSetData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self) ->Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), [dict(list(marker.items())[1:]) 
                                        for marker in self._framedata.children]
    

class labeledMarkerData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self) ->Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), [dict(list(self._framedata.items())[1:-1])]


class legacyMarkerSetData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self) ->Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), [dict(list(legacyMarker.items())[1:]) 
                                        for legacyMarker in self._framedata.children]


class rigidBodyData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self) ->Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), [dict(list(self._framedata.items())[1:-1])]


class skeletonData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self) ->Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), [dict(list(rigidBody.items())[1:-1]) 
                                        for rigidBody in self._framedata.children]
    
class assetData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self, asset_type) ->Tuple[int, Tuple[Dict, ...]]:
        if (asset_type == "AssetRigidBodies"):
            return self.relative_offset(), [dict(list(assetRigidBody.items())[1:]) 
                                            for assetRigidBody in self._framedata.rigid_bodies]
        elif (asset_type == "AssetMarkers"):
            return self.relative_offset(), [dict(list(assetMarker.items())[1:]) 
                                            for assetMarker in self._framedata.markers]
        else:
            raise ValueError(f"assetData.export() | asset_type must be 'AssetRigidBodies' or 'AssetMarkers'; type supplied: {asset_type}")



class forcePlateData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self) ->Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), [dict(list(frame.items())[1:]) 
                                        for channel in self._framedata.children 
                                        for frame in channel.children]


class deviceData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self) ->Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), [dict(list(frame.items())[1:]) 
                                        for channel in self._framedata.children
                                        for frame in channel.children]


class suffixData(dataUnpacker):
    def __init__(self, bytestream: bytes = None, offset: int = None, NatNetStreamVersion: Tuple[int, ...] = None) -> None:
        super().__init__(bytestream, offset, NatNetStreamVersion)

    def export(self) -> Tuple[int, Tuple[Dict, ...]]:
        return self.relative_offset(), tuple(dict(list(self._framedata.items())[1:-1]))
    


# # # # # # # # # # # # #
# Frame data container  #
# # # # # # # # # # # # #
    
class frameData:
    def __init__(self) -> None:
        
        # Aggregate Frame Data
        self._framedata = {
            'Prefix': (), 
            'MarkerSet': (), 
            'LabeledMarker': (),
            'LegacyMarkerSet': (),
            'RigidBody': (), 
            'Skeleton': (),
            'AssetRigidBody': (),
            'AssetMarker': (),
            'ForcePlate': (), 
            'Devices': (), 
            'Suffix': ()
        }

    # Log frame data for a given asset type
    def __validate_export_arg(self, arg: Union[Tuple[str,...] | str], name: str) -> Tuple[str, ...]:
        if isinstance(arg, str):
            return (arg,)
        elif isinstance(arg, tuple) and all(isinstance(i, str) for i in arg):
            return arg
        else:
            raise TypeError(f"frameData.export() | {name}: expected str or tuple thereof, got {type(arg)}")

    # Export frame data for desired asset types; also allows for omission
    def export(self, include: Union[Tuple[str, ...] | str], exclude: Union[Tuple[str, ...] | str] = None) -> Dict[Tuple[Dict, ...]]:
        include = self.__validate_export_arg(include, "include")

        if exclude is not None:
            exclude = self.__validate_export_arg(exclude, "exclude")
            return {k: v for k, v in self._framedata.items() 
                    if k in include and k not in exclude}
            
        return {k: v for k, v in self._framedata.items() if k in include}

