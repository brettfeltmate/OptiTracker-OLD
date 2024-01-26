from .MoCapDataClasses import FramePrefix, MarkerSets, RigidBodies, Skeletons, LabeledMarkers, ForcePlates, Devices, FrameSuffix, MoCapData

from construct import Struct, CString, Byte, Default
from construct import IfThenElse, Peek, this, Computed, Tell, ctx
from construct import Int32ul, Int16ub, Float32l, Float32b, Int64ul, Int32ul


#
# Data structures
#


# prefix data structures
# ----------------------
prefix_struct_motive_V3 = Struct(
    'frame_number' / Int32ul,
    'offset' / Tell
)

prefix_structs = {
    'default': prefix_struct_motive_V3,
    '3.0': prefix_struct_motive_V3
    # TODO: incorporate older versions
}
# ----------------------



# Marker Set data structures
# --------------------------
marker_struct_motive_V3 = Struct(
    # 'ctx._.' points to enclosing struct
    'model' / Computed(lambda ctx: ctx._.model),
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l
)

marker_set_struct_motive_V3 = Struct(
    'model' / IfThenElse(
        # If byte non-null, grab model label
        Peek(Byte) != 0, 
        CString('utf8'),
        # Default to 'unlabeled' otherwise
        Default(CString('utf8'), 'unlabeled')
    ),
    'marker_count' / Int32ul,
    'markers' / marker_struct_motive_V3[this.marker_count]
)

marker_sets_struct_motive_V3 = Struct(
    'marker_set_count' / Int32ul,
    'marker_sets' / marker_set_struct_motive_V3[this.marker_set_count],
    'offset' / Tell
)

marker_sets_structs = {
    'default': marker_set_struct_motive_V3,
    '3.0': marker_set_struct_motive_V3
}
# --------------------------


# Skeleton data structures
# ------------------------
rigid_body_struct_skeleton_motive_V3 = Struct(
    'skeleton_id' / Computed(lambda ctx: ctx._.skeleton_id),
    'id_num' / Int32ul,
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

rigid_bodies_struct_skeleton_motive_V3 = Struct(
    'skeleton_id' / Computed(lambda ctx: ctx._.skeleton_id),
    'rigid_bodies_count' / Int32ul,
    'rbodies' / rigid_body_struct_skeleton_motive_V3[this.rigid_bodies_count]
)

skeleton_struct_motive_V3 = Struct(
    'skeleton_id' / Int32ul,
    'rigid_body_count' / Int32ul,
    'rigid_bodies_list' / rigid_bodies_struct_skeleton_motive_V3[this.rigid_body_count]
)

skeletons_struct_motive_V3 = Struct(
    'skeleton_count' / Int32ul,
    'skeletons' / skeleton_struct_motive_V3[this.skeleton_count],
    'offset' / Tell
)

skeletons_structs = {
    'default': skeletons_struct_motive_V3,
    '3.0': skeletons_struct_motive_V3
}
# ------------------------


# Non-Skeleton associated Rigid Body data structures
# --------------------------------------------------
rigid_body_struct_motive_V3 = Struct(
    'id_num' / Int32ul,
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

rigid_bodies_struct_motive_V3 = Struct(
    'rigid_body_count' / Int32ul,
    'rigid_bodies' / rigid_body_struct_motive_V3[this.rigid_body_count],
    'offset' / Tell
)

rigid_bodies_structs = {
    'default': rigid_bodies_struct_motive_V3,
    '3.0': rigid_bodies_struct_motive_V3
}
# --------------------------------------------------


# Labeled Marker data structures
# ------------------------------
labeled_marker_struct_motive_V3 = Struct(
    'id_num' / Int32ul,
    'pos_x' / Float32l,
    'pos_y' / Float32l,
    'pos_z' / Float32l,
    'size' / Float32l,
    'param' / Int16ub,
    'residual' / Float32l
)

labeled_markers_struct_motive_V3 = Struct(
    'labeled_marker_count' / Int32ul,
    'labeled_markers' / labeled_marker_struct_motive_V3[this.labeled_marker_count],
    'offset' / Tell
)

labeled_markers_structs = {
    'default': labeled_markers_struct_motive_V3,
    '3.0': labeled_markers_struct_motive_V3
}
# ------------------------------


# Force Plate data structures
# TODO: implement
# ---------------------------
force_plate_channel_struct_motive_V3 = Struct()
force_plates_struct_motive_V3 = Struct()
force_plates_structs = {
    'default': force_plates_struct_motive_V3,
    '3.0': force_plates_struct_motive_V3
}
# ---------------------------


# Device data structures
# TODO: implement
# ----------------------------
device_channel_struct_motive_V3 = Struct()
devices_struct_motive_V3 = Struct()
devices_structs = {
    'default': devices_struct_motive_V3,
    '3.0': devices_struct_motive_V3
}
# ----------------------------


# Frame Suffix data structures
# ----------------------------

frame_suffix_struct_motive_V3 = Struct(
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

frame_suffix_structs = {
    'default': frame_suffix_struct_motive_V3,
    '3.0': frame_suffix_struct_motive_V3
}

# ----------------------------

#
# Structure Dictionary
#
DATA_STRUCT_DICT = {
    FramePrefix: prefix_structs,
    MarkerSets: marker_sets_structs,
    RigidBodies: rigid_bodies_structs,
    Skeletons: skeletons_structs,
    LabeledMarkers: labeled_markers_structs,
    ForcePlates: force_plates_structs,
    Devices: devices_structs,
    FrameSuffix: frame_suffix_structs
}
