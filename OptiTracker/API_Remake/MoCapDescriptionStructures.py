# Necessary for creating structure dicts
from .MoCapDescriptionClasses import DescriptionMarkerSets, DescriptionRigidBodies, DescriptionSkeletons, DescriptionForcePlates, DescriptionDevices, DescriptionCameras

# Structures created using the work of art that is the Construct library
from construct import Struct, CString
from construct import this, Computed, Tell
from construct import Int32ul, Float32l, Int32ul

# MoCap Asset Description structures
#       NOTE: Structures for MoCap asset data defined in MoCapDataStructures.py
#
#   Structures first collated into asset-specific dictionaries
#   then collated into a master dictionary indexed by asset type & Motive version
#   Default values are provided, which assume Motive version >= 3.0
#
#   Note: Backwards compatibility (versions < 3.0) yet to be implemented

# Structures for Marker Set(s) description
# ----------------------
marker_description_v3 = Struct(
    'set_name' / Computed(lambda ctx: ctx._.set_name),
    'marker_name' / CString('utf8')
)

marker_set_description_v3 = Struct(
    'set_name' / CString('utf8'),
    'count' / Int32ul,
    'markers' / marker_description_v3[this.count],
    'offset' / Tell
)

struct_marker_set_description = {
    'default': marker_set_description_v3,
    '3.0': marker_set_description_v3
}
# ----------------------


# Structures for Skeleton(s) description (essentially rigid bodies with extra metadata)
# --------------------------
skeleton_rb_marker_description_v3 = Struct(
    'skeleton_id' / Computed(lambda ctx: ctx._.skeleton_id),
    'offset_x' / Float32l,
    'offset_y' / Float32l,
    'offset_z' / Float32l,
    'active_label' / Int32ul,
    'marker_name' / CString('utf8')
)

skeleton_rb_set_description_v3 = Struct(
    'skeleton_id' / Computed(lambda ctx: ctx._.skeleton_id),
    'rb_name' / CString('utf8'),
    'id_self' / Int32ul,
    'id_parent' / Int32ul,
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l,
    'rb_count' / Int32ul,
    'rb_markers' / skeleton_rb_marker_description_v3[this.rb_count]
)

skeleton_description_v3 = Struct(
    'skeleton_name' / CString('utf8'),
    'skeleton_id' / Int32ul,
    'rb_set_count' / Int32ul,
    'rb_sets' / skeleton_rb_set_description_v3[this.rb_set_count],
    'offset' / Tell
)

struct_skeleton_description = {
    'default': skeleton_description_v3,
    '3.0': skeleton_description_v3
}

# --------------------------

# Structures for Rigid Body(ies), NOT integral to skeletons, description
# --------------------------

rb_marker_description_v3 = Struct(
    'pos_offset' / Float32l[3],
    'active_label' / Int32ul,
    'marker_name' / CString('utf8')
)

rb_description_v3 = Struct(
    'rb_name' / CString('utf8'),
    'id_self' / Int32ul,
    'id_parent' / Int32ul,
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l,
    'rb_count' / Int32ul,
    'rb_markers' / rb_marker_description_v3[this.rb_count],
    'offset' / Tell
)

struct_rb_description = {
    'default': rb_description_v3,
    '3.0': rb_description_v3
}
# --------------------------


# Structures for Labeled Marker(s) description
# --------------------------
# TODO: omg... they're just regular markers with labels... but don't include the labels...
# TODO: Refactor (non-rigid-body) markers into a shared structure/class
# --------------------------

# Structures for Force Plate(s) description
# --------------------------
fplate_corner_matrix_description_v3 = Struct(
    'row_1_col_1' / Float32l, 'row_1_col_2' / Float32l, 'row_1_col_3' / Float32l,
    'row_2_col_1' / Float32l, 'row_2_col_2' / Float32l, 'row_2_col_3' / Float32l,
    'row_3_col_1' / Float32l, 'row_3_col_2' / Float32l, 'row_3_col_3' / Float32l,
    'row_4_col_1' / Float32l, 'row_4_col_2' / Float32l, 'row_4_col_3' / Float32l
)

