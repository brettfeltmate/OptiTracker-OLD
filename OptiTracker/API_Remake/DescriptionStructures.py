# Structures created using the work of art that is the Construct library
from construct import Struct, CString, Optional, this, Computed, Tell, Probe
from construct import Int32ul, Float32l, Int32ul

# MoCap Asset Description structures
#       NOTE: Structures for MoCap asset data defined in MoCapDataStructures.py
#
#   Structures first collated into asset-specific dictionaries
#   then collated into a master dictionary indexed by asset type & Motive version
#   Default values are provided, which assume Motive version >= 3.0
#
#   Note: Backwards compatibility (versions < 3.0) yet to be implemented



# Unit-level structure for MarkerSet Markers
# ----------------------
descStruct_Marker = Struct(
    'asset_type' /          Computed("Marker"),
    'asset_name' /          CString('utf8'),
    'parent_name' /         Computed(lambda ctx: ctx._.asset_name)
)
# ----------------------


# Structures for MarkerSet description
# ----------------------
descStruct_MarkerSet = Struct(
    'asset_type' /      Computed("MarkerSet"),
    'asset_name' /      CString('utf8'),
    'packet_size' /     Int32ul,
    'child_count' /     Int32ul,
    'children' /        descStruct_Marker[this.child_count],
    'relative_offset' / Tell
)
# ----------------------


# Structures for Rigid Body descriptions, belonging to skeletons or otherwise
# --------------------------

descStruct_RigidBodyMarker = Struct(
    'asset_type' /      Computed("RigidBodyMarker"),
    'asset_ID' /        Computed(lambda ctx: ctx._.asset_ID),
    'parent_ID' /       Computed(lambda ctx: ctx._.parent_ID),
    # 'parent_type' /     Computed(lambda ctx: ctx._.parent_type),
    # 'parent_name' /     Computed(lambda ctx: ctx._.parent_name),
    'pos_x' /           Computed(lambda ctx: ctx._.pos_x),
    'pos_y' /           Computed(lambda ctx: ctx._.pos_y),
    'pos_z' /           Computed(lambda ctx: ctx._.pos_z),
    Probe(lookahead=12),
    'offset_x' /        Float32l,
    'offset_y' /        Float32l,
    'offset_z' /        Float32l,
    'active_label' /    Int32ul,
    'asset_name' /      CString('utf8'),
    Probe()
)

descStruct_RigidBody = Struct(
    Probe(lookahead=12),
    'asset_type' /      Computed("RigidBody"),
    'asset_name' /      CString('utf8'),
    'asset_ID' /        Int32ul,
    'parent_ID' /       Int32ul,
    # parent_name = None when not nested within parent structure
    # 'parent_type' /     Optional(Computed(lambda ctx: ctx._.asset_type)),
    # 'parent_name' /     Optional(Computed(lambda ctx: ctx._.asset_name)),
    'pos_x' /           Float32l, 
    'pos_y' /           Float32l, 
    'pos_z' /           Float32l,
    'child_count' /     Int32ul,
    Probe(),
    'children' /        descStruct_RigidBodyMarker[this.child_count],
    'relative_offset'/  Tell,
    Probe()
)

descStruct_Skeleton = Struct(
    'asset_type' /      Computed("Skeleton"),
    'asset_name' /      CString('utf8'),
    'asset_ID' /        Int32ul,
    'child_count' /     Int32ul,
    'children' /        descStruct_RigidBody[this.child_count],
    'relative_offset' / Tell,
    Probe()
)
# --------------------------

# Structures for Asset descriptions
# --------------------------

descStruct_Asset = Struct(
    'asset_name' /          CString('utf8'),
    'asset_type' /          Int32ul,
    'asset_ID' /            Int32ul,
    'rigid_body_count' /    Int32ul,
    'rigid_body_children' / descStruct_RigidBody[this.rigid_body_count],
    'marker_count' /        Int32ul,
    'marker_children' /     descStruct_Marker[this.marker_count],
    'relative_offset' /     Tell,
    Probe()
)



# Structures for Force Plate(s) description
# --------------------------
descStruct_ForcePlate_Corners_Matrix = Struct(
    'asset_type' / Computed('ForcePlateCornersMatrix'),
    'row_1_col_1' / Float32l, 'row_1_col_2' / Float32l, 'row_1_col_3' / Float32l,
    'row_2_col_1' / Float32l, 'row_2_col_2' / Float32l, 'row_2_col_3' / Float32l,
    'row_3_col_1' / Float32l, 'row_3_col_2' / Float32l, 'row_3_col_3' / Float32l,
    'row_4_col_1' / Float32l, 'row_4_col_2' / Float32l, 'row_4_col_3' / Float32l
)

