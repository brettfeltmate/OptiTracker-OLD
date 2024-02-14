# Necessary for creating structure dicts
from .MoCapDataClasses import DataPrefix, DataMarkerSets, DataRigidBodies, DataSkeletons, DataLabeledMarkers, DataForcePlates, DataDevices, DataSuffix

# Structures created using the work of art that is the Construct library
from construct import Struct, CString, Byte, Default
from construct import IfThenElse, Peek, this, Computed, Tell
from construct import Int32ul, Int16ub, Float32l, Int64ul, Int32ul

# TODO: Prepopulating with default values upon construction might be smart/necessary...

# MoCap Asset Data structures
#       NOTE: Structures for MoCap asset descriptions defined in MoCapDescriptionStructures.py
#
#   Structures first collated into asset-specific dictionaries
#   then collated into a master dictionary indexed by asset type & Motive version
#   Default values are provided, which assume Motive version >= 3.0
#
#   Note: Backwards compatibility (versions < 3.0) yet to be implemented


# Structures for Frame Prefix data
# ----------------------
prefix_data_v3 = Struct(
    'frame_number' / Int32ul,
    # Tell returns landing point in datastream after parsing
    'offset' / Tell
)

# NOTE: asset-specific dictionaries allow for version-specific structures (once implemented)
struct_prefix_data = {
    'default': prefix_data_v3,
    '3.0': prefix_data_v3
}
# ----------------------



# Structures for Marker Set(s) data
# --------------------------
marker_data_v3 = Struct(
    # 'ctx._.' points to enclosing struct
    'id_model' / Computed(lambda ctx: ctx._.id_model),
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l
)

# TODO: test Peek() with dummy data; not sure if this works like I think it does
marker_set_data_v3 = Struct(
    'id_model' / IfThenElse(
        # Model labels terminate with null byte; if byte non-null, grab model label
        Peek(Byte) != 0, 
        CString('utf8'),
        # Otherwise, default to 'unlabeled'
        Default(CString('utf8'), 'unlabeled')
    ),
    'count' / Int32ul,
    # [] operator constructs a list (of len count) of given struct
    'markers' / marker_data_v3[this.count]
)

marker_sets_data_v3 = Struct(
    'count' / Int32ul,
    'sets' / marker_set_data_v3[this.count],
    'offset' / Tell
)

struct_marker_sets_data = {
    'default': marker_set_data_v3,
    '3.0': marker_set_data_v3
}
# --------------------------


# Structures for Skeleton(s) data (essentially rigid bodies with extra metadata)
# ------------------------
skeleton_rb_marker_data_v3 = Struct(
    'id_skeleton' / Computed(lambda ctx: ctx._.id_skeleton),
    'id_self' / Int32ul,
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l,
    'rot_w' / Float32l,
    'rot_x' / Float32l,
    'rot_y' / Float32l,
    'rot_z' / Float32l,
    'error' / Float32l,
    'tracking_valid' / Int16ub
)

skeleton_rb_set_data_v3 = Struct(
    'id_skeleton' / Computed(lambda ctx: ctx._.id_skeleton),
    'count' / Int32ul,
    'rigid_bodies' / skeleton_rb_marker_data_v3[this.count]
)

skeleton_data_v3 = Struct(
    'id_skeleton' / Int32ul,
    'count' / Int32ul,
    'rigid_body_sets' / skeleton_rb_set_data_v3[this.count]
)

skeleton_set_data_v3 = Struct(
    'count' / Int32ul,
    'skeletons' / skeleton_data_v3[this.count],
    'offset' / Tell
)

struct_skeleton_sets_data = {
    'default': skeleton_set_data_v3,
    '3.0': skeleton_set_data_v3
}
# ------------------------


# Structures for (non-skeleton associated) Rigid Body(s) data
# --------------------------------------------------
rb_marker_data_v3 = Struct(
    'id_self' / Int32ul,
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l,
    'rot_w' / Float32l,
    'rot_x' / Float32l,
    'rot_y' / Float32l,
    'rot_z' / Float32l,
    'error' / Float32l,
    'tracking_valid' / Int16ub
)

rb_set_data_v3 = Struct(
    'count' / Int32ul,
    'rigid_bodies' / rb_marker_data_v3[this.count],
    'offset' / Tell
)

struct_rigid_body_sets_data = {
    'default': rb_set_data_v3,
    '3.0': rb_set_data_v3
}
# --------------------------------------------------


# Structures for Labeled Marker(s) data
# ------------------------------
lbl_marker_data_v3 = Struct(
    'id_self' / Int32ul,
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l,
    'size' / Float32l,
    'param' / Int16ub,
    'residual' / Float32l
)

lbl_marker_set_data_v3 = Struct(
    'count' / Int32ul,
    'labeled_markers' / lbl_marker_data_v3[this.count],
    'offset' / Tell
)

struct_lbl_marker_sets_data = {
    'default': lbl_marker_set_data_v3,
    '3.0': lbl_marker_set_data_v3
}
# ------------------------------


# Structures for Force Plate(s) data
# ---------------------------
fplate_channel_data_v3 = Struct(
    'id_force_plate' / Computed(lambda ctx: ctx._.id_self),
    'value' / Float32l[this.count]
)

fplate_data_v3 = Struct(
    'id_self' / Int32ul,
    'count' / Int32ul,
    'channels' / fplate_channel_data_v3[this.count]
)

fplates_data_v3 = Struct(
    'count' / Int32ul,
    'force_plates' / fplate_data_v3[this.count],
    'offset' / Tell
)

struct_force_plates_data = {
    'default': fplates_data_v3,
    '3.0': fplates_data_v3
}
# ---------------------------


# Structures for Device(s) data
# ----------------------------
device_channel_data_v3 = Struct(
    'id_device' / Computed(lambda ctx: ctx._.id_self),
    'float_value' / Float32l,
    'int_value' / Int32ul
)

device_data_v3 = Struct(
    'id_self' / Int32ul,
    'count' / Int32ul,
    'channels' / device_channel_data_v3[this.count]
)

devices_data_v3 = Struct(
    'count' / Int32ul,
    'devices' / device_data_v3[this.count],
    'offset' / Tell
)

struct_devices_data = {
    'default': devices_data_v3,
    '3.0': devices_data_v3
}
# ----------------------------


# Frame Suffix data structures
# ----------------------------

suffix_data_v3 = Struct(
    'timecode' / Int32ul,
    'timecode_sub' / Int32ul,
    'timestamp' / Float32l,
    'stamp_camera_mid_exposure' / Int64ul,
    'stamp_data_received' / Int64ul,
    'stamp_transmit' / Int64ul,
    'param' / Int32ul,
    'is_recording' / Byte,
    'tracked_models_changed' / Byte,
    'offset' / Tell
)

struct_suffix_data = {
    'default': suffix_data_v3,
    '3.0': suffix_data_v3
}

# ----------------------------

#
# Structure Dictionary
#
MOCAP_DATA_STRUCTS = {
    DataPrefix: struct_prefix_data,
    DataMarkerSets: struct_marker_sets_data,
    DataRigidBodies: struct_rigid_body_sets_data,
    DataSkeletons: struct_skeleton_sets_data,
    DataLabeledMarkers: struct_lbl_marker_sets_data,
    DataForcePlates: struct_force_plates_data,
    DataDevices: struct_devices_data,
    DataSuffix: struct_suffix_data
}
