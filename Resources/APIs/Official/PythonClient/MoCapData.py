#Copyright © 2021 Naturalpoint
#
#Licensed under the Apache License, Version 2.0 (the "License")
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# OptiTrack NatNet direct depacketization sample for Python 3.x
#


# Uses the Python NatNetClient.py library to establish a connection (by creating a NatNetClient),
# and receive data via a NatNet connection and decode it using the NatNetClient library.

#Utility functions

import copy
import hashlib
import random
import warnings

import numpy as np



K_SKIP = [0,0,1]
K_FAIL = [0,1,0]
K_PASS = [1,0,0]

# get_tab_str
# generate a string that takes the nesting level into account
def get_tab_str(tab_str, level):
    out_tab_str=""
    loop_range = range(0,level)
    for _ in loop_range:
        out_tab_str+=tab_str
    return out_tab_str

def add_lists(totals, totals_tmp):
    totals[0]+=totals_tmp[0]
    totals[1]+=totals_tmp[1]
    totals[2]+=totals_tmp[2]
    return totals

def test_hash(test_name, test_hash_str, test_object):
    out_str = test_object.get_as_string()
    out_hash_str=hashlib.sha1(out_str.encode()).hexdigest()
    ret_value=True
    if test_hash_str == out_hash_str:
        print("[PASS]:%s"%test_name)
    else:
        print("[FAIL]:%s test_hash_str != out_hash_str"%test_name)
        print("test_hash_str=%s"%test_hash_str)
        print("out_hash_str=%s"%out_hash_str)
        print("out_str =\n%s"%out_str)
        ret_value=False
    return ret_value

def test_hash2(test_name, test_hash_str, test_object, run_test=True):
    ret_value = K_FAIL
    out_str = "FAIL"
    out_str2=""
    indent_string="       "
    if not run_test:
        ret_value = K_SKIP
        out_str = "SKIP"
    elif test_object == None:
        out_str = "FAIL"
        ret_value = K_FAIL
        out_str2 = "%sERROR: test_object was None"%indent_string
    else:

        if str(type(test_object)) != 'NoneType':
            obj_out_str = test_object.get_as_string()
            obj_out_hash_str=hashlib.sha1(obj_out_str.encode()).hexdigest()

        if test_hash_str == obj_out_hash_str:
            out_str = "PASS"
            ret_value = K_PASS
        else:
            out_str2+="%s%s test_hash_str != out_hash_str\n"%(indent_string,test_name)
            out_str2+="%stest_hash_str=%s\n"%(indent_string,test_hash_str)
            out_str2+="%sobj_out_hash_str=%s\n"%(indent_string,obj_out_hash_str)
            out_str2+="%sobj_out_str =\n%s"%(indent_string,obj_out_str)
            ret_value = K_FAIL
    print("[%s]:%s"%(out_str,test_name))

    if len(out_str2):
        print("%s"%out_str2)
    return ret_value

def get_as_string(input_str):
    type_input_str=str(type(input_str))
    if type_input_str == "<class 'str'>":
        return input_str
    elif type_input_str ==  "<class 'NoneType'>":
        return ""
    elif type_input_str == "<class 'bytes'>":
        return input_str.decode('utf-8')
    else:
        print("type_input_str = %s NOT HANDLED"%type_input_str)
        return input_str

# #
# Asset Data Classes
# # 

# Simply logs frame number; seems overkill, might refactor out
class FramePrefix:
    def __init__(self, motive_version) -> None:
        self.motive_version = motive_version
        self.dtype = self._dtype()

        self.__frame = np.array([], dtype=self.dtype)

    # Get dtype based on the motive version  
    def _dtype(self):
        if self.motive_version:
            pass

        dtype = np.dtype([('frame_number', np.int32)])
  
        return dtype
    
    def bytesize(self) -> int:
        return self.dtype.itemsize

    def parse(self, data):
        if len(data) != self.dtype.itemsize:
            raise ValueError(
                "FramePrefixData.parse() : Expected %d bytes, recieved %d."%(
                self.dtype.itemsize, len(data)))
        
        self.__frame['frame_number'] = np.frombuffer(data, dtype=self.dtype)
        
    def frame(self):
        if np.all(np.equal(self.__frame['frame_number'], 0)):
            warnings.warn("FramePrefixData.export() : No data recorded.", Warning)
        
        return self.__frame