descStruct_ForcePlate_Calibration_Matrix = Struct(
    'asset_type' / Computed("ForcePlateCalibrationMatrix"),
    'row_1_col_1'  /  Float32l, 'row_1_col_2'  /  Float32l, 'row_1_col_3'  /  Float32l, 
    'row_1_col_4'  /  Float32l, 'row_1_col_5'  /  Float32l, 'row_1_col_6'  /  Float32l, 
    'row_1_col_7'  /  Float32l, 'row_1_col_8'  /  Float32l, 'row_1_col_9'  /  Float32l, 
    'row_1_col_10' /  Float32l, 'row_1_col_11' /  Float32l, 'row_1_col_12' /  Float32l, 
    'row_2_col_1'  /  Float32l, 'row_2_col_2'  /  Float32l, 'row_2_col_3'  /  Float32l, 
    'row_2_col_4'  /  Float32l, 'row_2_col_5'  /  Float32l, 'row_2_col_6'  /  Float32l, 
    'row_2_col_7'  /  Float32l, 'row_2_col_8'  /  Float32l, 'row_2_col_9'  /  Float32l, 
    'row_2_col_10' /  Float32l, 'row_2_col_11' /  Float32l, 'row_2_col_12' /  Float32l, 
    'row_3_col_1'  /  Float32l, 'row_3_col_2'  /  Float32l, 'row_3_col_3'  /  Float32l, 
    'row_3_col_4'  /  Float32l, 'row_3_col_5'  /  Float32l, 'row_3_col_6'  /  Float32l, 
    'row_3_col_7'  /  Float32l, 'row_3_col_8'  /  Float32l, 'row_3_col_9'  /  Float32l, 
    'row_3_col_10' /  Float32l, 'row_3_col_11' /  Float32l, 'row_3_col_12' /  Float32l, 
    'row_4_col_1'  /  Float32l, 'row_4_col_2'  /  Float32l, 'row_4_col_3'  /  Float32l, 
    'row_4_col_4'  /  Float32l, 'row_4_col_5'  /  Float32l, 'row_4_col_6'  /  Float32l, 
    'row_4_col_7'  /  Float32l, 'row_4_col_8'  /  Float32l, 'row_4_col_9'  /  Float32l, 
    'row_4_col_10' /  Float32l, 'row_4_col_11' /  Float32l, 'row_4_col_12' /  Float32l, 
    'row_5_col_1'  /  Float32l, 'row_5_col_2'  /  Float32l, 'row_5_col_3'  /  Float32l, 
    'row_5_col_4'  /  Float32l, 'row_5_col_5'  /  Float32l, 'row_5_col_6'  /  Float32l, 
    'row_5_col_7'  /  Float32l, 'row_5_col_8'  /  Float32l, 'row_5_col_9'  /  Float32l, 
    'row_5_col_10' /  Float32l, 'row_5_col_11' /  Float32l, 'row_5_col_12' /  Float32l, 
    'row_6_col_1'  /  Float32l, 'row_6_col_2'  /  Float32l, 'row_6_col_3'  /  Float32l, 
    'row_6_col_4'  /  Float32l, 'row_6_col_5'  /  Float32l, 'row_6_col_6'  /  Float32l, 
    'row_6_col_7'  /  Float32l, 'row_6_col_8'  /  Float32l, 'row_6_col_9'  /  Float32l, 
    'row_6_col_10' /  Float32l, 'row_6_col_11' /  Float32l, 'row_6_col_12' /  Float32l, 
    'row_7_col_1'  /  Float32l, 'row_7_col_2'  /  Float32l, 'row_7_col_3'  /  Float32l, 
    'row_7_col_4'  /  Float32l, 'row_7_col_5'  /  Float32l, 'row_7_col_6'  /  Float32l, 
    'row_7_col_7'  /  Float32l, 'row_7_col_8'  /  Float32l, 'row_7_col_9'  /  Float32l, 
    'row_7_col_10' /  Float32l, 'row_7_col_11' /  Float32l, 'row_7_col_12' /  Float32l, 
    'row_8_col_1'  /  Float32l, 'row_8_col_2'  /  Float32l, 'row_8_col_3'  /  Float32l, 
    'row_8_col_4'  /  Float32l, 'row_8_col_5'  /  Float32l, 'row_8_col_6'  /  Float32l, 
    'row_8_col_7'  /  Float32l, 'row_8_col_8'  /  Float32l, 'row_8_col_9'  /  Float32l, 
    'row_8_col_10' /  Float32l, 'row_8_col_11' /  Float32l, 'row_8_col_12' /  Float32l, 
    'row_9_col_1'  /  Float32l, 'row_9_col_2'  /  Float32l, 'row_9_col_3'  /  Float32l, 
    'row_9_col_4'  /  Float32l, 'row_9_col_5'  /  Float32l, 'row_9_col_6'  /  Float32l, 
    'row_9_col_7'  /  Float32l, 'row_9_col_8'  /  Float32l, 'row_9_col_9'  /  Float32l, 
    'row_9_col_10' /  Float32l, 'row_9_col_11' /  Float32l, 'row_9_col_12' /  Float32l, 
    'row_10_col_1' /  Float32l, 'row_10_col_2' /  Float32l, 'row_10_col_3' /  Float32l, 
    'row_10_col_4' /  Float32l, 'row_10_col_5' /  Float32l, 'row_10_col_6' /  Float32l, 
    'row_10_col_7' /  Float32l, 'row_10_col_8' /  Float32l, 'row_10_col_9' /  Float32l, 
    'row_10_col_10'/  Float32l, 'row_10_col_11'/  Float32l, 'row_10_col_12'/  Float32l, 
    'row_11_col_1' /  Float32l, 'row_11_col_2' /  Float32l, 'row_11_col_3' /  Float32l, 
    'row_11_col_4' /  Float32l, 'row_11_col_5' /  Float32l, 'row_11_col_6' /  Float32l, 
    'row_11_col_7' /  Float32l, 'row_11_col_8' /  Float32l, 'row_11_col_9' /  Float32l, 
    'row_11_col_10'/  Float32l, 'row_11_col_11'/  Float32l, 'row_11_col_12'/  Float32l, 
    'row_12_col_1' /  Float32l, 'row_12_col_2' /  Float32l, 'row_12_col_3' /  Float32l, 
    'row_12_col_4' /  Float32l, 'row_12_col_5' /  Float32l, 'row_12_col_6' /  Float32l, 
    'row_12_col_7' /  Float32l, 'row_12_col_8' /  Float32l, 'row_12_col_9' /  Float32l, 
    'row_12_col_10'/  Float32l, 'row_12_col_11'/  Float32l, 'row_12_col_12'/  Float32l
)
    

