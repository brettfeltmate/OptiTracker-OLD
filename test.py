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

# Record one second worth of frame data
wait_until = time.time() + 1
while time.time() < wait_until:
    pass

OptiTracker.stop_client()


print("\n\n================================")
print("Test print of full description\n================================")
pprint.pprint(OptiTracker.descriptions['full'])
# ALso dump to file
with open("out/fulldesc.txt", 'w') as file:
    file.write("================================================")
    file.write("\nTest print of complete description of all models\n")
    file.write("================================================\n\n")
    pprint.pprint(OptiTracker.descriptions['full'], file)

print("\n\n================================")
print("Test print of skeleton data\n================================")
pprint.pprint(OptiTracker.frame['skeletons'])
with open("out/skeldesc.txt", 'w') as file:
    file.write("================================================")
    file.write("\nTest print of 1s of frame data relating to hand skeleton\n")
    file.write("================================================\n\n")
    pprint.pprint(OptiTracker.frame['skeletons'], file)

print("\n\n================================")
print("Test print of rigid body data\n================================")
pprint.pprint(OptiTracker.frame['rigid_bodies'])
with open("out/rbdat.txt", 'w') as file:
    file.write("================================================")
    file.write("\nTest print of 1s of frame data relating to rigid bodies (i.e., hand & 'table')\n")
    file.write("================================================\n\n")
    pprint.pprint(OptiTracker.descriptions['full'], file)


# print(OptiTracker.frame['rigid_bodies']['rb_0']['pos'].x)



sys.exit()