fplate_calibration_matrix_description_v3 = Struct(
    'row_1_col_1' / Float32l, 'row_1_col_2' / Float32l, 'row_1_col_3' / Float32l, 
    'row_1_col_4' / Float32l, 'row_1_col_5' / Float32l, 'row_1_col_6' / Float32l, 
    'row_1_col_7' / Float32l, 'row_1_col_8' / Float32l, 'row_1_col_9' / Float32l, 
    'row_1_col_10' / Float32l, 'row_1_col_11' / Float32l, 'row_1_col_12' / Float32l, 
    'row_2_col_1' / Float32l, 'row_2_col_2' / Float32l, 'row_2_col_3' / Float32l, 
    'row_2_col_4' / Float32l, 'row_2_col_5' / Float32l, 'row_2_col_6' / Float32l, 
    'row_2_col_7' / Float32l, 'row_2_col_8' / Float32l, 'row_2_col_9' / Float32l, 
    'row_2_col_10' / Float32l, 'row_2_col_11' / Float32l, 'row_2_col_12' / Float32l, 
    'row_3_col_1' / Float32l, 'row_3_col_2' / Float32l, 'row_3_col_3' / Float32l, 
    'row_3_col_4' / Float32l, 'row_3_col_5' / Float32l, 'row_3_col_6' / Float32l, 
    'row_3_col_7' / Float32l, 'row_3_col_8' / Float32l, 'row_3_col_9' / Float32l, 
    'row_3_col_10' / Float32l, 'row_3_col_11' / Float32l, 'row_3_col_12' / Float32l, 
    'row_4_col_1' / Float32l, 'row_4_col_2' / Float32l, 'row_4_col_3' / Float32l, 
    'row_4_col_4' / Float32l, 'row_4_col_5' / Float32l, 'row_4_col_6' / Float32l, 
    'row_4_col_7' / Float32l, 'row_4_col_8' / Float32l, 'row_4_col_9' / Float32l, 
    'row_4_col_10' / Float32l, 'row_4_col_11' / Float32l, 'row_4_col_12' / Float32l, 
    'row_5_col_1' / Float32l, 'row_5_col_2' / Float32l, 'row_5_col_3' / Float32l, 
    'row_5_col_4' / Float32l, 'row_5_col_5' / Float32l, 'row_5_col_6' / Float32l, 
    'row_5_col_7' / Float32l, 'row_5_col_8' / Float32l, 'row_5_col_9' / Float32l, 
    'row_5_col_10' / Float32l, 'row_5_col_11' / Float32l, 'row_5_col_12' / Float32l, 
    'row_6_col_1' / Float32l, 'row_6_col_2' / Float32l, 'row_6_col_3' / Float32l, 
    'row_6_col_4' / Float32l, 'row_6_col_5' / Float32l, 'row_6_col_6' / Float32l, 
    'row_6_col_7' / Float32l, 'row_6_col_8' / Float32l, 'row_6_col_9' / Float32l, 
    'row_6_col_10' / Float32l, 'row_6_col_11' / Float32l, 'row_6_col_12' / Float32l, 
    'row_7_col_1' / Float32l, 'row_7_col_2' / Float32l, 'row_7_col_3' / Float32l, 
    'row_7_col_4' / Float32l, 'row_7_col_5' / Float32l, 'row_7_col_6' / Float32l, 
    'row_7_col_7' / Float32l, 'row_7_col_8' / Float32l, 'row_7_col_9' / Float32l, 
    'row_7_col_10' / Float32l, 'row_7_col_11' / Float32l, 'row_7_col_12' / Float32l, 
    'row_8_col_1' / Float32l, 'row_8_col_2' / Float32l, 'row_8_col_3' / Float32l, 
    'row_8_col_4' / Float32l, 'row_8_col_5' / Float32l, 'row_8_col_6' / Float32l, 
    'row_8_col_7' / Float32l, 'row_8_col_8' / Float32l, 'row_8_col_9' / Float32l, 
    'row_8_col_10' / Float32l, 'row_8_col_11' / Float32l, 'row_8_col_12' / Float32l, 
    'row_9_col_1' / Float32l, 'row_9_col_2' / Float32l, 'row_9_col_3' / Float32l, 
    'row_9_col_4' / Float32l, 'row_9_col_5' / Float32l, 'row_9_col_6' / Float32l, 
    'row_9_col_7' / Float32l, 'row_9_col_8' / Float32l, 'row_9_col_9' / Float32l, 
    'row_9_col_10' / Float32l, 'row_9_col_11' / Float32l, 'row_9_col_12' / Float32l, 
    'row_10_col_1' / Float32l, 'row_10_col_2' / Float32l, 'row_10_col_3' / Float32l, 
    'row_10_col_4' / Float32l, 'row_10_col_5' / Float32l, 'row_10_col_6' / Float32l, 
    'row_10_col_7' / Float32l, 'row_10_col_8' / Float32l, 'row_10_col_9' / Float32l, 
    'row_10_col_10' / Float32l, 'row_10_col_11' / Float32l, 'row_10_col_12' / Float32l, 
    'row_11_col_1' / Float32l, 'row_11_col_2' / Float32l, 'row_11_col_3' / Float32l, 
    'row_11_col_4' / Float32l, 'row_11_col_5' / Float32l, 'row_11_col_6' / Float32l, 
    'row_11_col_7' / Float32l, 'row_11_col_8' / Float32l, 'row_11_col_9' / Float32l, 
    'row_11_col_10' / Float32l, 'row_11_col_11' / Float32l, 'row_11_col_12' / Float32l, 
    'row_12_col_1' / Float32l, 'row_12_col_2' / Float32l, 'row_12_col_3' / Float32l, 
    'row_12_col_4' / Float32l, 'row_12_col_5' / Float32l, 'row_12_col_6' / Float32l, 
    'row_12_col_7' / Float32l, 'row_12_col_8' / Float32l, 'row_12_col_9' / Float32l, 
    'row_12_col_10' / Float32l, 'row_12_col_11' / Float32l, 'row_12_col_12' / Float32l
)
    


