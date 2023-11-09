
import sys
import os
import time
import pprint

from OptiTracker import OptiTracker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

OptiTracker = OptiTracker()

OptiTracker.init_client()


OptiTracker.start_client()


print("\n\n================================")
print("Test print of full description\n================================")
pprint.pprint(OptiTracker.descriptions['full'])
# ALso dump to file
with open("out/fulldesc.txt", 'w') as file:
    file.write("================================================")
    file.write("\nTest print of complete description of all models\n")
    file.write("================================================\n\n")
    pprint.pprint(OptiTracker.descriptions['full'], file)


with open("out/skel_data.txt", 'w') as file:
    file.write("================================================")
    file.write("\nTest print of 1s of frame data relating to hand skeleton\n")
    file.write("================================================\n\n")

record_for = 1
input(f"Press enter then get moving.\nWill record skeleton data for {record_for} second(s).")

# Record one second worth of frame data
wait_until = time.time() + 1
with open("out/skel_data.txt", 'a') as file:
    while time.time() < wait_until:
        pprint.pprint(OptiTracker.frame['skeletons'], file)
        file.write("\n\n")
        file.flush()


with open("out/rbdat.txt", 'w') as file:
    file.write("================================================")
    file.write("\nTest print of 1s of frame data")
    file.write("\nrelating to rigid bodies (i.e., hand & 'table')\n")
    file.write("================================================\n\n")

record_for = 1
input(f"Press enter then get moving.\nWill record rigid body data for {record_for} second(s).")

# Record one second worth of frame data
wait_until = time.time() + 1
with open("out/rb_data.txt", 'a') as file:
    while time.time() < wait_until:
        pprint.pprint(OptiTracker.frame['rigid_bodies'], file)
        file.write("\n\n")      
        file.flush()  



OptiTracker.stop_client()


# print(OptiTracker.frame['rigid_bodies']['rb_0']['pos'].x)



sys.exit()