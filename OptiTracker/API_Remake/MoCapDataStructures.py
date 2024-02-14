# Necessary for creating structure dicts
from .MoCapDataClasses import DataPrefix, DataMarkerSets, DataRigidBodies, DataSkeletons, DataLabeledMarkers, DataForcePlates, DataDevices, DataSuffix

# Structures created using the work of art that is the Construct library
from construct import Struct, CString, Byte, Default
from construct import IfThenElse, Peek, this, Computed, Tell
from construct import Int32ul, Int16ul, Float32l, Int64ul, Int32ul

# TODO: Prepopulating with default values upon construction might be smart/necessary...

# MoCap Asset Data structures
#       NOTE: Structures for MoCap asset descriptions defined in MoCapDescriptionStructures.py
#
#   Structures first collated into asset-specific dictionaries
#   then collated into a master dictionary indexed by asset type & Motive version
#   Default values are provided, which assume Motive version >= 3.0
#
#   Note: Backwards compatibility (versions < 3.0) yet to be implemented



# Frame prefix (i.e. frame number)
# --------------------------
dataStruct_Prefix = Struct(
    'frame_number' / Int32ul,
    'offset' / Tell
)
# --------------------------


# Mocap marker data, organized as set of sets of markers
# --------------------------

# Individual Markers
dataStruct_Marker = Struct(
    # Dupe id_model from parent struct
    'id_model' / Computed(lambda ctx: ctx._.id_model),
    'pos_x' / Float32l, 'pos_y' / Float32l, 'pos_z' / Float32l
)

# Set of Markers
dataStruct_MarkerSet = Struct(
    'id_model' / Default(CString('utf8'), 'unlabeled'),
    'count' / Int32ul,
    # Preallocate marker-wise data
    'markers' / dataStruct_Marker[this.count]
)

# Set of sets
dataStruct_MarkerSets = Struct(
    'count' / Int32ul,
    'sets' / dataStruct_MarkerSet[this.count],
    'packet_size' / Int32ul,
    'offset' / Tell
)

# --------------------------


# Mocap Skeleton data; essentially a triple-nested list of rigid bodies (ew)
# ------------------------
dataStruct_SkeletonRigidBody = Struct(
    'id_parent' / Computed(lambda ctx: ctx._.id_parent),
    'id_self' / Int32ul,
    'pos_x' / Float32l, 'pos_y' / Float32l, 'pos_z' / Float32l,
    'rot_w' / Float32l, 'rot_x' / Float32l, 'rot_y' / Float32l, 'rot_z' / Float32l,
    'error' / Float32l,
    'tracking_valid' / Int16ul
)

dataStruct_SkeletonRigidBodies = Struct(
    'id_parent' / Computed(lambda ctx: ctx._.id_self),
    'count' / Int32ul,
    'rigid_bodies' / dataStruct_SkeletonRigidBody[this.count]
)

dataStruct_Skeleton = Struct(
    'id_self' / Int32ul,
    'count' / Int32ul,
    'rigid_body_sets' / dataStruct_SkeletonRigidBodies[this.count]
)

dataStruct_Skeletons = Struct(
    'count' / Int32ul,
    'packet_size' / Int32ul,
    'skeletons' / dataStruct_Skeleton[this.count],
    'offset' / Tell
)

# ------------------------


# Mocap data for Rigid Bodies not integral to Skeletons (why)
# --------------------------------------------------
dataStruct_RigidBody = Struct(
    'id_self' / Int32ul,
    'pos_x' / Float32l, 'pos_y' / Float32l, 'pos_z' / Float32l,
    'rot_w' / Float32l, 'rot_x' / Float32l, 'rot_y' / Float32l, 'rot_z' / Float32l,
    'error' / Float32l,
    'tracking_valid' / Int16ul
)

dataStruct_RigidBodies = Struct(
    'count' / Int32ul,
    'packet_size' / Int32ul,
    'rigid_bodies' / dataStruct_RigidBody[this.count],
    'offset' / Tell
)
# --------------------------------------------------


# Mocap data for Labeled Markers (does not contain marker labels)
# ------------------------------
dataStruct_LabeledMarker = Struct(
    'id_self' / Int32ul,
    'pos_x' / Float32l, 'pos_y' / Float32l, 'pos_z' / Float32l,
    'size' / Float32l,
    'param' / Int16ul,
    'residual' / Float32l
)

dataStruct_LabeledMarkerSet = Struct(
    'count' / Int32ul,
    'packet_size' / Int32ul,
    'labeled_markers' / dataStruct_LabeledMarker[this.count],
    'offset' / Tell
)
# ------------------------------


# Mocap data for Force Plates; essentially a triple-nested list of channel-wise frame values (wtvr those are)
# ---------------------------

dataStruct_ForcePlateChannelFrame = Struct(
    'id_parent' / Computed(lambda ctx: ctx._.id_self),
    'value' / Float32l
)

dataStruct_ForcePlateChannel = Struct(
    'id_parent' / Computed(lambda ctx: ctx._.id_self),
    'count' / Int32ul,
    'frames' / dataStruct_ForcePlateChannelFrame[this.count]
)

dataStruct_ForcePlate = Struct(
    'id_self' / Int32ul,
    'count' / Int32ul,
    'channels' / dataStruct_ForcePlateChannel[this.count]
)

dataStruct_ForcePlates = Struct(
    'count' / Int32ul,
    'packet_size' / Int32ul,
    'force_plates' / dataStruct_ForcePlate[this.count],
    'offset' / Tell
)

# ---------------------------


# Structures for Device(s) data
# ----------------------------
dataStruct_DeviceChannelFrame = Struct(
    'id_parent' / Computed(lambda ctx: ctx._.id_self),
    'value' / Float32l
)

dataStruct_DeviceChannel = Struct(
    'id_parent' / Computed(lambda ctx: ctx._.id_self),
    'count' / Int32ul,
    'frames' / dataStruct_DeviceChannelFrame[this.count]
)

dataStruct_Device = Struct(
    'id_self' / Int32ul,
    'count' / Int32ul,
    'channels' / dataStruct_DeviceChannel[this.count]
)

dataStruct_Devices = Struct(
    'count' / Int32ul,
    'packet_size' / Int32ul,
    'devices' / dataStruct_Device[this.count],
    'offset' / Tell
)

# ----------------------------


# Frame Suffix data structures
# ----------------------------

dataStruct_Suffix = Struct(
    'timecode' / Int32ul,
    'timecode_sub' / Int32ul,
    'timestamp' / Int64ul,
    'stamp_camera_mid_exposure' / Int64ul,
    'stamp_data_received' / Int64ul,
    'stamp_transmit' / Int64ul,
    'prec_timestamp_secs' / Int32ul,
    'prec_timestamp_frac_secs' / Int32ul,
    'param' / Int32ul,
    'is_recording' / Byte,
    'tracked_models_changed' / Byte,
    'offset' / Tell
)

# ----------------------------

#
# Structure Dictionary
#
MOCAP_DATA_STRUCTS = {
    DataPrefix: dataStruct_Prefix,
    DataMarkerSets: dataStruct_MarkerSets,
    DataRigidBodies: dataStruct_RigidBodies,
    DataSkeletons: dataStruct_Skeletons,
    DataLabeledMarkers: dataStruct_LabeledMarkerSet,
    DataForcePlates: dataStruct_ForcePlates,
    DataDevices: dataStruct_Devices,
    DataSuffix: dataStruct_Suffix
}
