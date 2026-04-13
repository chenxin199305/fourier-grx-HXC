from fourier_grx.comm.fi_dynalink_base import DynalinkBase


class DynalinkHardware(DynalinkBase):
    """
    Dynalink Hardware 模块，用于硬件模块的数据交互[单例模式]
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def _create_components(self):
        self.odl_io_status = None
        self.idl_io_status = None
        self.red_led_status = 0
        self.yellow_led_status = 0
        self.blue_led_status = 0
        self.emergent_stop_key_status = 0
        self.send_can_message = 0
        self.send_can_id = 0
        self.receive_can_message = 0
        self.receive_can_id = 0
        self.send_can_open_node_id = 0
        self.send_can_open_index = 0
        self.send_can_open_subindex = 0
        self.send_can_open_operation = 0
        self.send_can_open_byte = 0

        # --------------------------------------------------

        # 定义可读字段列表
        self.read_fields = [
            "odl_io_status",
            "idl_io_status",
            "red_led_status",
            "yellow_led_status",
            "blue_led_status",
            "emergent_stop_key_status",
            "send_can_id",
            "send_can_message",
            "receive_can_id",
            "receive_can_message",
            "send_can_open_node_id",
            "send_can_open_index",
            "send_can_open_subindex",
            "send_can_open_operation",
            "send_can_open_byte",
        ]

        # 定义可写字段列表
        self.write_fields = [
            "red_led_status",
            "yellow_led_status",
            "blue_led_status",
            "send_can_id",
            "send_can_message",
            "receive_can_id",
            "receive_can_message",
            "send_can_open_node_id",
            "send_can_open_index",
            "send_can_open_subindex",
            "send_can_open_operation",
            "send_can_open_byte",
        ]

        # 合并所有字段
        self.dict_fields = self.read_fields + self.write_fields