# Short of fewer data params, hard to say this differs meaningfully from LabeledMarker
class MarkerSet:
    def __init__(self, motive_version, name, count, data = None) -> None:
        self.motive_version = motive_version
        self.name = name
        self.count = count
        self.dtype = self._dtype() # Note: marker_pos structure

        self.__frame = np.array([
            ("model", name),
            ("markers", np.array([], dtype=self.dtype))
        ])

        if data:
            self.parse(data)

    def _dtype(self) -> np.dtype:
        if self.motive_version:
            pass
        
        # marker_count len array of positional tuples 
        dtype = np.dtype([
            ('pos', 
             np.dtype([('x', np.float32), ('y', np.float32), ('z', np.float32)]), 
            (self.count,))
        ])

        return dtype

    def bytesize(self) -> int:
        return self.dtype.itemsize * self.count

    def parse(self, bytestream) -> None:
        chunk_size = self.bytesize // self.count

        if len(bytestream) != self.bytesize:
            raise ValueError(
                "MarkerData.parse() : Expected %d bytes\n\t%d markers * %d bytes\nRecieved %d."%(
                    self.bytesize, self.count, chunk_size, len(bytestream)))

        for i in range(self.count):
            start = i*chunk_size
            end = (i+1)*chunk_size
            marker = np.frombuffer(bytestream[start:end], dtype=self.dtype)
            self.__frame['markers']['pos'][i] = marker['pos']

    def frame(self) -> np.array:
        if np.all(np.equal(self.__frame['marker_pos_list']['pos'], 0)):
            warnings.warn("MarkerData.frame() : No markers positions recorded.", Warning)
        

        return self.__frame

# For storing markerset belonging to models or otherwise unlabeled
class MarkerSets:
    def __init__(self, motive_version) -> None:
        self.motive_version = motive_version
        self.__frame = np.array([
            ("labeled", np.array([], dtype=object)), 
            ("unlabeled", np.array([], dtype=object))
        ])
        self.dtype = self.__frame.dtype

    def bytesize(self, count) -> int:
        dummy = MarkerSet(self.motive_version, "dummy", count)
        return dummy.bytesize
    
    def parse(self, count, data, label = None) -> None:
        model = label if label is not None else "unlabeled"
        markers = MarkerSet(self.motive_version, model, count)
        markers.parse(data)

        if model == "unlabeled":
            self.__frame['unlabeled'] = np.append(self.__frame['unlabeled'], markers.frame())

        else:
            self.__frame['labeled'] = np.append(self.__frame['labeled'], markers.frame())

    def frame(self) -> np.array:
        if np.all(np.equal(self.__frame['labeled'], 0)):
            warnings.warn("MarkerSetData.frame() : No labeled markers recorded.", Warning)
        
        if np.all(np.equal(self.__frame['unlabeled'], 0)):
            warnings.warn("MarkerSetData.frame() : No unlabeled markers recorded.", Warning)
        
        return self.__frame

# Not used for versions >= 3.0; add support anyway
class RigidBodyMarker:
    def __init__(self):
        self.pos = [0.0,0.0,0.0]
        self.id_num = 0
        self.size = 0
        self.error = 0

    def get_data_dict(self):
        data = OrderedDict()
        data['pos'] = Pos(self.pos[0],self.pos[1],self.pos[2])
        data['id_num'] = self.id_num
        data['size'] = self.size
        data['error'] = self.error

        return data

    def get_as_string(self, tab_str="  ", level=0):
        out_tab_str = get_tab_str(tab_str, level)
        out_str = ""

        out_str += "%sPosition: [%3.2f %3.2f %3.2f]\n"%( out_tab_str, self.pos[0], self.pos[1], self.pos[2] )
        out_str += "%sID      : %3.1d\n"%(out_tab_str, self.id_num)
        out_str += "%sSize    : %3.1d\n"%(out_tab_str, self.size)
        return out_str

