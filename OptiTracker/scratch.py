from construct import Struct, CString, Byte, Default
from construct import IfThenElse, Peek, this, Computed, Tell, Probe, Debugger
from construct import Int32ul, Int16ub, Float32l, Int64ul, Int32ul
import struct
import random



marker_data_v3 = Struct(
    # 'ctx._.' points to enclosing struct
    'id_model' / Default(Computed(lambda ctx: ctx._.id_model), 'unlabeled'),
    #Probe(this.id_model),
    'pos_x' / Default(Float32l, 0.0),
    #Probe(this.pos_x),
    'pos_y' / Default(Float32l, 0.0),
    #Probe(this.pos_y),
    'pos_z' / Default(Float32l, 0.0)
   #Probe(this.pos_z)
)

# TODO: test Peek() with dummy data; not sure if this works like I think it does
marker_set_data_v3 = Struct(
    'id_model' / Default(CString('utf8'), 'unlabeled'),
    # 'id_model' / IfThenElse(
    #     # Model labels terminate with null byte; if byte non-null, grab model label
    #     Peek(Byte) != 0, 
    #     Probe(lookahead=16),
    #     #CString('utf8'),
    #     # Otherwise, default to 'unlabeled'
    #     Default(CString('utf8'), 'unlabeled')
    # ),
    'count' / Default(Int32ul, 5),
    # [] operator constructs a list (of len count) of given struct
    #Probe(this.id_model),
    #Probe(this.count),
    'markers' / marker_data_v3[5]
)

marker_sets_data_v3 = Struct(
    'count' / Default(Int32ul,3),
    Probe(this.count),
    'sets' / marker_set_data_v3[3],
    'offset' / Tell,
    #Probe(this.sets)
)



#880100005461626c650005000000c894

with open('OptiTracker/API/bins/bytes_marker_set.bin', 'rb') as f:
    bs = f.read()


# 0xBB, 0xAA, 0x3E, 0xCB, 0x5A, 0x16, 0xBB, 0xF2, 0x09, 0x11, 0x3F, 0xDD,
# 0x09, 0x76, 0xBE, 0x7E, 0x3D, 0xDB, 0x3A, 0x05

Debugger(marker_sets_data_v3.parse(bs))

b'\0xBB\0xAA\0x3E\0xCB\0x5A\0x16\0xBB\0xF2\0x09\0x11\0x3F\0xDD\0x09\0x76\0xBE\0x7E\0x3D\0xDB\0x3A\0x05'

b'\0x00\0x2F\0xD1\0x2D'
b'\0x2F\0xD1\0x2D\0x3F'
b'\0xD1\0x2D\0x3F\0x3E'
b'\0x00\0x2F\0xD1\0x2D\0x3F\0x3E'