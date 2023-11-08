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

# Give it a sec to make sure things get populated
# Almost certainly unnecessary.
wait_until = time.time() + 2
while time.time() < wait_until:
    pass

# Hopefully now each of these should point to their 
# corresponding descriptions and can be written to csv

OptiTracker.stop_client()

# for asset_type in ['rigid_bodies', 'skeletons', 'full']:
#     OptiTracker.save_description(asset_type)

# pprint.pprint(OptiTracker.descriptions['rigid_bodies'])
# print(f"\n\nsz_name: {OptiTracker.descriptions['rigid_bodies']['sz_name']}")


print("\n\n================================")
print("Test print of full description\n================================")
pprint.pprint(OptiTracker.descriptions['full'])
# ALso dump to file
with open("out/fulldesc.txt", 'w') as file:
    pprint.pprint(OptiTracker.descriptions['full'], file)

# for key in OptiTracker.descriptions['full'].keys():
#     pprint.pprint(vars(OptiTracker.descriptions['full'][key]))

print("\n\n================================")
print("Test print of skeleton data\n================================")
pprint.pprint(OptiTracker.frame['skeletons'])
with open("out/skeldesc.txt", 'w') as file:
    pprint.pprint(OptiTracker.descriptions['full'], file)
# for key in OptiTracker.frame['skeletons'].keys():
#     pprint.pprint(vars(OptiTracker.frame['skeletons'][key]))

print("\n\n================================")
print("Test print of rigid body data\n================================")
pprint.pprint(OptiTracker.frame['rigid_bodies'])
with open("out/rbdat.txt", 'w') as file:
    pprint.pprint(OptiTracker.descriptions['full'], file)
# for key in OptiTracker.frame['rigid_bodies'].keys():
#     pprint.pprint(vars(OptiTracker.frame['rigid_bodies'][key]))

print(OptiTracker.frame['rigid_bodies']['rb_0']['pos'].x)



sys.exit()