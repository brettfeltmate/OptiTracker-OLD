# Structures created using the work of art that is the Construct library
from construct import Struct, CString, Optional, Computed, this, Tell, Probe
from construct import Int16sl, Int32ul, Int64ul, Float32l



# Frame prefix structure
dataStruct_Prefix = Struct(
    'asset_type' /      Computed("Prefix"),
    'frame_number' /    Int32ul,
    'relative_offset' / Tell,
    Probe()
)


# Marker & MarkerSet structures
dataStruct_Marker = Struct(
    'asset_type' /      Computed('Marker'),
    'parent_name' /     Computed(lambda ctx: ctx._.asset_name),
    'pos_x' /           Float32l, 
    'pos_y' /           Float32l, 
    'pos_z' /           Float32l
)

dataStruct_MarkerSet = Struct(
    'asset_type' /      Computed("MarkerSet"),
    Probe(),
    'asset_name' /      CString("utf8"),
    Probe(),
    'child_count' /     Int32ul,
    'children' /        dataStruct_Marker[this.child_count],
    'relative_offset' / Tell,
    Probe()
)

dataStruct_MarkerSets = Struct(
    'asset_type' /      Computed("MarkerSets"),
    'child_count' /     Int32ul,
    'packet_size' /     Int32ul,
    'children' /        dataStruct_MarkerSet[this.child_count],
    'relative_offset' / Tell,
    Probe()
)


# Labeled marker structure
    # some properties need decoding
def decodeMarkerID(obj, ctx): return (obj.encoded_id & 0x0000ffff)
def decodeModelID(obj, ctx): return (obj.encoded_id >> 16)

dataStruct_LabeledMarker = Struct(
    'asset_type' /      Computed("LabeledMarker"),
    'encoded_id' /      Int32ul,
    'asset_ID' /        Computed(this.encoded_id * decodeMarkerID),
    'parent_ID' /       Computed(this.encoded_id * decodeModelID),
    'pos_x' /           Float32l,
    'pos_y' /           Float32l,
    'pos_z' /           Float32l,
    'size' /            Float32l,
    'param' /           Int16sl,
    'residual' /        Float32l,
    'relative_offset' / Tell,
    Probe()
)

dataStruct_LabeledMarkerSet = Struct(
    'asset_type' /      Computed("LabeledMarkerSet"),
    'packet_size' /     Int32ul,
    'child_count' /     Int32ul,
    'children' /        dataStruct_LabeledMarker[this.child_count],
    'relative_offset' / Tell,
    Probe()
)


# Legacy marker & marker set structures
dataStruct_LegacyMarker = Struct(
    'asset_type' /      Computed("LegacyMarker"),
    'pos_x' /           Float32l,
    'pos_y' /           Float32l,
    'pos_z' /           Float32l
)

dataStruct_LegacyMarkerSet = Struct(
    'asset_type' /      Computed("LegacyMarkerSet"),
    'child_count' /     Int32ul,
    'packet_size' /     Int32ul,
    'children' /        dataStruct_LegacyMarker[this.child_count],
    'relative_offset' / Tell,
    Probe()
)

# RigidBody & Skeleton structures
    # tracking validity needs decoding
def isTrue(obj, ctx): return (obj & 0x01) != 0

dataStruct_RigidBody = Struct(
    'asset_type' /          Computed("RigidBody"),
    'asset_ID' /            Int32ul,
    'pos_x' /               Float32l,
    'pos_y' /               Float32l,
    'pos_z' /               Float32l,
    'rot_w' /               Float32l,
    'rot_x' /               Float32l,
    'rot_y' /               Float32l,
    'rot_z' /               Float32l,
    'error' /               Float32l,
    'tracking_validity' /   Int16sl
)

dataStruct_RigidBodies = Struct(
    'asset_type' /      Computed("RigidBodies"),
    'child_count' /     Int32ul,
    'packet_size' /     Int32ul,
    'children' /        dataStruct_RigidBody[this.child_count],
    'relative_offset' / Tell,
    Probe()
)

dataStruct_Skeleton = Struct(
    'asset_type' /      Computed("Skeleton"),
    'asset_ID' /        Int32ul,
    'child_count' /     Int32ul,
    'children' /        dataStruct_RigidBody[this.child_count],
    Probe()
)

