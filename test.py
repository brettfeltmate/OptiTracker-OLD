import sys
import os
import time

from OptiTracker import OptiTracker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

OptiTracker = OptiTracker()

OptiTracker.init_client()

if OptiTracker.start_client():

    # Give it a sec to make sure things get populated
    # Almost certainly unnecessary.
    wait_until = time.time() + 0.5
    while time.time() < wait_until:
        pass

    # Hopefully now each of these should point to their 
    # corresponding descriptions and can be written to csv
    for asset_type in ['rigid_bodies', 'skeletons', 'full']:
        OptiTracker.save_description(asset_type)

    OptiTracker.stop_client()

else:
    print("Client failed to start.")

sys.exit()