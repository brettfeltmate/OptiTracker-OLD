import sys
import os
import time

from OptiTracker import OptiTracker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

OptiTracker = OptiTracker()

OptiTracker.init_client()

OptiTracker.start_client()

wait_until = time.time() + 0.1

while time.time() < wait_until:
    pass

OptiTracker.save_description()

OptiTracker.stop_client()

exit()