# Each element in RigidBodies is of this class
class RigidBody:
    def __init__(self, motive_version, data=None) -> None:
        self.motive_version = motive_version
        self.dtype = self._dtype()
        self.__frame = np.array([], dtype=self.dtype)

        if data:
            self.parse(data)

    # Set the dtype based on the motive version
    def _dtype(self) -> np.dtype:
        if self.motive_version:
            pass

        dtype = [
            ('id_num', np.int32),
            ('pos', [('x', np.float32), ('y', np.float32), ('z', np.float32)]),
            ('rot', [('w', np.float32), ('x', np.float32), ('y', np.float32), ('z', np.float32)]),
            ('tracking_valid', np.int16),
            ('error', np.float32)
        ] 


        return dtype
    
    def bytesize(self) -> int:
        return self.dtype.itemsize

    def parse(self, data) -> None:
        if len(data) != self.dtype.itemsize:
            raise ValueError(
                "RigidBody.parse() : Expected %d bytes, recieved %d"%(
                    self.dtype.itemsize,len(data)))
        
        self.__frame = np.frombuffer(data, dtype=self.dtype)
        
        # Tracking validity communicated by least significant bit
        self.__frame['tracking_valid'] = (self.__frame['tracking_valid'] & 0x01) != 0

    def frame(self) -> np.array:
        if self.__frame['id_num'] == None:
            warnings.warn("RigidBody.frame() : ID not recorded.", Warning)
        
        if self.__frame['pos'] == None:
            warnings.warn("RigidBody.frame() : position not recorded.", Warning)
        
        if self.__frame['rot'] == None:
            warnings.warn("RigidBody.frame() : rotation not recorded.", Warning)
        
        if self.__frame['error'] == None:
            warnings.warn("RigidBody.frame() : error not recorded.", Warning)
        
        if self.__frame['tracking_valid'] == None:
            warnings.warn("RigidBody.frame() : tracking validity not recorded.", Warning)

        return self.__frame

# Each element in Skeletons is of this class; also used for single rigid bodies (i.e., objects)
class RigidBodies:
    def __init__(self, motive_version, rb_count, data = None) -> None:
        self.motive_version = motive_version
        self.count = rb_count

        self.__frame = np.array([('rigid_bodies', np.array([], dtype=object))])
        self.dtype = self.__frame.dtype

        if data:
            self.parse(data)

    def bytesize(self, count) -> int:
        dummy = RigidBody(self.motive_version)
        return dummy.bytesize * count

    def parse(self, data) -> None:
        rb = RigidBody(self.motive_version)
        if len(data) != rb.dtype.itemsize * self.count:
            raise ValueError(
                "RigidBodies.parse() : Expected %d bytes\n\t%d rigid bodies * %d bytes\nRecieved %d."%(rb.dtype.itemsize * self.count, self.count, rb.dtype.itemsize, len(data)))
        

        for i in range(self.count):
            start = i*rb.dtype.itemsize
            end = (i+1)*rb.dtype.itemsize
            rb.parse(data[start:end])
            self.__frame['rigid_bodies'] = np.append(self.__frame['rigid_bodies'], rb.frame())
        
    def frame(self) -> np.array:
        if np.all(np.equal(self.__frame['rigid_bodies'], 0)):
            warnings.warn("RigidBodies.frame() : No rigid bodies recorded.", Warning)
        
        return self.__frame

# Each skeleton comprises some number of Rigidbodies
class Skeleton:
    def __init__(self, motive_version, id_num, rb_count, data = None) -> None:
        self.motive_version = motive_version
        self.id = id_num
        self.count = rb_count

        self.__frame = np.array([("id_num", self.id), ("rigid_bodies", np.array([], dtype=object))])
        self.dtype = self.__frame.dtype

        if data:
            self.parse(data)

    def bytesize(self) -> int:
        dummy = RigidBodies(self.motive_version, self.count)
        return dummy.bytesize

    def parse(self, data) -> None:
        rbodies = RigidBodies(self.motive_version, self.count)

        try:
            rbodies.parse(data)
        except ValueError as e:
            raise ValueError("Skeleton.parse() : \n\t%s"%e)
       
        self.__frame['rigid_bodies'] = np.append(self.__frame['rigid_bodies'], rbodies.frame())

    def frame(self) -> np.array:
        if np.all(np.equal(self.__frame['rigid_bodies'], 0)):
            warnings.warn("Skeleton.frame() : No rigid bodies recorded.", Warning)
        
        return self.__frame