dataStruct_Skeletons = Struct(
    'asset_type' /      Computed("Skeletons"),
    'child_count' /     Int32ul,
    'packet_size' /     Int32ul,
    'children' /        dataStruct_Skeleton[this.child_count],
    'relative_offset' / Tell,
    Probe()
)


# Asset structures
dataStruct_AssetRigidBody = Struct(
    'asset_type' /      Computed("AssetRigidBody"),
    'asset_ID' /        Int32ul,
    'pos_x' /           Float32l,
    'pos_y' /           Float32l,
    'pos_z' /           Float32l,
    'rot_w' /           Float32l,
    'rot_x' /           Float32l,
    'rot_y' /           Float32l,
    'rot_z' /           Float32l,
    'error' /           Float32l,
    'param' /           Int16sl,
)

dataStruct_AssetMarker = Struct(
    'asset_type' /      Computed("AssetMarker"),
    'asset_ID' /        Int32ul,
    'pos_x' /           Float32l,
    'pos_y' /           Float32l,
    'pos_z' /           Float32l,
    'marker_size' /     Float32l,
    'param' /           Int16sl,
    'residual' /        Float32l
)

dataStruct_Assets = Struct(
    "asset_type" /          Computed("Asset"),
    "asset_ID" /            Int32ul,
    "rigid_body_count" /    Int32ul,
    "rigid_body_children" / dataStruct_AssetRigidBody[this.rigid_body_count],
    "marker_count" /        Int32ul,
    "marker_children" /     dataStruct_AssetMarker[this.marker_count],
    "relative_offset" /     Tell,
    Probe()
)

dataStruct_Assetss = Struct(
    'asset_type' /      Computed("Assets"),
    'child_count' /     Int32ul,
    'packet_size' /     Int32ul,
    'children' /        dataStruct_Assets[this.child_count],
    'relative_offset' / Tell,
    Probe()
)


# Channel & channel frame (ForcePlate & Device) structures
dataStruct_ChannelFrame = Struct(
    'asset_type' /      Computed("ChannelFrame"),
    'parent_ID' /       Computed(lambda ctx: ctx._.parent_ID),
    'parent_type' /     Computed(lambda ctx: ctx._.parent_type),
    'value' /           Float32l
)

dataStruct_Channel = Struct(
    'asset_type' /      Computed("Channel"),
    'parent_ID' /       Computed(lambda ctx: ctx._.self_ID),
    'parent_type' /     Computed(lambda ctx: ctx._.asset_type),
    'child_count' /     Int32ul,
    'children' /        dataStruct_ChannelFrame[this.child_count]
)

dataStruct_ForcePlate = Struct(
    'asset_type' /      Computed("ForcePlate"),
    'asset_ID' /         Int32ul,
    'child_count' /     Int32ul,
    'children' /        dataStruct_Channel[this.child_count]
)

dataStruct_ForcePlates = Struct(
    'asset_type' /      Computed("ForcePlates"),
    'child_count' /     Int32ul,
    'packet_size' /     Int32ul,
    'children' /        dataStruct_ForcePlate[this.child_count],
    'relative_offset' / Tell,
    Probe()
)

dataStruct_Device = Struct(
    'asset_type' /      Computed("Device"),
    'asset_ID' /        Int32ul,
    'child_count' /     Int32ul,
    'children' /        dataStruct_Channel[this.child_count]
)

dataStruct_Devices = Struct(
    'asset_type' /      Computed("Devices"),
    'child_count' /     Int32ul,
    'packet_size' /     Int32ul,
    'children' /        dataStruct_Device[this.child_count],
    'relative_offset' / Tell,
    Probe()
)


# Frame Suffix data structures
    # recording and change flags need decoding
def isRecording(obj, ctx): return (obj.param & 0x01) != 0
def hasChanged(obj, ctx): return (obj.param & 0x02) != 0

dataStruct_Suffix = Struct(
    'asset_type' /                  Computed("Suffix"),
    'timecode' /                    Int32ul,
    'timecode_sub' /                Int32ul,
    'timestamp' /                   Int64ul,
    'stamp_camera_mid_exposure' /   Int64ul,
    'stamp_data_received' /         Int64ul,
    'stamp_transmit' /              Int64ul,
    'prec_timestamp_secs' /         Int32ul,
    'prec_timestamp_frac_secs' /    Int32ul,
    'param' /                       Int16sl,
    'is_recording' /                Computed(this.param * isRecording),
    'tracked_models_changed' /      Computed(this.param * hasChanged),
    'relative_offset' /             Tell,
    Probe()
)



