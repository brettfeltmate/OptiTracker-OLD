import sys
import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# Import MoCap interface
from Resources.API.Official.PythonClient import NatNetClient