# Seems like MarkerSets but more detailed...?
class LabeledMarker:
    def __init__(self, motive_version, data = None) -> None:

        self.motive_version = motive_version
        self.dtype = self._dtype()
        self.__frame = np.array([], dtype=self.dtype['out'])

        if data:
            self.parse(data)



        # self.id_num=new_id
        # self.pos = pos
        # self.size = size
        # self.param = param
        # self.residual = residual

        # Dunno if this'll need to be reincorporated
        # if str(type(size)) == "<class 'tuple'>":
        #     self.size=size[0]

    # Set the dtype based on the motive version
    def _dtype(self) -> None:
        # TODO: account for motive version
        if self.motive_version:
            pass

        dtype_in = [            
            ('id_num', np.int32),
            ('pos', [('x', np.float32), ('y', np.float32), ('z', np.float32)]),
            ('size', np.float32),
            ('param', np.int16),
            ('residual', np.float32)
        ]

        dtype_out = [
            ('model_id', np.int32),
            ('marker_id', np.int32),
            ('pos', [('x', np.float32), ('y', np.float32), ('z', np.float32)]),
            ('size', np.float32),
            ('occluded', np.int16),
            ('point_cloud_solved', np.int16),
            ('model_solved', np.int16),
            ('residual', np.float32)
        ]

        return {'in': dtype_in, 'out': dtype_out}
    
    def bytesize(self) -> int:
        return self.dtype['in'].itemsize

    def parse(self, data):

        # The format of recieved data differs from that of the output
        expected = self.dtype['in'].itemsize
        received = len(data)
        if received != expected:
            raise ValueError(
                "\nLabeledMarker.parse() | Unexpected packet size" +\
                "\n\tExpected: %d bytes, \n\tReceived: %d bytes"%(
                expected, received))
        
        # parse input data into temp storage
        tmp_data = np.frombuffer(data, dtype=self.dtype['in'])


        # Some values need to be decoded prior to storing, but not these
        self.__frame['pos'] = tmp_data['pos']
        self.__frame['size'] = tmp_data['size']
        self.__frame['residual'] = tmp_data['residual']

        # These ones; using some bit shift voodoo I don't care to understand
        self.__frame['model_id'], self.__frame['marker_id'] = self.__decode_marker_id(tmp_data['id_num'])
        # Decode param into occluded, point_cloud_solved, and model_solved
        self.__frame['occluded'], self.__frame['point_cloud_solved'], self.__frame['model_solved'] = self.__decode_param(tmp_data['param'])


    def frame(self) -> np.array:
        return self.__frame

    def __decode_marker_id(self, id_num):
        model_id = id_num >> 16
        marker_id = id_num & 0x0000ffff
        return model_id, marker_id

    def __decode_param(self, param):
        occluded = ( param & 0x01 ) != 0
        point_cloud_solved = ( param & 0x02 ) != 0
        model_solved = ( param & 0x04 ) != 0
        return occluded,point_cloud_solved, model_solved

# For storing sets of LabeledMarker
class LabeledMarkerData:
    def __init__(self, motive_version, count, data = None) -> None:
        self.motive_version = motive_version
        self.count = count
        self.__frame=np.array(['LabeledMarkers', object])
        self.dtype = self.__frame.dtype

    def bytesize(self) -> int:
        dummy = LabeledMarker(self.motive_version)
        return dummy.bytesize * self.count

    def parse(self, data) -> None:
        marker = LabeledMarker(self.motive_version)
        if len(data) != marker.bytesize * self.count:
            raise ValueError(
                "LabeledMarkerData.parse() : Expected %d bytes\n\t%d markers * %d bytes\nRecieved %d."%(
                    marker.bytesize * self.count, self.count, marker.bytesize, len(data)))
        

        for i in range(self.count):
            start = i*marker.bytesize
            end = (i+1)*marker.bytesize
            marker.parse(data[start:end])
            self.__frame['LabeledMarkers'] = np.append(self.__frame['LabeledMarkers'], marker.frame())


# TODO: Add support
class ForcePlateChannelData:
    def __init__(self):
        # list of floats
        self.frame_list=[]

    def add__frame_entry(self, frame_entry):
        self.frame_list.append(copy.deepcopy(frame_entry))
        return len(self.frame_list)

    def get_data_dict(self):
        data = OrderedDict()
        for i in range(len(self.frame_list)):
            data['frame_%d'%i] = self.frame_list[i]

        return data

    def get_as_string(self, tab_str, level, channel_num = -1):
        fc_max = 4
        out_tab_str  = get_tab_str(tab_str, level)

        out_str = ""
        frame_count = len(self.frame_list)
        fc_show = min(frame_count, fc_max)
        out_str += "%s"%(out_tab_str)
        if channel_num >= 0 :
            out_str += "Channel %3.1d: "%channel_num
        out_str += "%3.1d Frames - Frame Data: "%(frame_count)
        for i in range(fc_show):
            out_str += "%3.2f "%(self.frame_list[i])
        if fc_show < frame_count :
            out_str += " - Showing %3.1d of %3.1d frames"%(fc_show, frame_count)
        out_str += "\n"
        return out_str
