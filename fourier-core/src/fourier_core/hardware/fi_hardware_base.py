from .fi_hardware_predefine import FunctionResult


class HardwareBase:
    def __init__(self):

        self.__attr_loaded = False

        # Hardware info
        self.serial_number = 0

        # Hardware init flags
        self.flag_use_clock = False
        self.flag_use_adc = False
        self.flag_use_gpio = False
        self.flag_use_flash = False
        self.flag_use_can = False
        self.flag_use_ethernet = False
        self.flag_use_spi = False
        self.flag_use_uart = False

    def __getattr__(self, item):
        """
        Delegate unknown attributes/methods to return FunctionResult.NOT_IMPLEMENTED
        """
        # Lazy load attributes if not already loaded
        self._load_attr()

        return self._get_attr(item)

    # -------------------------------------------------------------------------

    def _load_attr(self) -> FunctionResult:
        if not self.__attr_loaded:
            print(
                f"HardwareBase.__load_attr: self={self}"
            )
            self.__attr_loaded = True

        return FunctionResult.SUCCESS

    def _get_attr(self, item):
        return lambda *args, **kwargs: FunctionResult.NOT_IMPLEMENTED

    # -------------------------------------------------------------------------

    def init(self) -> FunctionResult:

        if self.flag_use_clock:
            if not self.clock_init() == FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        if self.flag_use_adc:
            if not self.adc_init() == FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        if self.flag_use_gpio:
            if not self.gpio_init() == FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        if self.flag_use_flash:
            if not self.flash_init() == FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        if self.flag_use_can:
            if not self.can_init() == FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        if self.flag_use_ethernet:
            if not self.ethernet_init() == FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        if self.flag_use_spi:
            if not self.spi_init() == FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        if self.flag_use_uart:
            if not self.uart_init() == FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def clock_init(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def adc_init(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def gpio_init(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def flash_init(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def can_init(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def ethernet_init(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def spi_init(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def uart_init(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    # -------------------------------------------------------------------------
