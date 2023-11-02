from NatNetClient import NatNetClient


class OptiTracker:
    def __init__(self) -> None:
        pass

    def init_client(self, 
            server_address = "127.0.0.1", multicast_address = "239.255.42.99",
            command_port = 1510, data_port = 1511,
            asset_listener = None, frame_listener = None,
            motive_version = (3,0,1,0), verbose = False):
        
        # IP address of NatNet server
        self.server_address = server_address

        # Must match multicast address listed in Motive's streaming settings
        self.multicast_address = multicast_address

        # NatNet command port
        self.command_port = command_port

        # NatNet data port
        self.data_port = data_port

        