# TODO: Add support
class ForcePlate:
    def __init__(self, new_id=0):
        self.id_num = new_id
        self.channel_data_list=[]

    def add_channel_data(self, channel_data):
        self.channel_data_list.append(copy.deepcopy(channel_data))
        return len(self.channel_data_list)

    def get_data_dict(self):
        data = OrderedDict()
        for i in range(len(self.channel_data_list)):
            channel_data = self.channel_data_list[i]
            data['channel_%d'%i] = channel_data.get_data_dict()

        return data

    def get_as_string(self, tab_str, level):
        out_tab_str = get_tab_str(tab_str, level)
        out_str = ""

        out_str += "%sID           : %3.1d"%(out_tab_str, self.id_num)
        num_channels = len(self.channel_data_list)
        out_str += "%sChannel Count: %3.1d\n"%(out_tab_str, num_channels)
        for i in range(num_channels):
            out_str += self.channel_data_list[i].get_as_string(tab_str, level+1,i)
        return out_str
# TODO: Add support
class ForcePlateData:
    def __init__(self):
        self.force_plate_list=[]

    def add_force_plate(self, force_plate):
        self.force_plate_list.append(copy.deepcopy(force_plate))
        return len(self.force_plate_list)

    def get_force_plate_count(self):
        return len(self.force_plate_list)

    def get_data_dict(self):
        data = OrderedDict()
        for i in range(len(self.force_plate_list)):
            force_plate = self.force_plate_list[i]
            data['force_plate_%d'%i] = force_plate.get_data_dict()

        return data

    def get_as_string(self, tab_str="  ", level=0):
        out_tab_str = get_tab_str(tab_str, level)
        out_tab_str2 = get_tab_str(tab_str, level+1)
        out_str=""

        force_plate_count = len(self.force_plate_list)
        out_str += "%sForce Plate Count: %3.1d\n"%(out_tab_str, force_plate_count)
        for i in range(force_plate_count):
            out_str += "%sForce Plate %3.1d\n"%(out_tab_str2, i)
            out_str += self.force_plate_list[i].get_as_string(tab_str, level+2)

        return out_str
# TODO: Add support
class DeviceChannelData:
    def __init__(self):
        # list of floats
        self.frame_list=[]

    def add__frame_entry(self, frame_entry):
        self.frame_list.append(copy.deepcopy(frame_entry))
        return len(self.frame_list)
    
    def get_data_dict(self):
        data = OrderedDict()
        for i in range(len(self.frame_list)):
            data['frame_%d'%i] = self.frame_list[i]

        return data

    def get_as_string(self, tab_str, level, channel_num = -1):
        fc_max = 4
        out_tab_str  = get_tab_str(tab_str, level)

        out_str = ""
        frame_count = len(self.frame_list)
        fc_show = min(frame_count, fc_max)
        out_str += "%s"%(out_tab_str)
        if channel_num >= 0:
            out_str += "Channel %3.1d: "%channel_num
        out_str += "%3.1d Frames - Frame Data: "%(frame_count)
        for i in range(fc_show):
            out_str += "%3.2f "%(self.frame_list[i])
        if fc_show < frame_count:
            out_str += " - Showing %3.1d of %3.1d frames"%(fc_show, frame_count)
        out_str += "\n"
        return out_str
# TODO: Add support
class Device:
    def __init__(self, new_id):
        self.id_num=new_id
        self.channel_data_list = []

    def add_channel_data(self, channel_data):
        self.channel_data_list.append(copy.deepcopy(channel_data))
        return len(self.channel_data_list)
    
    def get_data_dict(self):
        data = OrderedDict()
        for i in range(len(self.channel_data_list)):
            channel_data = self.channel_data_list[i]
            data['channel_%d'%i] = channel_data.get_data_dict()

        return data

    def get_as_string(self, tab_str, level, device_num):
        out_tab_str = get_tab_str(tab_str, level)

        out_str = ""

        num_channels = len(self.channel_data_list)
        out_str+= "%sDevice %3.1d      ID: %3.1d Num Channels: %3.1d\n"% (out_tab_str, device_num, self.id_num, num_channels )
        for i in range(num_channels):
            out_str += self.channel_data_list[i].get_as_string(tab_str, level+1, i)

        return out_str
