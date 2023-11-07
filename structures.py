import numpy as np

rb_marker_struct = np.dtype([
    ('marker_name', 'S256')
])


skeleton_struct = np.dtype([
    ('szName', 'S20'),
    ("skeletonID", 'i32'),
    ()

])