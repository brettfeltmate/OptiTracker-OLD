import sys
import os
import time

from test_output import testOutput


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

tester = testOutput()

tester.init_client()

tester.start_client()

wait_until = time.time() + 0.1

while time.time() < wait_until:
    pass

tester.save_description()

tester.stop_client()

exit()