# TODO: Add support
class DeviceData:
    def __init__(self):
        self.device_list=[]

    def add_device(self, device):
        self.device_list.append(copy.deepcopy(device))
        return len(self.device_list)

    def get_device_count(self):
        return len(self.device_list)

    def get_data_dict(self):
        data = OrderedDict()
        for i in range(len(self.device_list)):
            device = self.device_list[i]
            data['device_%d'%i] = device.get_data_dict()

        return data

    def get_as_string(self, tab_str = "  ", level = 0):
        out_tab_str = get_tab_str(tab_str, level)

        out_str = ""

        device_count = len(self.device_list)
        out_str += "%sDevice Count: %3.1d\n"%(out_tab_str, device_count)
        for i in range(device_count):
            out_str += self.device_list[i].get_as_string(tab_str, level+1, i)
        return out_str

# timestamps and other metadata
class FrameSuffixData:
    def __init__(self, motive_version, data = None) -> None:
        self.motive_version = motive_version
        self.dtype = self._dtype()
        self.__frame = np.array([(0, 0, -1, -1, -1, -1, 0, False, True)], dtype=self.dtype)

        if data:
            self.parse(data)

    def _dtype(self) -> np.dtype:
        if self.motive_version:
            pass

        dtype = np.dtype([
            ('timecode', np.int32),
            ('timecode_sub', np.int32),
            ('timestamp', np.float64),
            ('stamp_camera_mid_exposure', np.uint64),
            ('stamp_data_received', np.uint64),
            ('stamp_transmit', np.uint64),
            ('param', np.int32),
            ('is_recording', np.bool),
            ('tracked_models_changed', np.bool)
        ])

        return dtype
    
    def bytesize(self) -> int:
        return self.dtype.itemsize
    
    def parse(self, data) -> None:
        if len(data) != self.dtype.itemsize:
            raise ValueError(
                "FrameSuffixData.parse() : Expected %d bytes, recieved %d."%(
                self.dtype.itemsize, len(data)))
        
        self.__frame = np.frombuffer(data, dtype=self.dtype)

    def frame(self) -> np.array:
        return self.__frame

# Aggregate frame data
class MoCapFrame:
    def __init__(self) -> None:
        
        # Aggregate Frame Data
        self.__frame = {
            'prefix': [],
            'model_marker_sets': [],
            'unlabeled_marker_sets': [],
            'rigid_bodies': [],
            'skeletons': [],
            'labeled_marker_sets': [],
            'force_plates': [],
            'devices': [],
            'suffix': []
        }
    
    # Return asset data
    def frame(self, asset = None, frame = None) -> np.array:

        if asset:
            if asset not in self.__frame.keys():
                raise ValueError("MoCapData.frame() | Unexpected asset type: %s"%asset)
            
            if frame:
                self.__frame[asset] = frame

            return self.__frame[asset]

        if frame:
            raise ValueError("MoCapData.frame() | Asset type required if frame is provided.")
            

        return self.__frame

# test program
import unittest


def generate_prefix_data(frame_num = 0):
    frame_prefix_data = FramePrefix(frame_num)
    return frame_prefix_data

def generate_label(label_base="label", label_num=0):
    out_label= "%s_%3.3d"%(label_base, label_num)
    return out_label

def generate_position_srand(pos_num=0, frame_num=0):
    random.seed(pos_num + (frame_num*1000))
    position=[(random.random()*100),(random.random()*100),(random.random()*100)]
    return position

def generate_marker_data(label_base, label_num, num_points=1):
    label=generate_label(label_base, label_num)
    if((label_base == None) or (label_base == "")):
        label=""
    marker_data=MarkerSet()
    marker_data.set_model_name(label)
    start_num=label_num * 10000
    end_num = start_num+num_points
    for point_num in range(start_num, end_num):
        position=generate_position_srand(point_num)
        marker_data.add_pos(position)

    return marker_data

def generate_marker_set_data(frame_num = 0, marker_set_num=0):
    marker_set_data=MarkerSets()
    #add labeled markers
    marker_set_data.add_marker_data(generate_marker_data("marker",0,3))
    marker_set_data.add_marker_data(generate_marker_data("marker",1,6))
    marker_set_data.add_marker_data(generate_marker_data("marker",2,5))
    #add unlabeled markers
    num_points=5
    start_num=(frame_num * 100000) + (10000 + marker_set_num)
    end_num = start_num+num_points
    for point_num in range(start_num, end_num):
        position=generate_position_srand(point_num)
        marker_set_data.add_unlabeled_marker(position)
    return marker_set_data

