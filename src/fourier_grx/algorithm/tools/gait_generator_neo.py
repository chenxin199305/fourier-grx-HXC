import torch


class FourierGaitGenerator:
    # state
    STATE_STAND = 1
    STATE_MOVE = 2
    STATE_WALK = 3
    STATE_RUN = 4

    """
    Jason 2024-07-25:
    The coupling_change_rate should be carefully tunned
    to make the curve change smoothly.
    """
    # coupling change rate
    COUPLING_CHANGE_RATE_INCREASE_BASE = 1.0  # 4.0
    COUPLING_CHANGE_RATE_DECREASE_BASE = 1.0  # 2.0

    def __init__(self,
                 num_envs,
                 num_feet,
                 phase_offset=None,
                 dt: float = 0.02,
                 frequency: float = (1.0 / 1.0),
                 reference_speed: float = 0.5,
                 device=None, ):
        """
        Fourier Gait Generator

        Inputs:
        :param num_envs: number of environments
        :param num_feet: number of feet
        :param phase_offset: phase offset of the oscillators. Range: [0, 2 * pi]
        :param dt: time step. Unit: second
        :param frequency: frequency of the oscillators. Unit: Hz
        :param reference_speed: reference speed. Unit: m/s
        :param device: device to run the code
        """
        self.num_envs = num_envs
        self.num_feet = num_feet

        self.device = "cuda:0" if device is None else device
        self.all_env_ids = torch.arange(num_envs, device=self.device)

        # states
        self.states = torch.zeros(self.num_envs, 1, dtype=torch.int, device=self.device)

        # time step
        self.dt = dt
        self.natural_frequency = frequency
        self.frequency = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device) * self.natural_frequency

        self.reference_speed = reference_speed

        # cycle radius
        self.cycle_r = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.cycle_r_max = 1.0
        self.cycle_r_min = 0.0001
        self.cycle_r_detection_threshold = 0.01

        # x, y of the oscillators
        self.x = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device) * self.cycle_r_max
        self.y = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device) * 0.0
        self.x_last = self.x.clone()
        self.y_last = self.y.clone()

        # decide the convergence rate of the oscillators
        # Jason 2024-07-24: [0.0, 10.0] is a good range
        self.rate_xy = 10.0

        # phase
        self.phase_rad = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.phase_rad_last = self.phase_rad.clone()
        self.phase_norm = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.phase_norm_last = self.phase_norm.clone()

        self.flag_phase_rollover = torch.zeros(self.num_envs, self.num_feet, dtype=torch.bool, device=self.device)

        # phase offset (different oscillators have different phase offset)
        # Jason 2024-07-24: must change the phase offset gradually, otherwise the oscillators will be unstable !!!
        self.phase_offset = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.phase_offset_target = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.phase_offset_change_rate = 0.01 * (self.dt / 0.001)
        self.set_phase_offset(phase_offset=phase_offset)

        # coupling change rate
        self.coupling_change_rate = \
            torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device) \
            * self.COUPLING_CHANGE_RATE_INCREASE_BASE
        self.coupling_change_rate_increase = self.COUPLING_CHANGE_RATE_INCREASE_BASE
        self.coupling_change_rate_decrease = self.COUPLING_CHANGE_RATE_DECREASE_BASE

        # map to the foot contact
        """
        Jason 2024-10-23:
        如果采样 dt 越大，则 threshold 需要设置的越大，因为振荡器的计算精度下降了。
        """
        self.contact_threshold = self.cycle_r_min * (2.0 + self.dt / 0.001)
        self.contact_ratio = 0.5 * torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.b: float = 1000.0  # decide precision of the contact_ratio, the higher, the more precise

        self.foot_contact = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.compulsory_contact = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.compulsory_swing = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)

        # mirror values
        self.mirror_index = torch.arange(num_feet - 1, -1, -1, device=self.device)

        self.mirror_x = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device) * self.cycle_r_max
        self.mirror_y = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device) * 0.0

        self.mirror_phase_rad = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.mirror_phase_norm = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)

        self.mirror_foot_contact = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.mirror_compulsory_contact = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.mirror_compulsory_swing = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)

        # ---------------------------------------------------------------

        # output value (select original values or mirror values)
        self.output_selection = torch.zeros(self.num_envs, 1, dtype=torch.int, device=self.device)

        # ---------------------------------------------------------------
        # Different Patterns
        num_feet_float = float(self.num_feet)

        walk_contact_ratio_biped_val = 0.666
        walk_contact_ratio_multi_val = 1 - 1 / num_feet_float

        run_contact_ratio_biped_val = 0.333
        run_contact_ratio_multi_val = 1 / num_feet_float

        t = min(1.0, max(0.0, (num_feet_float - 2.0) / 2.0))
        walk_contact_ratio = walk_contact_ratio_biped_val * (1 - t) + walk_contact_ratio_multi_val * t
        run_contact_ratio = run_contact_ratio_biped_val * (1 - t) + run_contact_ratio_multi_val * t

        self.pattern_params = {
            "stand": {
                "state": self.STATE_STAND,
                "frequency": self.natural_frequency,
                "cycle_r": self.cycle_r_min,
                # "phase_offset": torch.tensor([0.0] * self.num_feet, device=self.device),
                "phase_offset": -2 * torch.pi * torch.arange(self.num_feet, device=self.device) / self.num_feet,
                "contact_ratio": torch.tensor([0.500] * self.num_feet, device=self.device),
                "compulsory_contact": torch.tensor([0.0] * self.num_feet, device=self.device),
                "compulsory_swing": torch.tensor([0.0] * self.num_feet, device=self.device),
                "coupling_change_rate": self.coupling_change_rate_decrease,
            },
            "walk": {
                "state": self.STATE_WALK,
                "frequency": self.natural_frequency,
                "cycle_r": self.cycle_r_max,
                "phase_offset": -2 * torch.pi * torch.arange(self.num_feet, device=self.device) / self.num_feet,
                "contact_ratio": torch.tensor([walk_contact_ratio] * self.num_feet, device=self.device),
                "compulsory_contact": torch.tensor([0.0] * self.num_feet, device=self.device),
                "compulsory_swing": torch.tensor([0.0] * self.num_feet, device=self.device),
                "coupling_change_rate": self.coupling_change_rate_increase,
            },
            "run": {
                "state": self.STATE_RUN,
                "frequency": self.natural_frequency,
                "cycle_r": self.cycle_r_max,
                "phase_offset": -2 * torch.pi * torch.arange(self.num_feet, device=self.device) / self.num_feet,
                "contact_ratio": torch.tensor([run_contact_ratio] * self.num_feet, device=self.device),
                "compulsory_contact": torch.tensor([0.0] * self.num_feet, device=self.device),
                "compulsory_swing": torch.tensor([0.0] * self.num_feet, device=self.device),
                "coupling_change_rate": self.coupling_change_rate_increase,
            },
        }

        # ---------------------------------------------------------------
        # set stand pattern in the beginning
        self.set_pattern(pattern="stand")

    # ---------------------------------------------------------------

    def _gamma(self, y):
        """
        gamma function

        Ouput:
        - gamma: [num_envs, num_feet]
        """
        term1 = torch.pi / ((1 - self.contact_ratio) * (torch.exp(-self.b * y) + 1))
        term2 = torch.pi / ((0 + self.contact_ratio) * (torch.exp(self.b * y) + 1))
        gamma = term1 + term2
        return gamma

    def _coupling(self, norm=True):
        """
        Compute coupling between oscillators in a fully vectorized way (no Python loops).

        Returns:
            coupling_x: [num_envs, num_feet]
            coupling_y: [num_envs, num_feet]
        """
        # 1. phase difference between all oscillators: [E, F, F]
        phase_diff = self.phase_offset.unsqueeze(2) - self.phase_offset.unsqueeze(1)

        # 2. cos/sin of phase difference
        cos_diff = torch.cos(phase_diff)
        sin_diff = torch.sin(phase_diff)

        # 3. replicate x and y for broadcasting
        # x_j, y_j shape: [E, F, F], where axis 1 = i, axis 2 = j
        x_j = self.x.unsqueeze(1).expand(-1, self.num_feet, -1)
        y_j = self.y.unsqueeze(1).expand(-1, self.num_feet, -1)

        # 4. compute raw coupling
        coupling_x_ij = cos_diff * x_j - sin_diff * y_j
        coupling_y_ij = sin_diff * x_j + cos_diff * y_j

        # 5. mask out self-coupling (i == j)
        mask = 1 - torch.eye(self.num_feet, device=self.device).unsqueeze(0)  # [1, F, F]
        coupling_x_ij = coupling_x_ij * mask
        coupling_y_ij = coupling_y_ij * mask

        # 6. normalize coupling if needed
        if norm:
            r_i = torch.sqrt(self.x ** 2 + self.y ** 2).unsqueeze(2)  # [E, F, 1]
            r_j = torch.sqrt(self.x ** 2 + self.y ** 2).unsqueeze(1)  # [E, 1, F]
            coupling_x_ij = coupling_x_ij / (r_j + 1e-8) * r_i
            coupling_y_ij = coupling_y_ij / (r_j + 1e-8) * r_i

        # 7. sum over j to get total coupling for each i
        coupling_x = coupling_x_ij.sum(dim=2)  # [E, F]
        coupling_y = coupling_y_ij.sum(dim=2)  # [E, F]

        return coupling_x, coupling_y

    def _phase_change(self):
        """
        change the phase offset of the oscillators
        """
        phase_offset = self.phase_offset
        phase_offset_target = self.phase_offset_target
        phase_offset_change_rate = self.phase_offset_change_rate

        phase_offset = phase_offset + (phase_offset_target - phase_offset) * phase_offset_change_rate
        self.phase_offset = phase_offset

    def _cpg_hopf_oscillator(self):
        """
        Hopf oscillator differential equations
        """
        # record last x, y, phase for the coupling calculation
        self.x_last = self.x.clone()
        self.y_last = self.y.clone()
        self.phase_rad_last = self.phase_rad.clone()
        self.phase_norm_last = self.phase_norm.clone()

        # ---------------------------------------------------------------

        # Parameters for the Hopf oscillator
        r = torch.sqrt(self.x ** 2 + self.y ** 2)
        gamma = self._gamma(self.y)

        # extend frequency to [num_envs, num_feet]
        oscillator_frequency = self.frequency

        # alpha: Controls the rate of convergence to the limit cycle
        alpha = oscillator_frequency * self.rate_xy

        # omega: Natural frequency of the oscillator
        omega = oscillator_frequency * gamma

        # phase change
        self._phase_change()

        # coupling
        coupling_x, coupling_y = self._coupling(norm=True)

        # coupling_change_rate: the ratio of the coupling strength
        # Jason 2024-07-24: [0.0, 10.0] is a good range, lower than self.rate_xy
        # FIXME: more than 2 oscillators will have a problem
        # FIXME: too big coupling_change_rate will cause the oscillators to be unstable
        # FIXME: too big coupling_change_rate will cause the oscillators phase to move back when change
        # TODO: change this ratio from a experience value to a learnable parameter

        # Hopf oscillator differential equations
        dx = (alpha * (self.cycle_r ** 2 - r ** 2) * self.x - omega * self.y) \
             + self.coupling_change_rate * coupling_x
        dy = (alpha * (self.cycle_r ** 2 - r ** 2) * self.y + omega * self.x) \
             + self.coupling_change_rate * coupling_y

        # Euler method to update the state
        self.x += dx * self.dt
        self.y += dy * self.dt

        # ---------------------------------------------------------------

        # phase
        self.phase_rad = torch.atan2(self.y, self.x) % (2 * torch.pi)  # range: [0, 2 * pi]
        self.phase_norm = self.phase_rad / (2 * torch.pi)

        # phase rollover detection
        self.flag_phase_rollover = (self.phase_rad_last > torch.pi) & (self.phase_rad < torch.pi)

        # ---------------------------------------------------------------

        # change if needed
        r_now = torch.sqrt(self.x ** 2 + self.y ** 2)
        mask = self.flag_phase_rollover
        r_new = torch.where(mask, self.cycle_r, r_now)

        self.x = torch.where(mask, self.x * (r_new / (r_now + 1e-8)), self.x)
        self.y = torch.where(mask, self.y * (r_new / (r_now + 1e-8)), self.y)

        # ---------------------------------------------------------------

        # limit if needed (only for r < cycle_r_min)
        r_now = torch.sqrt(self.x ** 2 + self.y ** 2)
        mask = (r_now < self.cycle_r_min)
        r_new = torch.where(mask, self.cycle_r_min, r_now)

        self.x = torch.where(mask, self.x * (r_new / (r_now + 1e-8)), self.x)
        self.y = torch.where(mask, self.y * (r_new / (r_now + 1e-8)), self.y)

        # limit if needed (only for r > cycle_r_max)
        r_now = torch.sqrt(self.x ** 2 + self.y ** 2)
        mask = (r_now > self.cycle_r_max)
        r_new = torch.where(mask, self.cycle_r_max, r_now)

        self.x = torch.where(mask, self.x * (r_new / (r_now + 1e-8)), self.x)
        self.y = torch.where(mask, self.y * (r_new / (r_now + 1e-8)), self.y)

        # ---------------------------------------------------------------

        # phase
        self.phase_rad = torch.atan2(self.y, self.x) % (2 * torch.pi)  # range: [0, 2 * pi]
        self.phase_norm = self.phase_rad / (2 * torch.pi)

        # phase rollover detection
        self.flag_phase_rollover = (self.phase_rad_last > torch.pi) & (self.phase_rad < torch.pi)

        # ---------------------------------------------------------------

        # mirror values
        self.mirror_x = self.x[:, self.mirror_index]
        self.mirror_y = self.y[:, self.mirror_index]
        self.mirror_phase_rad = self.phase_rad[:, self.mirror_index]
        self.mirror_phase_norm = self.phase_norm[:, self.mirror_index]

        # ---------------------------------------------------------------

    # ====================================================================================================

    def reset(self, env_ids=None, randomize=False):
        """
        reset the state of the oscillator

        1. set phase
        2. calculate x, y
        3. add phase offset
        4. set x, y

        :param env_ids: [num_envs]
        :param randomize: whether to randomize the phase
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        self.set_phase_offset(env_ids=env_ids, phase_offset=self.phase_offset_target[env_ids])

        self.x[env_ids] = torch.cos(self.phase_offset_target[env_ids]) * self.cycle_r[env_ids]
        self.y[env_ids] = torch.sin(self.phase_offset_target[env_ids]) * self.cycle_r[env_ids]

        if randomize:
            rand_phase = torch.rand(size=env_ids.shape, device=self.device) * 2 * torch.pi
            rand_phase = rand_phase.unsqueeze(1).repeat(1, self.num_feet)

            self.x[env_ids] = torch.cos(rand_phase)
            self.y[env_ids] = torch.sin(rand_phase)

    def step(self, dt=None):
        if dt is not None:
            self.dt = dt

        self._cpg_hopf_oscillator()

    # ---------------------------------------------------------------

    def set_x(self, env_ids=None, x=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if x is None:
            x = torch.ones(env_ids.shape[0], self.num_feet, device=self.device) * self.cycle_r_max
        else:
            x = x

        self.x[env_ids] = x

    def set_y(self, env_ids=None, y=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if y is None:
            y = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            y = y

        self.y[env_ids] = y

    def set_frequency(self, env_ids=None, frequency=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if frequency is None:
            frequency = (1.0 / 1.0)
        else:
            frequency = frequency

        self.frequency[env_ids] = frequency

    def set_cycle_r(self, env_ids=None, cycle_r=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if cycle_r is None:
            cycle_r = torch.ones(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            cycle_r = cycle_r

        self.cycle_r[env_ids] = cycle_r

    def set_coupling_change_rate(self, env_ids=None, coupling_change_rate=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if coupling_change_rate is None:
            coupling_change_rate = torch.ones(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            coupling_change_rate = coupling_change_rate

        self.coupling_change_rate[env_ids] = coupling_change_rate

    def set_contact_ratio(self, env_ids=None, contact_ratio=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if contact_ratio is None:
            contact_ratio = 0.5 * torch.ones(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            contact_ratio = contact_ratio

        self.contact_ratio[env_ids] = contact_ratio

    def set_phase_offset(self, env_ids=None, phase_offset=None):
        """
        set the phase offset of the oscillators

        Inputs:
        - env_ids: [num_envs]
        - phase_offset: [num_envs, num_feet], range: [0, 2 * pi]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if phase_offset is None:
            phase_offset = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            phase_offset = phase_offset

        # update phase offset
        self.phase_offset_target[env_ids] = phase_offset

    def set_compulsory_contact(self, env_ids=None, compulsory_contact=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if compulsory_contact is None:
            compulsory_contact = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            compulsory_contact = compulsory_contact

        self.compulsory_contact[env_ids] = compulsory_contact

        self.mirror_compulsory_contact = self.compulsory_contact[:, self.mirror_index]

    def set_compulsory_swing(self, env_ids=None, compulsory_swing=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if compulsory_swing is None:
            compulsory_swing = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            compulsory_swing = compulsory_swing

        self.compulsory_swing[env_ids] = compulsory_swing

        self.mirror_compulsory_swing = self.compulsory_swing[:, self.mirror_index]

    # ---------------------------------------------------------------

    def get_frequency(self, env_ids=None):
        """
        Get the frequency of the oscillators

        Inputs:
        - env_ids: [num_envs], if None, get all environments
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        frequency = self.frequency[env_ids].clone()

        return frequency

    def get_frequency_norm(self, env_ids=None):
        """
        Get the normalized frequency of the oscillators

        Inputs:
        - env_ids: [num_envs], if None, get all environments
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        frequency_norm = (self.frequency[env_ids] - self.natural_frequency) / self.natural_frequency

        return frequency_norm.clone()

    def get_contact_ratio(self, env_ids=None):
        """
        Get the contact ratio of the oscillators

        Inputs:
        - env_ids: [num_envs], if None, get all environments
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        contact_ratio = self.contact_ratio[env_ids]

        return contact_ratio.clone()

    def get_contact_ratio_norm(self, env_ids=None):
        """
        Get the normalized contact ratio of the oscillators

        Inputs:
        - env_ids: [num_envs], if None, get all environments
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        contact_ratio_norm = (self.contact_ratio[env_ids] - 0.5) / 0.5

        return contact_ratio_norm.clone()

    # ====================================================================================================

    def set_pattern(
            self,
            pattern,
            env_ids=None,
            start_side_selection=None,
            frequency=None,
            contact_ratio=None,
            **kwargs,
    ):
        """
        Set the pattern of the oscillators

        Inputs:
        - pattern: one of the following:
            - 'stand'
            - 'walk'
            - 'run'
        - env_ids: [num_envs], if None, set all environments
        - start_side_selection: [num_envs], if None, use default selection
        - frequency: [num_envs, num_feet], if None, use default frequency
        - contact_ratio: [num_envs, num_feet], if None, use default contact ratio
        """

        env_ids = self.all_env_ids if env_ids is None else env_ids

        if pattern not in ["stand", "walk", "run"]:
            raise ValueError(f"Unknown pattern: {pattern}")

        if pattern in ["stand", "walk", "run"]:
            self.set_frequency(env_ids=env_ids, frequency=self.pattern_params[pattern]["frequency"])
            self.set_cycle_r(env_ids=env_ids, cycle_r=self.pattern_params[pattern]["cycle_r"])
            self.set_phase_offset(env_ids=env_ids, phase_offset=self.pattern_params[pattern]["phase_offset"])
            self.set_contact_ratio(env_ids=env_ids, contact_ratio=self.pattern_params[pattern]["contact_ratio"])
            self.set_compulsory_contact(env_ids=env_ids, compulsory_contact=self.pattern_params[pattern]["compulsory_contact"])
            self.set_compulsory_swing(env_ids=env_ids, compulsory_swing=self.pattern_params[pattern]["compulsory_swing"])
            self.set_coupling_change_rate(env_ids=env_ids, coupling_change_rate=self.pattern_params[pattern]["coupling_change_rate"])

        # customize frequency and contact_ratio if provided
        if pattern in ["walk", "run"]:
            self.from_stand_to_move(
                env_ids=env_ids,
                phase_offset=self.pattern_params[pattern]["phase_offset"],
                start_side_selection=start_side_selection,
            )

        if frequency is not None:
            # frequency: [num_envs, num_feet]
            self.set_frequency(env_ids=env_ids, frequency=frequency)

        if contact_ratio is not None:
            # contact_ratio: [num_envs, num_feet]
            self.set_contact_ratio(env_ids=env_ids, contact_ratio=contact_ratio)

        # Important: Change the state at last!!!
        self.states[env_ids] = self.pattern_params[pattern]["state"]

    def from_stand_to_move(
            self,
            env_ids=None,
            phase_offset=None,
            randomize_start_side=True,
            start_side_selection=None,
    ):
        """
        如果是从静止到运动，那么需要立即修改 x,y 到合适的值，
        否则由于站立的 phase_offset 给的是 0，会导致多条腿同时抬起

        Input Params:
        - env_ids: [num_envs]
        - phase_offset: [2], range: [0, 2 * pi]
        - randomize_start_side: bool, 是否随机选择左侧或右侧的腿踏步等运动模式
        - start_side_selection: [num_envs, 1], 如果不为 None，则使用该值作为输出选择
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids
        phase_offset = torch.zeros(self.num_feet, device=self.device) if phase_offset is None else phase_offset

        """
        Jason 2024-10-24:
        这里需要判断当前状态是否是站立状态，如果是站立状态，那么需要立即修改 x,y 到合适的值，
        否则不要去修改 x,y 的值，因为 x,y 的值是由 phase_offset 决定的，如果修改了 x,y 的值，那么 phase_offset 就没有意义了。

        这里比较容易出问题的是在 simulator 中，因为这个函数会被反复 call，所以需要保证只有在站立状态下才修改 x,y 的值。
        """
        indexes_of_stand_state = torch.where(self.states[env_ids] == self.STATE_STAND)[0]
        env_ids_of_stand_state = env_ids[torch.where(self.states[env_ids] == self.STATE_STAND)[0]]

        self.set_x(env_ids=env_ids_of_stand_state,
                   x=torch.ones(env_ids_of_stand_state.shape[0],
                                self.num_feet,
                                device=self.device)
                     * self.cycle_r_min
                     * torch.cos(phase_offset))
        self.set_y(env_ids=env_ids_of_stand_state,
                   y=torch.zeros(env_ids_of_stand_state.shape[0],
                                 self.num_feet,
                                 device=self.device))

        """
        Jason 2024-12-25:
        随机设置 output_selection, 可以防止机器人启动的时候只使用一侧的腿启动踏步，容易形成非 mirror 的 policy
        """
        if start_side_selection is not None:
            # 如果提供了 start_side_selection，则使用该值作为输出选择
            output_selection = start_side_selection[indexes_of_stand_state]
        elif randomize_start_side:
            # 随机选择左侧或右侧的腿踏步等运动模式
            output_selection = torch.randint(low=0,
                                             high=2,
                                             size=(env_ids_of_stand_state.shape[0], 1),
                                             dtype=torch.int,
                                             device=self.device)
        else:
            # 默认使用左侧的腿踏步等运动模式
            output_selection = None

        self.set_output_selection(env_ids=env_ids_of_stand_state,
                                  output_selection=output_selection)

    # ====================================================================================================

    def get_stand_pattern_env_ids(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_STAND)[0]]

        return env_ids

    def get_walk_pattern_env_ids(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_WALK)[0]]

        return env_ids

    def get_run_pattern_env_ids(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_RUN)[0]]

        return env_ids

    # ====================================================================================================
    # Original Values

    def get_x(self, env_ids=None):
        """
        get the x value of the oscillators

        return:
        x: [num_envs, num_feet]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        x = self.x[env_ids]

        return x.clone()

    def get_y(self, env_ids=None):
        """
        get the y value of the oscillators

        return:
        y: [num_envs, num_feet]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        y = self.y[env_ids]

        return y.clone()

    def get_phase_rad(self, env_ids=None):
        """
        get the phase of the oscillators

        return:
        phase: [num_envs, num_feet], range: [0, 2 * pi]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        phase_rad = self.phase_rad[env_ids]

        return phase_rad.clone()

    def get_x_norm(self, env_ids=None):
        """
        get the normalized x value of the oscillators

        return:
        x_norm: [num_envs, num_feet], range: [-1, 1]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        r_env_ids = torch.sqrt(self.x ** 2 + self.y ** 2)
        x_norm = torch.where(r_env_ids > self.cycle_r_detection_threshold, self.x, 0)
        x_norm = x_norm[env_ids]

        return x_norm.clone()

    def get_y_norm(self, env_ids=None):
        """
        get the normalized y value of the oscillators

        return:
        y_norm: [num_envs, num_feet], range: [-1, 1]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        r_env_ids = torch.sqrt(self.x ** 2 + self.y ** 2)
        y_norm = torch.where(r_env_ids > self.cycle_r_detection_threshold, self.y, 0)
        y_norm = y_norm[env_ids]

        return y_norm.clone()

    def get_phase_norm(self, env_ids=None):
        """
        get the normalized phase of the oscillators

        return:
        phase_norm: [num_envs, num_feet], range: [0, 1]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        phase_norm = self.phase_norm[env_ids]

        return phase_norm.clone()

    def get_foot_contact(self, env_ids=None) -> torch.Tensor:
        """
        get the foot contact situation
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        # situation 1: when in move state, y < contact_threshold
        flags_of_foot_contact_s1 = (self.y <= self.contact_threshold).int()

        # situation 2: force setting the foot contact situation
        flags_of_foot_contact_s2 = self.get_compulsory_contact()

        # situation 3: force setting the foot swing situation
        flags_of_foot_contact_s3 = self.get_compulsory_swing()

        # foot contact situation
        temp_foot_contact = (flags_of_foot_contact_s1
                             + flags_of_foot_contact_s2) \
                            * (1 - flags_of_foot_contact_s3)

        self.foot_contact = torch.clip(temp_foot_contact, 0, 1)

        foot_contact = self.foot_contact[env_ids]

        return foot_contact.clone()

    def get_compulsory_contact(self, env_ids=None) -> torch.Tensor:
        """
        get the foot contact situation
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        compulsory_contact = self.compulsory_contact[env_ids]

        return compulsory_contact.clone()

    def get_compulsory_swing(self, env_ids=None) -> torch.Tensor:
        """
        get the foot swing situation
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        compulsory_swing = self.compulsory_swing[env_ids]

        return compulsory_swing.clone()

    # ====================================================================================================
    # Mirror Values

    def get_mirror_x(self, env_ids=None):
        """
        get the mirror x value of the oscillators

        return:
        x: [num_envs, num_feet]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        mirror_x = self.mirror_x[env_ids]

        return mirror_x.clone()

    def get_mirror_y(self, env_ids=None):
        """
        get the mirror y value of the oscillators

        return:
        y: [num_envs, num_feet]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        mirror_y = self.mirror_y[env_ids]

        return mirror_y.clone()

    def get_mirror_phase_rad(self, env_ids=None):
        """
        get the mirror phase of the oscillators

        return:
        phase: [num_envs, num_feet], range: [0, 2 * pi]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        phase_rad = self.mirror_phase_rad[env_ids]

        return phase_rad.clone()

    def get_mirror_x_norm(self, env_ids=None):
        """
        get the normalized mirror x value of the oscillators

        return:
        x_norm: [num_envs, num_feet], range: [-1, 1]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        r_env_ids = torch.sqrt(self.mirror_x ** 2 + self.mirror_y ** 2)
        mirror_x_norm = torch.where(r_env_ids > self.cycle_r_detection_threshold, self.mirror_x, 0)
        mirror_x_norm = mirror_x_norm[env_ids]

        return mirror_x_norm.clone()

    def get_mirror_y_norm(self, env_ids=None):
        """
        get the normalized mirror y value of the oscillators

        return:
        y_norm: [num_envs, num_feet], range: [-1, 1]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        r_env_ids = torch.sqrt(self.mirror_x ** 2 + self.mirror_y ** 2)
        mirror_y_norm = torch.where(r_env_ids > self.cycle_r_detection_threshold, self.mirror_y, 0)
        mirror_y_norm = mirror_y_norm[env_ids]

        return mirror_y_norm.clone()

    def get_mirror_phase_norm(self, env_ids=None):
        """
        get the normalized mirror phase of the oscillators

        return:
        phase_norm: [num_envs, num_feet], range: [0, 1]
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        mirror_phase_norm = self.mirror_phase_norm[env_ids]

        return mirror_phase_norm.clone()

    def get_mirror_foot_contact(self, env_ids=None) -> torch.Tensor:
        """
        get the foot contact situation
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        # situation 1: when in move state, y < contact_threshold
        flags_of_foot_contact_s1 = (self.mirror_y <= self.contact_threshold).int()

        # situation 2: force setting the foot contact situation
        flags_of_foot_contact_s2 = self.get_mirror_compulsory_contact()

        # situation 3: force setting the foot swing situation
        flags_of_foot_contact_s3 = self.get_mirror_compulsory_swing()

        # foot contact situation
        temp_foot_contact = (flags_of_foot_contact_s1
                             + flags_of_foot_contact_s2) \
                            * (1 - flags_of_foot_contact_s3)

        self.mirror_foot_contact = torch.clip(temp_foot_contact, 0, 1)

        mirror_foot_contact = self.mirror_foot_contact[env_ids]

        return mirror_foot_contact.clone()

    def get_mirror_compulsory_contact(self, env_ids=None) -> torch.Tensor:
        """
        get the foot contact situation
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        mirror_compulsory_contact = self.mirror_compulsory_contact[env_ids]

        return mirror_compulsory_contact.clone()

    def get_mirror_compulsory_swing(self, env_ids=None) -> torch.Tensor:
        """
        get the foot swing situation
        """
        env_ids = self.all_env_ids if env_ids is None else env_ids

        mirror_compulsory_swing = self.mirror_compulsory_swing[env_ids]

        return mirror_compulsory_swing.clone()

    # ====================================================================================================
    # Output Values

    def set_output_selection(self, env_ids=None, output_selection=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        if output_selection is None:
            output_selection = torch.zeros(env_ids.shape[0], 1, dtype=torch.int, device=self.device)
        else:
            output_selection = output_selection

        self.output_selection[env_ids] = output_selection

    def get_output_x(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        output_x = torch.where(self.output_selection == 0, self.x, self.mirror_x)
        output_x = output_x[env_ids]

        return output_x.clone()

    def get_output_y(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        output_y = torch.where(self.output_selection == 0, self.y, self.mirror_y)
        output_y = output_y[env_ids]

        return output_y.clone()

    def get_output_phase_rad(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        output_phase_rad = torch.where(self.output_selection == 0, self.get_phase_rad(), self.get_mirror_phase_rad())
        output_phase_rad = output_phase_rad[env_ids]

        return output_phase_rad.clone()

    def get_output_x_norm(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        output_x_norm = torch.where(self.output_selection == 0, self.get_x_norm(), self.get_mirror_x_norm())
        output_x_norm = output_x_norm[env_ids]

        return output_x_norm.clone()

    def get_output_y_norm(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        output_y_norm = torch.where(self.output_selection == 0, self.get_y_norm(), self.get_mirror_y_norm())
        output_y_norm = output_y_norm[env_ids]

        return output_y_norm.clone()

    def get_output_phase_norm(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        output_phase_norm = torch.where(self.output_selection == 0, self.get_phase_norm(), self.get_mirror_phase_norm())
        output_phase_norm = output_phase_norm[env_ids]

        return output_phase_norm.clone()

    def get_output_foot_contact(self, env_ids=None):
        env_ids = self.all_env_ids if env_ids is None else env_ids

        output_foot_contact = torch.where(self.output_selection == 0, self.get_foot_contact(), self.get_mirror_foot_contact())
        output_foot_contact = output_foot_contact[env_ids]

        return output_foot_contact.clone()

    def get_output_foot_swing(self, env_ids=None):
        """
        get the foot swing situation
        """
        output_foot_contact = self.get_output_foot_contact(env_ids=env_ids)
        output_foot_swing = 1 - output_foot_contact

        return output_foot_swing.clone()


# ====================================================================================================


if __name__ == "__main__":
    import matplotlib

    matplotlib.use("Qt5Agg")  # 或 QtAgg

    import matplotlib.pyplot as plt
    import random

    T = random.randint(15, 15)
    dt = 0.02
    time = range(int(T / dt))

    x_list = []
    y_list = []
    phase_list = []
    foot_contact_list = []
    phase_rollover_list = []

    mirror_x_list = []
    mirror_y_list = []
    mirror_phase_list = []
    mirror_foot_contact_list = []

    output_x_list = []
    output_y_list = []
    output_phase_list = []
    output_foot_contact_list = []

    num_envs = 1
    num_feet = 4
    gait_cycle_period = 1.6
    env_ids = torch.arange(num_envs, device="cpu")

    gait_generator = FourierGaitGenerator(
        num_envs=num_envs,
        num_feet=num_feet,
        dt=dt,
        frequency=(1.0 / gait_cycle_period),
        device="cpu")

    gait_generator.reset(env_ids=env_ids, randomize=False)

    print(
        f"env_ids = {env_ids}"
    )

    for i in time:
        if i == len(time) // 9 * 0:
            gait_generator.set_pattern(
                pattern="stand",
                env_ids=env_ids,
            )

        if i == len(time) // 9 * 2:
            gait_generator.set_pattern(
                pattern="walk",
                env_ids=env_ids,
                start_side_selection=torch.tensor([[0]], dtype=torch.int, device="cpu"),
            )

        if i == len(time) // 9 * 4:
            gait_generator.set_pattern(
                pattern="stand",
                env_ids=env_ids,
            )

        if i == len(time) // 9 * 6:
            gait_generator.set_pattern(
                pattern="run",
                env_ids=env_ids,
                start_side_selection=torch.tensor([[1]], dtype=torch.int, device="cpu"),
                frequency=torch.tensor([[1.0 / gait_cycle_period]], dtype=torch.float, device="cpu"),
                contact_ratio=torch.tensor([[0.3] * num_feet], dtype=torch.float, device="cpu"),
            )

        if i == len(time) // 9 * 8:
            gait_generator.set_pattern(
                pattern="stand",
                env_ids=env_ids,
            )

        gait_generator.step()

        # get original values
        x = gait_generator.get_x_norm()
        y = gait_generator.get_y_norm()
        phase = gait_generator.get_phase_norm()
        foot_contact = gait_generator.get_foot_contact()
        phase_rollover = gait_generator.flag_phase_rollover

        # get mirror values
        mirror_x = gait_generator.get_mirror_x_norm()
        mirror_y = gait_generator.get_mirror_y_norm()
        mirror_phase = gait_generator.get_mirror_phase_norm()
        mirror_foot_contact = gait_generator.get_mirror_foot_contact()

        # get output values
        output_x = gait_generator.get_output_x_norm()
        output_y = gait_generator.get_output_y_norm()
        output_phase = gait_generator.get_output_phase_norm()
        output_foot_contact = gait_generator.get_output_foot_contact()

        # add to list
        x_list.append(x)
        y_list.append(y)
        phase_list.append(phase)
        foot_contact_list.append(foot_contact)
        phase_rollover_list.append(phase_rollover)

        mirror_x_list.append(mirror_x)
        mirror_y_list.append(mirror_y)
        mirror_phase_list.append(mirror_phase)
        mirror_foot_contact_list.append(mirror_foot_contact)

        output_x_list.append(output_x)
        output_y_list.append(output_y)
        output_phase_list.append(output_phase)
        output_foot_contact_list.append(output_foot_contact)

    x_list = torch.stack(x_list).squeeze().detach().numpy()
    y_list = torch.stack(y_list).squeeze().detach().numpy()
    phase_list = torch.stack(phase_list).squeeze().detach().numpy()
    contact_list = torch.stack(foot_contact_list).squeeze().detach().numpy()
    phase_rollover_list = torch.stack(phase_rollover_list).squeeze().detach().numpy()

    mirror_x_list = torch.stack(mirror_x_list).squeeze().detach().numpy()
    mirror_y_list = torch.stack(mirror_y_list).squeeze().detach().numpy()
    mirror_phase_list = torch.stack(mirror_phase_list).squeeze().detach().numpy()
    mirror_contact_list = torch.stack(mirror_foot_contact_list).squeeze().detach().numpy()

    output_x_list = torch.stack(output_x_list).squeeze().detach().numpy()
    output_y_list = torch.stack(output_y_list).squeeze().detach().numpy()
    output_phase_list = torch.stack(output_phase_list).squeeze().detach().numpy()
    output_foot_contact_list = torch.stack(output_foot_contact_list).squeeze().detach().numpy()

    # subplots
    fig, axs = plt.subplots(5, 2, figsize=(12, 6))
    axs[0, 0].plot(time, x_list, label='x')
    axs[0, 0].legend()
    axs[1, 0].plot(time, y_list, label='y')
    axs[1, 0].legend()
    axs[2, 0].plot(time, phase_list, label='phase')
    axs[2, 0].legend()
    axs[3, 0].plot(time, contact_list, label='contact')
    axs[3, 0].legend()
    axs[4, 0].plot(time, phase_rollover_list, label='phase_rollover')
    axs[4, 0].legend()

    axs[0, 1].plot(time, mirror_x_list, label='mirror_x')
    axs[0, 1].legend()
    axs[1, 1].plot(time, mirror_y_list, label='mirror_y')
    axs[1, 1].legend()
    axs[2, 1].plot(time, mirror_phase_list, label='mirror_phase')
    axs[2, 1].legend()
    axs[3, 1].plot(time, mirror_contact_list, label='mirror_contact')
    axs[3, 1].legend()
    #
    # axs[0, 2].plot(time, output_x_list, label='output_x')
    # axs[0, 2].legend()
    # axs[1, 2].plot(time, output_y_list, label='output_y')
    # axs[1, 2].legend()
    # axs[2, 2].plot(time, output_phase_list, label='output_phase')
    # axs[2, 2].legend()
    # axs[3, 2].plot(time, output_foot_contact_list, label='output_contact')
    # axs[3, 2].legend()

    plt.xlabel('Time')
    plt.ylabel('x')
    plt.grid(True)
    plt.show()
