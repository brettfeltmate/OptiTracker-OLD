import sys
import os
import time

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

OptiTracker.dump_to_json("rigid_bodies")


sys.exit()