def generate_rigid_body_marker_srand(marker_num=0, frame_num = 0):
    rigid_body_marker=RigidBodyMarker()
    rbm_num=11000+marker_num
    random.seed(rbm_num)
    rigid_body_marker.pos=generate_position_srand(rbm_num, frame_num)
    rigid_body_marker.id_num=marker_num
    rigid_body_marker.size=1
    rigid_body_marker.error=random.random()

    return rigid_body_marker

def generate_rigid_body(body_num=0, frame_num = 0):
    pos=generate_position_srand(10000+body_num, frame_num)
    rot = [1,0,0,0]
    rigid_body = RigidBody(body_num,pos,rot)
    rigid_body.add_rigid_body_marker(generate_rigid_body_marker_srand(0, frame_num))
    rigid_body.add_rigid_body_marker(generate_rigid_body_marker_srand(1, frame_num))
    rigid_body.add_rigid_body_marker(generate_rigid_body_marker_srand(2))
    return rigid_body

def generate_rigid_body_data(frame_num = 0):
    rigid_body_data=RigidBodies()
    # add rigid bodies
    rigid_body_data.add_rigid_body(generate_rigid_body(0, frame_num))
    rigid_body_data.add_rigid_body(generate_rigid_body(1, frame_num))
    rigid_body_data.add_rigid_body(generate_rigid_body(2, frame_num))
    return rigid_body_data

def generate_skeleton(frame_num=0, skeleton_num=0,num_rbs=1):
    skeleton = Skeleton(skeleton_num)
    # add rigid bodies
    rb_seed_start=skeleton_num *165
    rb_seed_end=rb_seed_start + num_rbs
    for rb_num in range(rb_seed_start, rb_seed_end):
        skeleton.add_rigid_body(generate_rigid_body(rb_num, frame_num))
    return skeleton

def generate_skeleton_data(frame_num = 0):
    skeleton_data = Skeletons()
    skeleton_data.add_skeleton(generate_skeleton(frame_num, 0, 2))
    skeleton_data.add_skeleton(generate_skeleton(frame_num, 1, 6))
    skeleton_data.add_skeleton(generate_skeleton(frame_num, 2, 3))
    return skeleton_data

def generate_labeled_marker(frame_num=0, marker_num=0):
    point_num = (frame_num *2000) + marker_num
    pos = generate_position_srand(point_num)
    size = 1
    param = 0
    #occluded 0x01
    param += 0x01 * 0
    #point_cloud_solved 0x02
    param += 0x02 * 0
    #model_solved 0x04
    param += 0x04 * 1
    residual = 0.01
    return LabeledMarker(marker_num, pos, size, param,residual)

def generate_labeled_marker_data(frame_num = 0):
    labeled_marker_data = LabeledMarkerData()
    #add labeled marker
    labeled_marker_data.add_labeled_marker(generate_labeled_marker(frame_num,0))
    labeled_marker_data.add_labeled_marker(generate_labeled_marker(frame_num,1))
    labeled_marker_data.add_labeled_marker(generate_labeled_marker(frame_num,2))

    return labeled_marker_data

def generate_fp_channel_data(frame_num=0,fp_num=0, channel_num=0, num__frames =1):
    rseed=(frame_num*100000)+(fp_num*10000)+(channel_num *1000)
    random.seed(rseed)
    fp_channel_data = ForcePlateChannelData()
    for _ in range(num__frames):
        fp_channel_data.add__frame_entry(100.0*random.random())
    return fp_channel_data

def generate_force_plate(frame_num=0, fp_num = 0, num_channels=1):
    force_plate = ForcePlate(fp_num)
    #add channel_data
    for i in range(num_channels):
        force_plate.add_channel_data(generate_fp_channel_data(frame_num,fp_num, i, 10))
    return force_plate

def generate_force_plate_data(frame_num = 0):
    force_plate_data = ForcePlateData()
    # add force plates
    force_plate_data.add_force_plate(generate_force_plate(frame_num, 0,3))
    force_plate_data.add_force_plate(generate_force_plate(frame_num, 1,4))
    force_plate_data.add_force_plate(generate_force_plate(frame_num, 2,2))
    return force_plate_data

