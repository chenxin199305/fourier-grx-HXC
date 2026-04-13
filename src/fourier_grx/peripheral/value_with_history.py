class ValueWithHistory:
    def __init__(
            self,
            init_value=0,
            alpha=0.1,
    ):
        self.current = init_value
        self.last = init_value

        # 低通滤波系数
        self.alpha = alpha
        self.filtered = init_value

    def update(self, value=None):
        if value is None:
            return

        self.last = self.current
        self.current = value

        # 低通滤波
        self.filtered = self.current

        # TODO: add low pass filter function
        # FIXME: can not fit with tuple input value
        # self.filtered = self.alpha * self.current + (1 - self.alpha) * self.filtered

    def get(self):
        return self.current

    def get_last(self):
        return self.last

    def get_filtered(self):
        return self.filtered

    def __call__(self):
        return self.get()

    def __bool__(self):
        return bool(self.current)

    def __int__(self):
        return int(self.current)

    def __float__(self):
        return float(self.current)
