from fourier_grx.comm.fi_dynalink_base import DynalinkBase


class DynalinkError(DynalinkBase):
    """
    Dynalink Error 模块，用于错误模块的数据交互[单例模式]
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def _create_components(self):
        self.error_code = 0

        # dc bus error code (0~2)
        self.dc_bus_over_voltage = 0
        self.dc_bus_under_voltage = 0
        self.dc_bus_short_circuit = 0

        # motor error code
        self.motor_over_voltage = 0
        self.motor_over_current = 0
        self.motor_over_temperature = 0
        self.motor_over_load = 0
        self.motor_positive_limit = 0
        self.motor_negative_limit = 0
        self.motor_phase_error = 0
        self.motor_backup_bit = 0

        # driver、sensor、actuator error code
        self.dsa_over_temperature = 0
        self.dsa_under_voltage = 0
        self.dsa_tracking_error = 0
        self.dsa_encoder_error = 0
        self.dsa_sto_error = 0
        self.dsa_data_read_error = 0
        self.dsa_data_write_error = 0
        self.dsa_backup_bit = 0

        # communication error code
        self.communication_can_error = 0
        self.communication_ethernet_error = 0
        self.communication_backup_bit = 0

        # other error code
        self.other_error = 0

        # node id
        self.node_id = 0

        # --------------------------------------------------

        # 定义可读字段列表
        self.read_fields = [
            "error_code",
            "dc_bus_over_voltage",
            "dc_bus_under_voltage",
            "dc_bus_short_circuit",
            "motor_over_voltage",
            "motor_over_current",
            "motor_over_temperature",
            "motor_over_load",
            "motor_positive_limit",
            "motor_negative_limit",
            "motor_phase_error",
            "motor_backup_bit",
            "dsa_over_temperature",
            "dsa_under_voltage",
            "dsa_tracking_error",
            "dsa_encoder_error",
            "dsa_sto_error",
            "dsa_data_read_error",
            "dsa_data_write_error",
            "dsa_backup_bit",
            "communication_can_error",
            "communication_ethernet_error",
            "communication_backup_bit",
            "other_error",
            "node_id",
        ]

        # 定义可写字段列表
        self.write_fields = [
        ]

        # 定义所有字段列表
        self.dict_fields = self.read_fields + self.write_fields