def generate_device_channel_data(frame_num=0,device_num=0, channel_num=0, num__frames =1):
    rseed=(frame_num*100000)+(device_num*10000)+(channel_num *1000)
    random.seed(rseed)
    device_channel_data = DeviceChannelData()
    for _ in range(num__frames):
        device_channel_data.add__frame_entry(100.0*random.random())
    return device_channel_data

def generate_device(frame_num=0, device_num=0):
    device = Device(device_num)
    device.add_channel_data(generate_device_channel_data(frame_num, device_num,1,4))
    device.add_channel_data(generate_device_channel_data(frame_num, device_num,3,2))
    device.add_channel_data(generate_device_channel_data(frame_num, device_num,7,6))
    return device

def generate_device_data(frame_num = 0):
    device_data=DeviceData()
    device_data.add_device(generate_device(frame_num, 0))
    device_data.add_device(generate_device(frame_num, 2))
    return device_data

def generate_suffix_data(frame_num = 0):
    frame_suffix_data = FrameSuffixData()
    frame_suffix_data.stamp_camera_mid_exposure = 5844402979291+frame_num
    frame_suffix_data.stamp_data_received = 0
    frame_suffix_data.stamp_transmit = 5844403268753+ frame_num
    frame_suffix_data.timecode = 0
    frame_suffix_data.timecode_sub = 0
    frame_suffix_data.timestamp = 762.63
    return frame_suffix_data

def generate_mocap_data(frame_num=0):
    mocap_data=MoCapFrame()

    mocap_data.set_prefix_data(generate_prefix_data(frame_num))
    mocap_data.set_marker_set_data(generate_marker_set_data(frame_num))
    mocap_data.set_rigid_body_data(generate_rigid_body_data(frame_num))
    mocap_data.set_skeleton_data(generate_skeleton_data(frame_num))
    mocap_data.set_labeled_marker_data(generate_labeled_marker_data(frame_num))
    mocap_data.set_force_plate_data(generate_force_plate_data(frame_num))
    mocap_data.set_device_data(generate_device_data(frame_num))
    mocap_data.set_suffix_data(generate_suffix_data(frame_num))

    return mocap_data

def test_all(run_test=True):
    totals=[0,0,0]
    if run_test is True:
        test_cases=[["Test Prefix Data 0",          "bffba016d02cf2167780df31aee697e1ec746b4c",
                     "generate_prefix_data(0)",True],
                    ["Test Marker Set Data 0",      "d2550194fed1b1fc525f4f4d06bf584f291f41c7",
                     "generate_marker_set_data(0)",True],
                    ["Test Rigid Body Data 0",      "abd1a48a476eaa9b5c4fae6e705e03aa75f85624",
                     "generate_rigid_body_data(0)",True],
                    ["Test Skeleton Data 0",        "1e36e3334e291cebfaa530d7aab2122d6983ecab",
                     "generate_skeleton_data(0)",True],
                    ["Test Labeled Marker Data 0",  "25f3ee026c3c8fc716fbb05c34138ef5afd95d75",
                     "generate_labeled_marker_data(0)",True],
                    ["Test Force Plate Data 0",    "b83d04a1b89169bdcefee3bc3951c3bdcb6b792e",
                     "generate_force_plate_data(0)",True],
                    ["Test Device Data 0",         "be10f0b93a7ba3858dce976b7868c1f79fd719c3",
                     "generate_device_data(0)",True],
                    ["Test Suffix Data 0",         "6aa02c434bdb53a418ae1b1f73317dc80a5f887d",
                     "generate_suffix_data(0)",True],
                    ["Test MoCap Data 0",          "09930ecf665d9eb3ca61616f9bcc55890373f414",
                     "generate_mocap_data(0)",True]
                    ]
        num_tests = len(test_cases)
        for i in range(num_tests):
            data = eval(test_cases[i][2])
            totals_tmp = test_hash2(test_cases[i][0],test_cases[i][1],data,test_cases[i][3])
            totals=add_lists(totals, totals_tmp)

    print("--------------------")
    print("[PASS] Count = %3.1d"%totals[0])
    print("[FAIL] Count = %3.1d"%totals[1])
    print("[SKIP] Count = %3.1d"%totals[2])

    return totals

if __name__ == "__main__":
    test_all(True)
