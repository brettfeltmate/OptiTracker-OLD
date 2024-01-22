class DataStructures:
    def __init__(self, motive_version = None) -> None:
        
        if motive_version is None:
            raise Exception("Motive version is not specified")
       
        self._motive_version = motive_version

        self.dtype = {
            "prefix":           self._set_prefix_dtype(),
            "marker":           self._set_marker_dtype(),
            "rigid_body":       self._set_rigid_body_dtype(),
            "skeleton":         self._set_skeleton_dtype(),
            "labeled_marker":   self._set_labeled_marker_dtype(),
            "force_plate":      self._set_force_plate_dtype(),
            "device":           self._set_device_dtype(),
            "suffix":           self._set_suffix_dtype()
        }


    def _set_prefix_dtype(self) -> None:
        if self._motive_version:
            pass
        pass

    def _set_marker_dtype(self) -> None:
        if self._motive_version:
            pass
        pass

    def _set_rigid_body_dtype(self) -> None:
        if self._motive_version:
            pass
        pass

    def _set_skeleton_dtype(self) -> None:
        if self._motive_version:
            pass
        pass

    def _set_labeled_marker_dtype(self) -> None:
        if self._motive_version:
            pass
        pass

    def _set_force_plate_dtype(self) -> None:
        if self._motive_version:
            pass
        pass

    def _set_device_dtype(self) -> None:
        if self._motive_version:
            pass
        pass

    def _set_suffix_dtype(self) -> None:
        if self._motive_version:
            pass
        pass

