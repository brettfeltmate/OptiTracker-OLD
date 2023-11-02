from NatNetClient import NatNetClient


class OptiTracker:
    def __init__(self) -> None:
        self.client = self.init_client()


    # Create NatNetClient instance
    def init_client(self,
            server="127.0.0.1", multicast="239.255.42.99",
            commandPort=1510, dataPort=1511,
            motiveVersion=(3,0,1,0), verbose=False,
            uses_skeleton_listener=False,
            uses_rigid_body_listener=False,
            uses_marker_set_listener=False,
            uses_frame_listener=True) -> object:
        
        # Spawn client
        client = NatNetClient(
            server=server, multicast=multicast,
            commandPort=commandPort, dataPort=dataPort,
            motiveVersion=motiveVersion, verbose=verbose
        )

        # Activate requested listeners by assinging them to client
        # Active listener functions get called on every frame
        if uses_skeleton_listener:
            client.skeletonListener = self.skeleton_listener
        
        if uses_rigid_body_listener:
            client.rigidBodyListener = self.rigid_body_listener

        if uses_marker_set_listener:
            client.markerSetListener = self.marker_set_listener

        if uses_frame_listener:
            client.newFrameListener = self.frame_listener

        # Activate client
        # TODO: How best to inform user if client setup fails?
        client.run()

        return client
    
    # Returns summary description of all active assets
    # Called once when initing.
    def get_asset_descriptions(self) -> dict:
        pass
    
    # When active, records frame-data of all active assets
    # Activated by default, called once per frame-rate
    def frame_listener(self) -> None:
        pass

    # When active, records frame-data of all active skeleton assets
    # Deactivated by default, called once per frame-rate
    def skeleton_listener(self) -> None:
        pass

    # When active, records frame-data of all active rigid body assets
    # Deactivated by default, called once per frame-rate
    def rigid_body_listener(self) -> None:
        pass

    # When active, records frame-data of all active markerset assets 
    # Deactivated by default, called once per frame-rate
    def marker_set_listener(self) -> None:
        pass
    