fplate_channel_description_v3 = Struct(
    'channel_id'/ Computed(lambda ctx: ctx._.id_self),
    'channel_name' / CString('utf8')
)

fplate_description_v3 = Struct(
    'id_self' / Int32ul,
    'serial_no' / CString('utf8'),
    'width' / Float32l,
    'length' / Float32l,
    'origin_x' / Float32l,
    'origin_y' / Float32l,
    'origin_z' / Float32l,
    'cal_matrix' / fplate_calibration_matrix_description_v3,
    'corner_matrix' / fplate_corner_matrix_description_v3,
    'plate_type' / Int32ul,
    'channel_data_type' / Int32ul,
    'channel_count' / Int32ul,
    'channels' / fplate_channel_description_v3[this.channel_count],
    'offset' / Tell
)

struct_fplate_description = {
    'default': fplate_description_v3,
    '3.0': fplate_description_v3
}

# --------------------------

# Structures for Device(s) description
# --------------------------
device_channel_description_v3 = Struct(
    'channel_id' / Computed(lambda ctx: ctx._.id_self),
    'channel_name' / CString('utf8')
)

device_description_v3 = Struct(
    'id_self' / Int32ul,
    'device_name' / CString('utf8'),
    'serial_no' / CString('utf8'),
    'device_type' / Int32ul,
    'channel_data_type' / Int32ul,
    'channel_count' / Int32ul,
    'channels' / device_channel_description_v3[this.channel_count],
    'offset' / Tell
)

struct_device_description = {
    'default': device_description_v3,
    '3.0': device_description_v3
}

# --------------------------

# Structures for camera description
# --------------------------
camera_description_v3 = Struct(
    'camera_name' / CString('utf8'),
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l,
    'rot_w' / Float32l,
    'rot_x' / Float32l,
    'rot_y' / Float32l,
    'rot_z' / Float32l,
    'offset' / Tell
)

struct_camera_description = {
    'default': camera_description_v3,
    '3.0': camera_description_v3
}
# --------------------------

#
# Structures dictionary for MoCap asset descriptions
#

MOCAP_DESCRIPTION_STRUCTS = {
    DescriptionMarkerSets: struct_marker_set_description,
    DescriptionSkeletons: struct_skeleton_description,
    DescriptionRigidBodies: struct_rb_description,
    DescriptionForcePlates: struct_fplate_description,
    DescriptionDevices: struct_device_description,
    DescriptionCameras: camera_description_v3,
}









