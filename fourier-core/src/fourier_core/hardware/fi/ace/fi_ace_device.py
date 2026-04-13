class ACEInterfaceGroup:
    def __init__(self):
        self.device_map = {}
        self.subs_data_map = {}

    def add_device(self, server_ip, device):
        self.device_map[server_ip] = device

    def add_subs_data(self, server_ip, sub_data):
        self.subs_data_map[server_ip] = sub_data


# Singleton Object
gl_ace_intf_group = ACEInterfaceGroup()