descStruct_Channel = Struct(
    'asset_type' /      Computed('Channel'),
    'asset_name' /      CString('utf8'),
    'parent_ID' /       Computed(lambda ctx: ctx._.asset_ID),
    'parent_type' /     Computed(lambda ctx: ctx._.asset_type)
)

descStruct_ForcePlate = Struct(
    'asset_type' /          Computed('ForcePlate'),
    'asset_ID' /            Int32ul,
    'serial_num' /          CString('utf8'),
    'plate_width' /         Float32l,
    'plate_length' /        Float32l,
    'origin_x' /            Float32l, 
    'origin_y' /            Float32l, 
    'origin_z' /            Float32l,
    'calibration_matrix' /  descStruct_ForcePlate_Calibration_Matrix,
    'corners_matrix' /      descStruct_ForcePlate_Corners_Matrix,
    'plate_type' /          Int32ul,
    'channel_data_type' /   Int32ul,
    'child_count' /         Int32ul,
    'children' /            descStruct_Channel[this.child_count],
    'relative_offset' /     Tell
)
# --------------------------


# Structures for Device(s) description
# --------------------------
descStruct_Device = Struct(
    'asset_type' /          Computed("Device"),
    'id_self' /             Int32ul,
    'asset_name' /          CString('utf8'),
    'serial_num' /          CString('utf8'),
    'device_type' /         Int32ul,
    'channel_data_type' /   Int32ul,
    'child_count' /         Int32ul,
    'children' /            descStruct_Channel[this.child_count],
    'relative_offset' /     Tell
)
# --------------------------


# Structures for camera description
# --------------------------
descStruct_Camera = Struct(
    'asset_type' /      Computed("Camera"),
    'asset_name' /      CString('utf8'),
    'pos_x' /           Float32l, 
    'pos_y' /           Float32l, 
    'pos_z' /           Float32l,
    'rot_w' /           Float32l, 
    'rot_x' /           Float32l, 
    'rot_y' /           Float32l, 
    'rot_z' /           Float32l,
    'relative_offset' / Tell
)
# --------------------------













