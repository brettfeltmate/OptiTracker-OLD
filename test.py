
# Get script directory to allow for relative imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# Imports
import sys
import os
import time
import pprint

# Import OptiTracker API wrapper class
from OptiTracker import OptiTracker

# Initialize OptiTracker
OptiTracker = OptiTracker()

# Initialize NatNetClient
OptiTracker.init_client()

# Duration of frame data recording, in seconds
record_duration= 0.1

# Wait until user is ready to start recording
input(f"Press enter then get moving.\nWill record frame data for {record_duration} second(s).")

# Start recording
record_until = time.time() + record_duration
OptiTracker.start_client()
while time.time() < record_until:
    pass

# Stop recording
OptiTracker.stop_client()

# Inform user that recording is complete
input("\n\nDone recording. Press enter to trigger writing.")

# Write descriptions to file
with open("out/skeleton_descriptions.txt", 'w') as file:
    file.write("==============================================================================")
    file.write("\NSKELETON DESCRIPTION." /
               "\n\nNote:\n" /
               "Skeletons are composed of rigid bodies (bones),\n" /
               "where each rigid body is itself a set of rigid body markers.\n\n" /
               "Rigid body pos's are (I think) interpolated 'midpoints' of marker positions.\n\n"
               )
    file.write("==============================================================================\n\n")
    pprint.pprint(OptiTracker.descriptions['skeletons'], file)


with open("out/rigid_body_descriptions.txt", 'w') as file:
    file.write("===========================================================================")
    file.write("\nRIGID BODY DESCRIPTIONS." /
               "\n\nNote:\n" /
               "Here, rigid bodies can either belong to skeletons,\n" /
               "or be their 'own' thing (in this case, the table)\n\n"
               "My hope was to be able to label the table corners (i.e, top-left)\n" /
               "as that've been handy, but neither the API or software allow for this.\n\n"
               )
    file.write("===========================================================================\n\n")
    pprint.pprint(OptiTracker.descriptions['rigid_bodies'], file)

# Write frame data to file
with open("out/skeleton_frame_data.txt", 'w') as file:
    file.write("==============================================================================")
    file.write("\n100ms SKELETON FRAME DATA." /
               "\n\nNote:\n" /
               "Frame number is top-level key to make it easy to find visually.\n" /
               "This is in no way necessary to keep going forward.\n\n"
               "Here, position & rotation of markers are stored as namedtuple objects\n" /
               "this was my doing, as it made data exploration easier, as Pos.x and Pos[0]\n" /
               "both return that marker's 'x' position. This can be changed going forward.\n\n"
                )
    file.write("==============================================================================\n\n")
    pprint.pprint(OptiTracker.frame['skeletons'], file)


with open("out/rigid_body_frame_data.txt", 'w') as file:
    file.write("==============================================================================")
    file.write("\n100ms RIGID BODY FRAME DATA." /
               "\n\nNote:\n" /
               "Frame number is top-level key to make it easy to find visually.\n" /
               "This is in no way necessary to keep going forward.\n\n"
               "Here, position & rotation of markers are stored as namedtuple objects\n" /
               "this was my doing, as it made data exploration easier, as Pos.x and Pos[0]\n" /
               "both return that marker's 'x' position. This can be changed going forward.\n\n"
                )
    file.write("==============================================================================\n\n")
    pprint.pprint(OptiTracker.frame['rigid_bodies'], file)

# Inform user that writing is complete
input("\n\nDone writing. Press enter to close script.") 

sys.exit()