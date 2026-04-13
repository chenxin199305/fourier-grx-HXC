import math
import numpy
import torch


class FourierGaitGenerator:
    # state
    STATE_OFF = 0
    STATE_STAND = 1
    STATE_MOVE = 2
    STATE_WALK = 3
    STATE_RUN = 4
    STATE_JUMP = 5
    STATE_HOP = 6
    STATE_RUN_FAST = 7

    # foot height type
    FOOT_HEIGHT_TYPE_LINEAR = 0
    FOOT_HEIGHT_TYPE_SMOOTH = 1
    FOOT_HEIGHT_TYPE_MIXED = 2
    FOOT_HEIGHT_TYPE_NATURAL = 3

    """
    Jason 2024-07-25:
    The coupling_change_rate and amplitude_change_rate should be carefully tunned
    to make the curve change smoothly.
    """
    # coupling change rate
    COUPLING_CHANGE_RATE_INCREASE_BASE = 4.0
    COUPLING_CHANGE_RATE_DECREASE_BASE = 2.0

    # amplitude change rate
    AMPLITUDE_CHANGE_RATE_INCREASE_BASE = 1.05
    AMPLITUDE_CHANGE_RATE_DECREASE_BASE = 0.995

    # swing middle type
    SWING_MIDDLE_TYPE_LINEAR = 0
    SWING_MIDDLE_TYPE_ACCURATE = 1

    def __init__(self,
                 num_envs,
                 num_feet,
                 phase_offset=None,
                 dt: float = 0.02,
                 frequency: float = (1.0 / 1.0),
                 reference_speed: float = 0.5,
                 foot_height_target: float = 0.10,
                 shoulder_swing_target: float = math.radians(15.0),
                 device=None, ):
        """
        Fourier Gait Generator

        Inputs:
        - num_envs: number of environments
        - num_feet: number of feet
        - phase_offset: phase offset of the oscillators. Range: [0, 2 * pi]
        - dt: time step. Unit: second
        - frequency: frequency of the oscillators. Unit: Hz
        - reference_speed: reference speed. Unit: m/s
        - foot_height_target: target foot height. Unit: meter
        - shoulder_swing_target: target shoulder swing. Unit: radian
        - device: device to run the code
        """
        self.num_envs = num_envs
        self.num_feet = num_feet
        if device is None:
            self.device = "cuda:0"
        else:
            self.device = device

        # states
        self.states = torch.zeros(self.num_envs, dtype=torch.int, device=self.device)

        # time step
        self.dt = dt
        self.frequency = torch.ones(self.num_envs, dtype=torch.float, device=self.device) \
                         * frequency

        self.reference_speed = reference_speed

        # cycle radius
        self.cycle_r = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.cycle_r_max = 1.0
        self.cycle_r_min = 0.001

        # x, y of the oscillators
        self.x = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device) \
                 * self.cycle_r_max
        self.y = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)

        # mirror values
        self.mirror_x = torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device) \
                        * self.cycle_r_max
        self.mirror_y = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)

        # decide the convergence rate of the oscillators
        # Jason 2024-07-24: [0.0, 10.0] is a good range
        self.rate_xy = 10.0

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
        self.coupling_change_rate_increase = \
            self.COUPLING_CHANGE_RATE_INCREASE_BASE
        self.coupling_change_rate_decrease = \
            self.COUPLING_CHANGE_RATE_DECREASE_BASE

        # Note: related to dt !!! The smaller the dt, the smaller the amplitude_change_rate !!!
        # compared to increase_ratio in 0.001 second
        self.amplitude_change_rate = \
            torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.amplitude_change_rate_increase = \
            self.AMPLITUDE_CHANGE_RATE_INCREASE_BASE ** (self.dt / 0.001)
        self.amplitude_change_rate_decrease = \
            self.AMPLITUDE_CHANGE_RATE_DECREASE_BASE ** (self.dt / 0.001)

        # map to the foot contact
        """
        Jason 2024-10-23:
        如果采样 dt 越大，则 threshold 需要设置的越大，因为振荡器的计算精度下降了。
        """
        self.contact_threshold = self.cycle_r_min * (2.0 + self.dt / 0.001)
        self.contact_ratio = 0.5 * torch.ones(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.b: float = 1000.0  # decide precision of the contact_ratio, the higher, the more precise

        self.foot_contact = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.force_contact = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.force_swing = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)

        self.mirror_foot_contact = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.mirror_force_contact = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.mirror_force_swing = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)

        # map to the foot height
        """
        Jason 2024-10-23:
        如果采样 dt 越大，则 threshold 需要设置的越大，因为振荡器的计算精度下降了。
        """
        self.foot_height_threshold = self.cycle_r_min * 1.0
        self.foot_height = 0.0
        self.foot_height_target = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.foot_height_type = torch.zeros(self.num_envs, self.num_feet, dtype=torch.int, device=self.device)
        self.foot_height_change_rate = 0.1 * (self.dt / 0.001)
        self.set_foot_height(foot_height=foot_height_target)

        self.mirror_foot_height = 0.0

        # map to shoulder swing
        """
        Jason 2024-10-23:
        如果采样 dt 越大，则 threshold 需要设置的越大，因为振荡器的计算精度下降了。
        """
        self.shoulder_swing_threshold = self.cycle_r_min * 1.0
        self.shoulder_swing = 0.0
        self.shoulder_swing_target = torch.zeros(self.num_envs, self.num_feet, dtype=torch.float, device=self.device)
        self.set_shoulder_swing(shoulder_swing=shoulder_swing_target)

        # phase diff for stand state
        self.phase_diff_threshold_for_stand = 1 / 4
        self.phase_diff = 0.0

        self.mirror_phase_diff = 0.0

        # ---------------------------------------------------------------

        # output value (select original values or mirror values)
        self.output_selection = torch.zeros(self.num_envs, 1, dtype=torch.int, device=self.device)

        # ---------------------------------------------------------------
        # Different Patterns
        self.frequency_off = frequency
        self.frequency_stand = frequency
        self.frequency_walk = frequency
        self.frequency_run = frequency * 1.25
        self.frequency_run_fast = frequency * 1.25
        self.frequency_jump = frequency * 0.75
        self.frequency_hop = frequency * 1.25

        self.phase_offset_off = torch.tensor([0.0, 0.0], device=self.device)
        self.phase_offset_stand = torch.tensor([0.0, 0.0], device=self.device)
        self.phase_offset_walk = torch.tensor([0.0, -torch.pi], device=self.device)
        self.phase_offset_run = torch.tensor([0.0, -torch.pi], device=self.device)
        self.phase_offset_run_fast = torch.tensor([0.0, -torch.pi], device=self.device)
        self.phase_offset_jump = torch.tensor([0.0, 0.0], device=self.device)
        self.phase_offset_hop = torch.tensor([0.0, 0.0], device=self.device)

        self.contact_ratio_off = torch.tensor([0.500, 0.500], device=self.device)
        self.contact_ratio_stand = torch.tensor([0.500, 0.500], device=self.device)
        self.contact_ratio_walk = torch.tensor([0.666, 0.666], device=self.device)
        self.contact_ratio_run = torch.tensor([0.333, 0.333], device=self.device)
        self.contact_ratio_run_fast = torch.tensor([0.250, 0.250], device=self.device)
        self.contact_ratio_jump = torch.tensor([0.666, 0.666], device=self.device)
        self.contact_ratio_hop = torch.tensor([0.666, 0.666], device=self.device)

        self.force_contact_off = torch.tensor([0.0, 0.0], device=self.device)
        self.force_contact_stand = torch.tensor([0.0, 0.0], device=self.device)
        self.force_contact_walk = torch.tensor([0.0, 0.0], device=self.device)
        self.force_contact_run = torch.tensor([0.0, 0.0], device=self.device)
        self.force_contact_run_fast = torch.tensor([0.0, 0.0], device=self.device)
        self.force_contact_jump = torch.tensor([0.0, 0.0], device=self.device)
        self.force_contact_hop = torch.tensor([0.0, 0.0], device=self.device)

        self.force_swing_off = torch.tensor([0.0, 0.0], device=self.device)
        self.force_swing_stand = torch.tensor([0.0, 0.0], device=self.device)
        self.force_swing_walk = torch.tensor([0.0, 0.0], device=self.device)
        self.force_swing_run = torch.tensor([0.0, 0.0], device=self.device)
        self.force_swing_run_fast = torch.tensor([0.0, 0.0], device=self.device)
        self.force_swing_jump = torch.tensor([0.0, 0.0], device=self.device)
        self.force_swing_hop = torch.tensor([1.0, 0.0], device=self.device)

        self.foot_height_off = torch.tensor([0.0, 0.0], device=self.device)
        self.foot_height_stand = torch.tensor([0.06, 0.06], device=self.device)
        self.foot_height_walk = torch.tensor([0.06, 0.06], device=self.device)
        self.foot_height_run = torch.tensor([0.12, 0.12], device=self.device)
        self.foot_height_run_fast = torch.tensor([0.12, 0.12], device=self.device)
        self.foot_height_jump = torch.tensor([0.12, 0.12], device=self.device)
        self.foot_height_hop = torch.tensor([0.12, 0.12], device=self.device)

        self.encoder_off = torch.tensor([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], device=self.device)
        self.encoder_stand = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0], device=self.device)
        self.encoder_walk = torch.tensor([0.0, 1.0, 0.0, 0.0, 0.0, 0.0], device=self.device)
        self.encoder_run = torch.tensor([0.0, 0.0, 1.0, 0.0, 0.0, 0.0], device=self.device)
        self.encoder_run_fast = torch.tensor([0.0, 0.0, 0.0, 1.0, 0.0, 0.0], device=self.device)
        self.encoder_jump = torch.tensor([0.0, 0.0, 0.0, 0.0, 1.0, 0.0], device=self.device)
        self.encoder_hop = torch.tensor([0.0, 0.0, 0.0, 0.0, 0.0, 1.0], device=self.device)

        # encoder of the oscillators, for discrimination of different pattern states
        self.num_encoder = 6
        self.encoder = torch.zeros(self.num_envs, self.num_encoder, dtype=torch.float, device=self.device)
        self.encoder_target = torch.zeros(self.num_envs, self.num_encoder, dtype=torch.float, device=self.device)
        self.encoder[:] = self.encoder_stand
        self.encoder_target[:] = self.encoder_stand
        self.set_encoder(encoder=self.encoder)

        self.rate_encoder = 10.0

        self.mirror_encoder = torch.zeros(self.num_envs, self.num_encoder, dtype=torch.float, device=self.device)

        # ---------------------------------------------------------------
        # set stand pattern in the beginning
        self.set_stand_pattern()

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
        coupling between oscillators
        """
        coupling_x = torch.zeros(self.num_envs, self.num_feet, device=self.device)
        coupling_y = torch.zeros(self.num_envs, self.num_feet, device=self.device)
        phase_offset = self.phase_offset

        for i in range(self.num_feet):
            # index = 0 is the base oscillator
            # if i == 0:
            #     continue

            # coupling between oscillators
            coupling_x[:, i] = 0.0
            coupling_y[:, i] = 0.0

            for j in range(self.num_feet):

                if i == j:
                    continue

                # coupling between oscillators
                coupling_x_ij = torch.cos(phase_offset[:, i] - phase_offset[:, j]) * self.x[:, j] \
                                - torch.sin(phase_offset[:, i] - phase_offset[:, j]) * self.y[:, j]
                coupling_y_ij = torch.sin(phase_offset[:, i] - phase_offset[:, j]) * self.x[:, j] \
                                + torch.cos(phase_offset[:, i] - phase_offset[:, j]) * self.y[:, j]

                # normalize the coupling
                if norm:
                    r_i = torch.sqrt(self.x[:, i] ** 2 + self.y[:, i] ** 2)
                    r_j = torch.sqrt(self.x[:, j] ** 2 + self.y[:, j] ** 2)
                    coupling_x_ij = coupling_x_ij / r_j * r_i
                    coupling_y_ij = coupling_y_ij / r_j * r_i

                coupling_x[:, i] += coupling_x_ij
                coupling_y[:, i] += coupling_y_ij

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
        # record last x, y
        self.x_last = self.x.clone()
        self.y_last = self.y.clone()

        # ---------------------------------------------------------------

        # mirror x, y
        # record last mirror x, y
        self.mirror_x_last = self.mirror_x.clone()
        self.mirror_y_last = self.mirror_y.clone()

        # ---------------------------------------------------------------

        # Parameters for the Hopf oscillator
        r = torch.sqrt(self.x ** 2 + self.y ** 2)
        gamma = self._gamma(self.y)

        # extend frequency to [num_envs, num_feet]
        oscillator_frequency = self.frequency.unsqueeze(1).repeat(1, self.num_feet)

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

        # decay if needed
        self.x = torch.where(r > self.cycle_r_min, self.x * self.amplitude_change_rate, self.x)
        self.y = torch.where(r > self.cycle_r_min, self.y * self.amplitude_change_rate, self.y)

        # map the state to the limit cycle
        r = torch.sqrt(self.x ** 2 + self.y ** 2)
        self.x = torch.where(r > self.cycle_r_max, self.x / r, self.x)
        self.y = torch.where(r > self.cycle_r_max, self.y / r, self.y)

        # ---------------------------------------------------------------

        # mirror values
        # mirror x, y, exchange x[:,0] and x[:,1], y[:,0] and y[:,1]
        self.mirror_x = torch.stack([self.x[:, 1], self.x[:, 0]], dim=1)
        self.mirror_y = torch.stack([self.y[:, 1], self.y[:, 0]], dim=1)

        # ---------------------------------------------------------------

        # encoder
        # extend frequency to [num_envs, num_encoder]
        encoder_frequency = self.frequency.unsqueeze(1).repeat(1, self.num_encoder)

        de = encoder_frequency * self.rate_encoder * (self.encoder_target - self.encoder)

        self.encoder += de * self.dt

        self.mirror_encoder = self.encoder

    # ---------------------------------------------------------------

    def reset(self, env_ids=None, randomize=False):
        """
        reset the state of the oscillator

        1. set phase
        2. calculate x, y
        3. add phase offset
        4. set x, y
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if randomize:
            rand_phase = torch.rand(size=env_ids.shape, device=self.device) * 2 * torch.pi
            rand_phase = rand_phase.unsqueeze(1).repeat(1, self.num_feet)

            self.x[env_ids] = torch.cos(rand_phase)
            self.y[env_ids] = torch.sin(rand_phase)
        else:
            non_rand_phase = torch.zeros(env_ids.shape, device=self.device)
            non_rand_phase = non_rand_phase.unsqueeze(1).repeat(1, self.num_feet)

            self.x[env_ids] = torch.cos(non_rand_phase)
            self.y[env_ids] = torch.sin(non_rand_phase)

        self.set_phase_offset(env_ids=env_ids, phase_offset=self.phase_offset_target[env_ids])

    def step(self, dt=None):
        if dt is not None:
            self.dt = dt

        self._cpg_hopf_oscillator()

    # ---------------------------------------------------------------

    def set_x(self, env_ids=None, x=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if x is None:
            x = torch.ones(env_ids.shape[0], self.num_feet, device=self.device) * self.cycle_r_max
        else:
            x = x

        self.x[env_ids] = x

    def set_y(self, env_ids=None, y=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if y is None:
            y = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            y = y

        self.y[env_ids] = y

    def set_encoder(self, env_ids=None, encoder=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if encoder is None:
            encoder = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            encoder = encoder

        self.encoder_target[env_ids] = encoder

    def set_frequency(self, env_ids=None, frequency=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if frequency is None:
            frequency = (1.0 / 1.0)
        else:
            frequency = frequency

        self.frequency[env_ids] = frequency

    def set_cycle_r(self, env_ids=None, cycle_r=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if cycle_r is None:
            cycle_r = torch.ones(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            cycle_r = cycle_r

        self.cycle_r[env_ids] = cycle_r

    def set_coupling_change_rate(self, env_ids=None, coupling_change_rate=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if coupling_change_rate is None:
            coupling_change_rate = torch.ones(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            coupling_change_rate = coupling_change_rate

        self.coupling_change_rate[env_ids] = coupling_change_rate

    def set_amplitude_change_rate(self, env_ids=None, amplitude_change_rate=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if amplitude_change_rate is None:
            amplitude_change_rate = torch.ones(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            amplitude_change_rate = amplitude_change_rate

        self.amplitude_change_rate[env_ids] = amplitude_change_rate

    def set_contact_ratio(self, env_ids=None, contact_ratio=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

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
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if phase_offset is None:
            phase_offset = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            phase_offset = phase_offset

        # update phase offset
        self.phase_offset_target[env_ids] = phase_offset

    def set_force_contact(self, env_ids=None, force_contact=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if force_contact is None:
            force_contact = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            force_contact = force_contact

        self.force_contact[env_ids] = force_contact

        self.mirror_foot_contact = \
            torch.stack([self.force_contact[:, 1], self.force_contact[:, 0]], dim=1)

    def set_force_swing(self, env_ids=None, force_swing=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if force_swing is None:
            force_swing = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            force_swing = force_swing

        self.force_swing[env_ids] = force_swing

        self.mirror_force_swing = \
            torch.stack([self.force_swing[:, 1], self.force_swing[:, 0]], dim=1)

    def set_foot_height(self, env_ids=None, foot_height=None, foot_height_type=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if foot_height is None:
            foot_height = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            foot_height = foot_height

        self.foot_height_target[env_ids] = foot_height

        if foot_height_type is None:
            foot_height_type = torch.zeros(env_ids.shape[0], self.num_feet, dtype=torch.int, device=self.device)
        else:
            foot_height_type = foot_height_type

        self.foot_height_type[env_ids] = foot_height_type

    def set_shoulder_swing(self, env_ids=None, shoulder_swing=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if shoulder_swing is None:
            shoulder_swing = torch.zeros(env_ids.shape[0], self.num_feet, device=self.device)
        else:
            shoulder_swing = shoulder_swing

        self.shoulder_swing_target[env_ids] = shoulder_swing

    # ---------------------------------------------------------------

    def set_off_pattern(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        self.set_encoder(env_ids=env_ids, encoder=self.encoder_off)
        self.set_frequency(env_ids=env_ids, frequency=self.frequency_off)
        self.set_cycle_r(env_ids=env_ids, cycle_r=self.cycle_r_min)
        self.set_coupling_change_rate(env_ids=env_ids, coupling_change_rate=self.coupling_change_rate_decrease)
        self.set_amplitude_change_rate(env_ids=env_ids, amplitude_change_rate=self.amplitude_change_rate_decrease)
        self.set_phase_offset(env_ids=env_ids, phase_offset=self.phase_offset_off)
        self.set_contact_ratio(env_ids=env_ids, contact_ratio=self.contact_ratio_off)
        self.set_force_contact(env_ids=env_ids, force_contact=self.force_contact_off)
        self.set_force_swing(env_ids=env_ids, force_swing=self.force_swing_off)
        self.set_foot_height(env_ids=env_ids, foot_height=self.foot_height_off)

        self.states[env_ids] = self.STATE_OFF

    def set_stand_pattern(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        self.set_encoder(env_ids=env_ids, encoder=self.encoder_stand)
        self.set_frequency(env_ids=env_ids, frequency=self.frequency_stand)
        self.set_cycle_r(env_ids=env_ids, cycle_r=self.cycle_r_min)
        self.set_coupling_change_rate(env_ids=env_ids, coupling_change_rate=self.coupling_change_rate_decrease)
        self.set_amplitude_change_rate(env_ids=env_ids, amplitude_change_rate=self.amplitude_change_rate_decrease)
        self.set_phase_offset(env_ids=env_ids, phase_offset=self.phase_offset_stand)
        self.set_contact_ratio(env_ids=env_ids, contact_ratio=self.contact_ratio_stand)
        self.set_force_contact(env_ids=env_ids, force_contact=self.force_contact_stand)
        self.set_force_swing(env_ids=env_ids, force_swing=self.force_swing_stand)
        self.set_foot_height(env_ids=env_ids, foot_height=self.foot_height_stand)

        self.states[env_ids] = self.STATE_STAND

    def set_walk_pattern(self, env_ids=None, start_side_selection=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        self.set_encoder(env_ids=env_ids, encoder=self.encoder_walk)
        self.set_frequency(env_ids=env_ids, frequency=self.frequency_walk)
        self.set_cycle_r(env_ids=env_ids, cycle_r=self.cycle_r_max)
        self.set_coupling_change_rate(env_ids=env_ids, coupling_change_rate=self.coupling_change_rate_increase)
        self.set_amplitude_change_rate(env_ids=env_ids, amplitude_change_rate=self.amplitude_change_rate_increase)
        self.set_phase_offset(env_ids=env_ids, phase_offset=self.phase_offset_walk)
        self.set_contact_ratio(env_ids=env_ids, contact_ratio=self.contact_ratio_walk)
        self.set_force_contact(env_ids=env_ids, force_contact=self.force_contact_walk)
        self.set_force_swing(env_ids=env_ids, force_swing=self.force_swing_walk)
        self.set_foot_height(env_ids=env_ids, foot_height=self.foot_height_walk)

        self.from_stand_to_move(env_ids=env_ids, phase_offset=self.phase_offset_walk, start_side_selection=start_side_selection)

        self.states[env_ids] = self.STATE_WALK

    def set_run_pattern(self, env_ids=None, start_side_selection=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        self.set_encoder(env_ids=env_ids, encoder=self.encoder_run)
        self.set_frequency(env_ids=env_ids, frequency=self.frequency_run)
        self.set_cycle_r(env_ids=env_ids, cycle_r=self.cycle_r_max)
        self.set_coupling_change_rate(env_ids=env_ids, coupling_change_rate=self.coupling_change_rate_increase)
        self.set_amplitude_change_rate(env_ids=env_ids, amplitude_change_rate=self.amplitude_change_rate_increase)
        self.set_phase_offset(env_ids=env_ids, phase_offset=self.phase_offset_run)
        self.set_contact_ratio(env_ids=env_ids, contact_ratio=self.contact_ratio_run)
        self.set_force_contact(env_ids=env_ids, force_contact=self.force_contact_run)
        self.set_force_swing(env_ids=env_ids, force_swing=self.force_swing_run)
        self.set_foot_height(env_ids=env_ids, foot_height=self.foot_height_run)

        self.from_stand_to_move(env_ids=env_ids, phase_offset=self.phase_offset_run, start_side_selection=start_side_selection)

        self.states[env_ids] = self.STATE_RUN

    def set_jump_pattern(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        self.set_encoder(env_ids=env_ids, encoder=self.encoder_jump)
        self.set_frequency(env_ids=env_ids, frequency=self.frequency_jump)
        self.set_cycle_r(env_ids=env_ids, cycle_r=self.cycle_r_max)
        self.set_coupling_change_rate(env_ids=env_ids, coupling_change_rate=self.coupling_change_rate_increase)
        self.set_amplitude_change_rate(env_ids=env_ids, amplitude_change_rate=self.amplitude_change_rate_increase)
        self.set_phase_offset(env_ids=env_ids, phase_offset=self.phase_offset_jump)
        self.set_contact_ratio(env_ids=env_ids, contact_ratio=self.contact_ratio_jump)
        self.set_force_contact(env_ids=env_ids, force_contact=self.force_contact_jump)
        self.set_force_swing(env_ids=env_ids, force_swing=self.force_swing_jump)
        self.set_foot_height(env_ids=env_ids, foot_height=self.foot_height_jump)

        self.from_stand_to_move(env_ids=env_ids, phase_offset=self.phase_offset_jump)

        self.states[env_ids] = self.STATE_JUMP

    def set_hop_pattern(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        self.set_encoder(env_ids=env_ids, encoder=self.encoder_hop)
        self.set_frequency(env_ids=env_ids, frequency=self.frequency_hop)
        self.set_cycle_r(env_ids=env_ids, cycle_r=self.cycle_r_max)
        self.set_coupling_change_rate(env_ids=env_ids, coupling_change_rate=self.coupling_change_rate_increase)
        self.set_amplitude_change_rate(env_ids=env_ids, amplitude_change_rate=self.amplitude_change_rate_increase)
        self.set_phase_offset(env_ids=env_ids, phase_offset=self.phase_offset_hop)
        self.set_contact_ratio(env_ids=env_ids, contact_ratio=self.contact_ratio_hop)
        self.set_force_contact(env_ids=env_ids, force_contact=self.force_contact_hop)
        self.set_force_swing(env_ids=env_ids, force_swing=self.force_swing_hop)
        self.set_foot_height(env_ids=env_ids, foot_height=self.foot_height_hop)

        self.from_stand_to_move(env_ids=env_ids, phase_offset=self.phase_offset_hop)

        self.states[env_ids] = self.STATE_HOP

    def from_stand_to_move(
            self,
            env_ids=None,
            phase_offset=torch.Tensor([0.0, 0.0]),
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
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

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
        if randomize_start_side:
            # 随机选择左侧或右侧的腿踏步等运动模式
            output_selection = torch.randint(low=0,
                                             high=2,
                                             size=(env_ids_of_stand_state.shape[0], 1),
                                             dtype=torch.int,
                                             device=self.device)
        else:
            # 默认使用左侧的腿踏步等运动模式
            output_selection = None

        if start_side_selection is not None:
            # 如果提供了 start_side_selection，则使用该值作为输出选择
            output_selection = start_side_selection[indexes_of_stand_state]

        self.set_output_selection(env_ids=env_ids_of_stand_state,
                                  output_selection=output_selection)

    def get_stand_pattern_env_ids(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_STAND)[0]]

        return env_ids

    def get_walk_pattern_env_ids(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_WALK)[0]]

        return env_ids

    def get_run_pattern_env_ids(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_RUN)[0]]

        return env_ids

    def get_jump_pattern_env_ids(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_JUMP)[0]]

        return env_ids

    def get_hop_pattern_env_ids(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_HOP)[0]]

        return env_ids

    def get_stand_env_ids(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        # state match stand
        env_ids = env_ids[torch.where(self.states[env_ids] == self.STATE_STAND)[0]]

        # FIXME:
        #  Jason 2024-12-25: 这里遇到一个问题，如果用 mirror 的值进行计算，则会在 gym 训练中报如下错误：
        #  ../aten/src/ATen/native/cuda/IndexKernel.cu:92: operator():
        #  block: [0,0,0], thread: [0,0,0] Assertion `-sizes[i] <= index && index < sizes[i] && "index out of bounds"` failed.
        #  ../aten/src/ATen/native/cuda/IndexKernel.cu:92: operator():
        #  block: [0,0,0], thread: [1,0,0] Assertion `-sizes[i] <= index && index < sizes[i] && "index out of bounds"` failed.

        # phase diff match stand
        temp_phase_diff = self.get_phase_diff(env_ids=env_ids)[:, 0]  # dims 2->1

        # calculate the condition for phase difference being less than the threshold
        condition1 = temp_phase_diff < self.phase_diff_threshold_for_stand

        # calculate the condition for phase difference being greater than (1 - threshold)
        condition2 = temp_phase_diff > (1 - self.phase_diff_threshold_for_stand)

        # combine both conditions using logical OR
        combined_condition = condition1 | condition2

        # get the indices where the combined condition is true
        env_ids = torch.where(combined_condition)[0]

        return env_ids

    # ====================================================================================================
    # Original Values

    def get_x(self, env_ids=None):
        """
        get the x value of the oscillators

        return:
        x: [num_envs, num_feet]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.x[env_ids]

    def get_y(self, env_ids=None):
        """
        get the y value of the oscillators

        return:
        y: [num_envs, num_feet]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.y[env_ids]

    def get_encoder(self, env_ids=None):
        """
        get the encoder value of the oscillators

        return:
        encoder: [num_envs, num_feet]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.encoder[env_ids]

    def get_encoder_3bits(self, env_ids=None):
        """
        get the encoder value of the oscillators

        return:
        encoder: [num_envs, num_feet]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        temp_encoder = self.get_encoder()

        # only use first 3 bytes of encoder value
        encoder_3bits = temp_encoder[:, 0:3]

        return encoder_3bits[env_ids]

    def get_x_norm(self, env_ids=None):
        """
        get the normalized x value of the oscillators

        return:
        x_norm: [num_envs, num_feet], range: [-1, 1]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        r_env_ids = torch.sqrt(self.x ** 2 + self.y ** 2)
        x_norm = torch.where(r_env_ids > self.cycle_r_min, self.x, 0)

        return x_norm[env_ids]

    def get_y_norm(self, env_ids=None):
        """
        get the normalized y value of the oscillators

        return:
        y_norm: [num_envs, num_feet], range: [-1, 1]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        r_env_ids = torch.sqrt(self.x ** 2 + self.y ** 2)
        y_norm = torch.where(r_env_ids > self.cycle_r_min, self.y, 0)

        return y_norm[env_ids]

    def get_phase_base(self, env_ids=None):
        """
        get the base phase of the oscillators, the base phase is the phase of oscillator[0],
        but need to extend to all oscillators shape=[num_envs, num_feet]

        return:
        phase: [num_envs, num_feet], range: [0, 2 * pi]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        phi = torch.arctan2(self.y[:, 0], self.x[:, 0])

        phase_base = torch.where(phi < 0, phi + 2 * torch.pi, phi)
        phase_base = phase.unsqueeze(1).repeat(1, self.num_feet)

        return phase_base[env_ids]

    def get_phase_rad(self, env_ids=None):
        """
        get the phase of the oscillators

        return:
        phase: [num_envs, num_feet], range: [0, 2 * pi]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        phi = torch.arctan2(self.y, self.x)
        phase_rad = torch.where(phi < 0, phi + 2 * torch.pi, phi)

        return phase_rad[env_ids]

    def get_phase_norm(self, env_ids=None):
        """
        get the normalized phase of the oscillators

        return:
        phase_norm: [num_envs, num_feet], range: [0, 1]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        phase_norm = self.get_phase_rad() / (2 * torch.pi)

        return phase_norm[env_ids]

    def get_phase_offset(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.phase_offset[env_ids]

    def get_phase_diff(self, env_ids=None):
        """
        get the phase difference between the oscillators

        return:
        phase_diff: [num_envs, num_feet, num_feet], range: [0, 2 * pi]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        temp_phase = self.get_phase_norm()

        # phase_diff 这里是 env_ids * 1 维数据
        temp_phase_diff = temp_phase[:, 0:1] - temp_phase[:, 1:2]

        # self.phase_diff 是 env_ids * num_feet 维数据，但是每一个 env_ids 的数据是相同的值
        temp_phase_diff = \
            torch.where(temp_phase_diff < 0,
                        temp_phase_diff + 1,
                        temp_phase_diff).repeat(1, self.num_feet)

        self.phase_diff = temp_phase_diff

        return self.phase_diff[env_ids]

    def get_foot_height(self, env_ids=None, type=FOOT_HEIGHT_TYPE_SMOOTH) -> torch.Tensor:
        """
        map the y value to the foot height

        Inputs:
        - env_ids: [num_envs]
        - type: foot height type, Default: FOOT_HEIGHT_TYPE_SMOOTH
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        # 1. get foot height raw
        foot_height_raw = torch.where(self.y <= self.foot_height_threshold,
                                      0,
                                      self.y - self.foot_height_threshold)
        foot_height_raw = foot_height_raw / (self.cycle_r_max - self.foot_height_threshold)

        # 2. calculate foot height based on the foot height type
        if type == self.FOOT_HEIGHT_TYPE_LINEAR:
            temp_foot_height = (foot_height_raw ** 1) * self.foot_height_target

        elif type == self.FOOT_HEIGHT_TYPE_SMOOTH:
            temp_foot_height = (foot_height_raw ** 2) * self.foot_height_target

        elif type == self.FOOT_HEIGHT_TYPE_MIXED:
            # temp_rate change the smoothness of the curve
            # temp_rate change based on the phase of the oscillators
            _temp_rate_min = 1
            _temp_rate_max = 2
            _phase_norm = self.get_phase_norm()
            _contact_ratio = torch.clip(self.contact_ratio, 0.01, 0.99)
            _contact_phase_norm = torch.where(_phase_norm < (1 - _contact_ratio),
                                              _phase_norm / (1 - _contact_ratio),
                                              1)
            _temp_rate = _temp_rate_min + (_temp_rate_max - _temp_rate_min) * _contact_phase_norm
            temp_foot_height = (foot_height_raw ** _temp_rate) * self.foot_height_target

        elif type == self.FOOT_HEIGHT_TYPE_NATURAL:
            _A = numpy.array([
                # F(0) = 0
                # F(1) = 1
                # F'(0) = 0
                # F'(1) = 0
                # F(0.25) = 0.125
                # F(0.75) = 0.875
                [0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 1, 0],
                [5, 4, 3, 2, 1, 0],
                [0.25 ** 5, 0.25 ** 4, 0.25 ** 3, 0.25 ** 2, 0.25 ** 1, 0.25 ** 0],
                [0.75 ** 5, 0.75 ** 4, 0.75 ** 3, 0.75 ** 2, 0.75 ** 1, 0.75 ** 0],
            ])
            _A_inv = numpy.linalg.inv(_A)
            _b = numpy.array([
                0,
                1,
                0,
                0,
                0.125,
                0.875,
            ])
            _params = numpy.dot(_A_inv, _b)

            # F = (1 - e^(-a*y)) + e^(-a)*y
            # _natural_ratio = 1.0
            # self.foot_height = ((1 - torch.exp(-_natural_ratio * foot_height_raw))
            #                     + math.exp(-_natural_ratio) * foot_height_raw) \
            #                    * self.foot_height_target

            # F = a*y^5 + b*y^4 + c*y^3 + d*y^2 + e*y^1 + f*y^0
            temp_foot_height = (_params[0] * foot_height_raw ** 5
                                + _params[1] * foot_height_raw ** 4
                                + _params[2] * foot_height_raw ** 3
                                + _params[3] * foot_height_raw ** 2
                                + _params[4] * foot_height_raw ** 1
                                + _params[5]) * self.foot_height_target

        else:
            temp_foot_height = (foot_height_raw ** 1) * self.foot_height_target

        # check force contact
        temp_foot_height = temp_foot_height * (1 - self.get_force_contact())

        # check force swing
        temp_foot_height = temp_foot_height + self.get_force_swing() * self.foot_height_target

        # clip
        temp_foot_height = torch.clip(temp_foot_height,
                                      min=torch.zeros_like(temp_foot_height, device=self.device),
                                      max=self.foot_height_target)

        # update foot height
        self.foot_height = temp_foot_height

        return self.foot_height[env_ids]

    def get_foot_height_norm(self, env_ids=None, type=FOOT_HEIGHT_TYPE_SMOOTH):
        """
        get the normalized foot height of the oscillators

        Inputs:
        - env_ids: [num_envs]
        - type: foot height type, Default: FOOT_HEIGHT_TYPE_SMOOTH
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        temp_foot_height = self.get_foot_height(type=type)
        foot_height_norm = temp_foot_height / self.foot_height_target

        return foot_height_norm[env_ids]

    def get_foot_height_max(self, env_ids=None):
        """
        get the maximum foot height of the oscillators

        Inputs:
        - env_ids: [num_envs]
        - type: foot height type, Default: FOOT_HEIGHT_TYPE_SMOOTH
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        foot_height_max = self.foot_height_target

        return foot_height_max[env_ids]

    def get_foot_contact(self, env_ids=None) -> torch.Tensor:
        """
        get the foot contact situation
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        # situation 1: when in move state, y < contact_threshold
        flags_of_foot_contact_s1 = (self.y <= self.contact_threshold).int()

        # situation 2: when in stand state, need phase_diff_raw < phase_diff_threshold_for_stand
        env_ids_of_stand = self.get_stand_env_ids()
        flags_of_foot_contact_s2 = torch.zeros(self.num_envs, self.num_feet, device=self.device)
        flags_of_foot_contact_s2[env_ids_of_stand] = 1

        # situation 3: force setting the foot contact situation
        flags_of_foot_contact_s3 = self.get_force_contact()

        # situation 4: force setting the foot swing situation
        flags_of_foot_contact_s4 = self.get_force_swing()

        # foot contact situation
        temp_foot_contact = (flags_of_foot_contact_s1
                             + flags_of_foot_contact_s2
                             + flags_of_foot_contact_s3) \
                            * (1 - flags_of_foot_contact_s4)

        self.foot_contact = torch.clip(temp_foot_contact, 0, 1)

        return self.foot_contact[env_ids]

    def get_force_contact(self, env_ids=None) -> torch.Tensor:
        """
        get the foot contact situation
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.force_contact[env_ids]

    def get_force_swing(self, env_ids=None) -> torch.Tensor:
        """
        get the foot swing situation
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.force_swing[env_ids]

    def get_shoulder_swing(self, env_ids=None) -> torch.Tensor:
        """
        get the shoulder swing value

        Inputs:
        - env_ids: [num_envs]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        shoulder_swing = torch.abs(self.y * self.shoulder_swing_target)

        self.shoulder_swing = shoulder_swing

        return self.shoulder_swing[env_ids]

    def get_swing_middle(self, env_ids=None, type=SWING_MIDDLE_TYPE_LINEAR) -> torch.Tensor:
        """
        get the swing middle value

        type:
        - SWING_MIDDLE_TYPE_LINEAR: linear
        - SWING_MIDDLE_TYPE_ACCURATE: accurate

        return:
        swing_middle: [num_envs, num_feet]

        note:
        stand situation will have a swing_middle value of 0
        swing situation will have a swing_middle value of 1
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        # only consider the foot height above the middle situation
        foot_height_norm = self.get_foot_height_norm()
        foot_height_norm = torch.where(foot_height_norm > 0.5, foot_height_norm - 0.5, 0)
        foot_height_norm = foot_height_norm * 2

        if type == self.SWING_MIDDLE_TYPE_LINEAR:
            swing_middle = foot_height_norm ** 1
        elif type == self.SWING_MIDDLE_TYPE_ACCURATE:
            swing_middle = foot_height_norm ** 3
        else:
            swing_middle = foot_height_norm ** 1

        return swing_middle[env_ids]

    # ====================================================================================================
    # Mirror Values

    def get_mirror_x(self, env_ids=None):
        """
        get the mirror x value of the oscillators

        return:
        x: [num_envs, num_feet]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.mirror_x[env_ids]

    def get_mirror_y(self, env_ids=None):
        """
        get the mirror y value of the oscillators

        return:
        y: [num_envs, num_feet]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.mirror_y[env_ids]

    def get_mirror_encoder(self, env_ids=None):
        """
        get the mirror encoder value of the oscillators

        return:
        encoder: [num_envs, num_feet]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.mirror_encoder[env_ids]

    def get_mirror_encoder_3bits(self, env_ids=None):
        """
        get the mirror encoder value of the oscillators

        return:
        encoder: [num_envs, num_feet]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        temp_encoder = self.get_mirror_encoder()

        # only use first 3 bytes of encoder value
        encoder_3bits = temp_encoder[:, 0:3]

        return encoder_3bits[env_ids]

    def get_mirror_x_norm(self, env_ids=None):
        """
        get the normalized mirror x value of the oscillators

        return:
        x_norm: [num_envs, num_feet], range: [-1, 1]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        r_env_ids = torch.sqrt(self.mirror_x ** 2 + self.mirror_y ** 2)
        mirror_x_norm = torch.where(r_env_ids > self.cycle_r_min, self.mirror_x, 0)

        return mirror_x_norm[env_ids]

    def get_mirror_y_norm(self, env_ids=None):
        """
        get the normalized mirror y value of the oscillators

        return:
        y_norm: [num_envs, num_feet], range: [-1, 1]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        r_env_ids = torch.sqrt(self.mirror_y ** 2 + self.mirror_y ** 2)
        mirror_y_norm = torch.where(r_env_ids > self.cycle_r_min, self.mirror_y, 0)

        return mirror_y_norm[env_ids]

    def get_mirror_phase_rad(self, env_ids=None):
        """
        get the mirror phase of the oscillators

        return:
        phase: [num_envs, num_feet], range: [0, 2 * pi]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        phi = torch.arctan2(self.mirror_y, self.mirror_x)
        phase_rad = torch.where(phi < 0, phi + 2 * torch.pi, phi)

        return phase_rad[env_ids]

    def get_mirror_phase_norm(self, env_ids=None):
        """
        get the normalized mirror phase of the oscillators

        return:
        phase_norm: [num_envs, num_feet], range: [0, 1]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        mirror_phase_norm = self.get_mirror_phase_rad() / (2 * torch.pi)

        return mirror_phase_norm[env_ids]

    def get_mirror_phase_diff(self, env_ids=None):
        """
        get the mirror phase difference between the oscillators

        return:
        phase_diff: [num_envs, num_feet, num_feet], range: [0, 2 * pi]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        temp_phase = self.get_mirror_phase_norm()

        # phase_diff 这里是 env_ids * 1 维数据
        temp_phase_diff = temp_phase[env_ids, 0:1] - temp_phase[env_ids, 1:2]

        # self.phase_diff 是 env_ids * num_feet 维数据，但是每一个 env_ids 的数据是相同的值
        temp_phase_diff = \
            torch.where(temp_phase_diff < 0,
                        temp_phase_diff + 1,
                        temp_phase_diff).repeat(1, self.num_feet)

        self.mirror_phase_diff = temp_phase_diff

        return self.mirror_phase_diff[env_ids]

    def get_mirror_foot_height(self, env_ids=None, type=FOOT_HEIGHT_TYPE_SMOOTH) -> torch.Tensor:
        """
        map the mirror y value to the mirror foot height

        Inputs:
        - env_ids: [num_envs]
        - type: foot height type, Default: FOOT_HEIGHT_TYPE_SMOOTH
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        mirror_foot_height_raw = torch.where(self.mirror_y <= self.foot_height_threshold,
                                             0,
                                             self.mirror_y - self.foot_height_threshold)
        mirror_foot_height_raw = mirror_foot_height_raw / (self.cycle_r_max - self.foot_height_threshold)

        if type == self.FOOT_HEIGHT_TYPE_LINEAR:
            temp_foot_height = (mirror_foot_height_raw ** 1) * self.foot_height_target

        elif type == self.FOOT_HEIGHT_TYPE_SMOOTH:
            temp_foot_height = (mirror_foot_height_raw ** 2) * self.foot_height_target

        elif type == self.FOOT_HEIGHT_TYPE_MIXED:
            # temp_rate change the smoothness of the curve
            # temp_rate change based on the phase of the oscillators
            _temp_rate_min = 1
            _temp_rate_max = 2
            _mirror_phase_norm = self.get_mirror_phase_norm()
            _contact_ratio = torch.clip(self.contact_ratio, 0.01, 0.99)
            _contact_phase_norm = torch.where(_mirror_phase_norm < (1 - _contact_ratio),
                                              _mirror_phase_norm / (1 - _contact_ratio),
                                              1)
            _temp_rate = _temp_rate_min + (_temp_rate_max - _temp_rate_min) * _contact_phase_norm
            temp_foot_height = (mirror_foot_height_raw ** _temp_rate) * self.foot_height_target

        elif type == self.FOOT_HEIGHT_TYPE_NATURAL:
            _A = numpy.array([
                # F(0) = 0
                # F(1) = 1
                # F'(0) = 0
                # F'(1) = 0
                # F(0.25) = 0.125
                # F(0.75) = 0.875
                [0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 1, 0],
                [5, 4, 3, 2, 1, 0],
                [0.25 ** 5, 0.25 ** 4, 0.25 ** 3, 0.25 ** 2, 0.25 ** 1, 0.25 ** 0],
                [0.75 ** 5, 0.75 ** 4, 0.75 ** 3, 0.75 ** 2, 0.75 ** 1, 0.75 ** 0],
            ])
            _A_inv = numpy.linalg.inv(_A)
            _b = numpy.array([
                0,
                1,
                0,
                0,
                0.125,
                0.875,
            ])
            _params = numpy.dot(_A_inv, _b)

            # F = (1 - e^(-a*y)) + e^(-a)*y
            # _natural_ratio = 1.0
            # self.foot_height = ((1 - torch.exp(-_natural_ratio * foot_height_raw))
            #                     + math.exp(-_natural_ratio) * foot_height_raw) \
            #                    * self.foot_height_target

            # F = a*y^5 + b*y^4 + c*y^3 + d*y^2 + e*y^1 + f*y^0
            temp_foot_height = (_params[0] * mirror_foot_height_raw ** 5
                                + _params[1] * mirror_foot_height_raw ** 4
                                + _params[2] * mirror_foot_height_raw ** 3
                                + _params[3] * mirror_foot_height_raw ** 2
                                + _params[4] * mirror_foot_height_raw ** 1
                                + _params[5]) * self.foot_height_target

        else:
            temp_foot_height = (mirror_foot_height_raw ** 1) * self.foot_height_target

        # check force contact
        temp_foot_height = temp_foot_height * (1 - self.get_mirror_force_contact())

        # check force swing
        temp_foot_height = temp_foot_height + self.get_mirror_force_swing() * self.foot_height_target

        # clip
        temp_foot_height = torch.clip(temp_foot_height,
                                      min=torch.zeros_like(temp_foot_height, device=self.device),
                                      max=self.foot_height_target)

        # update foot height
        self.mirror_foot_height = temp_foot_height

        return self.mirror_foot_height[env_ids]

    def get_mirror_foot_height_norm(self, env_ids=None, type=FOOT_HEIGHT_TYPE_SMOOTH):
        """
        get the normalized mirror foot height of the oscillators

        Inputs:
        - env_ids: [num_envs]
        - type: foot height type, Default: FOOT_HEIGHT_TYPE_SMOOTH
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        temp_foot_height = self.get_mirror_foot_height(type=type)
        mirror_foot_height_norm = temp_foot_height / self.foot_height_target

        return mirror_foot_height_norm[env_ids]

    def get_mirror_foot_height_max(self, env_ids=None):
        """
        get the maximum foot height of the oscillators

        Inputs:
        - env_ids: [num_envs]
        - type: foot height type, Default: FOOT_HEIGHT_TYPE_SMOOTH
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        mirror_foot_height_max = self.foot_height_target

        return mirror_foot_height_max[env_ids]

    def get_mirror_foot_contact(self, env_ids=None) -> torch.Tensor:
        """
        get the foot contact situation
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        # situation 1: when in move state, y < contact_threshold
        flags_of_foot_contact_s1 = (self.mirror_y <= self.contact_threshold).int()

        # situation 2: when in stand state, need phase_diff_raw < phase_diff_threshold_for_stand
        env_ids_of_stand = self.get_stand_env_ids()
        flags_of_foot_contact_s2 = torch.zeros(self.num_envs, self.num_feet, device=self.device)
        flags_of_foot_contact_s2[env_ids_of_stand] = 1

        # situation 3: force setting the foot contact situation
        flags_of_foot_contact_s3 = self.get_mirror_force_contact()

        # situation 4: force setting the foot swing situation
        flags_of_foot_contact_s4 = self.get_mirror_force_swing()

        # foot contact situation
        temp_foot_contact = (flags_of_foot_contact_s1
                             + flags_of_foot_contact_s2
                             + flags_of_foot_contact_s3) \
                            * (1 - flags_of_foot_contact_s4)

        self.mirror_foot_contact = torch.clip(temp_foot_contact, 0, 1)

        return self.mirror_foot_contact[env_ids]

    def get_mirror_force_contact(self, env_ids=None) -> torch.Tensor:
        """
        get the foot contact situation
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.mirror_force_contact[env_ids]

    def get_mirror_force_swing(self, env_ids=None) -> torch.Tensor:
        """
        get the foot swing situation
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        return self.mirror_force_swing[env_ids]

    def get_mirror_shoulder_swing(self, env_ids=None) -> torch.Tensor:
        """
        get the shoulder swing situation
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        # TODO: add code to return mirror_shoulder_swing
        return self.shoulder_swing[env_ids]

    def get_mirror_swing_middle(self, env_ids=None, type=SWING_MIDDLE_TYPE_LINEAR) -> torch.Tensor:
        """
        get the swing middle value

        type:
        - SWING_MIDDLE_TYPE_LINEAR: linear
        - SWING_MIDDLE_TYPE_ACCURATE: accurate

        return:
        swing_middle: [num_envs, num_feet]

        note:
        stand situation will have a swing_middle value of 0
        swing situation will have a swing_middle value of 1
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        # only consider the foot height above the middle situation
        foot_height_norm = self.get_mirror_foot_height_norm()
        foot_height_norm = torch.where(foot_height_norm > 0.5, foot_height_norm - 0.5, 0)
        foot_height_norm = foot_height_norm * 2

        if type == self.SWING_MIDDLE_TYPE_LINEAR:
            swing_middle = foot_height_norm ** 1
        elif type == self.SWING_MIDDLE_TYPE_ACCURATE:
            swing_middle = foot_height_norm ** 3
        else:
            swing_middle = foot_height_norm ** 1

        return swing_middle[env_ids]

    # ====================================================================================================
    # Output Values

    def set_output_selection(self, env_ids=None, output_selection=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        if output_selection is None:
            output_selection = torch.zeros(env_ids.shape[0], 1, dtype=torch.int, device=self.device)
        else:
            output_selection = output_selection

        self.output_selection[env_ids] = output_selection

    def get_output_x(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_x = torch.where(self.output_selection == 0, self.x, self.mirror_x)

        return output_x[env_ids]

    def get_output_y(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_y = torch.where(self.output_selection == 0, self.y, self.mirror_y)

        return output_y[env_ids]

    def get_output_x_norm(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_x_norm = torch.where(self.output_selection == 0, self.get_x_norm(), self.get_mirror_x_norm())

        return output_x_norm[env_ids]

    def get_output_y_norm(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_y_norm = torch.where(self.output_selection == 0, self.get_y_norm(), self.get_mirror_y_norm())

        return output_y_norm[env_ids]

    def get_output_encoder(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_encoder = torch.where(self.output_selection == 0, self.get_encoder(), self.get_mirror_encoder())

        return output_encoder[env_ids]

    def get_output_encoder_3bits(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_encoder_3bits = torch.where(self.output_selection == 0,
                                           self.get_encoder_3bits(),
                                           self.get_mirror_encoder_3bits())

        return output_encoder_3bits[env_ids]

    def get_output_phase_norm(self, env_ids=None):
        """
        get the normalized phase of the oscillators

        return:
        phase_norm: [num_envs, num_feet], range: [0, 1]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_phase_norm = torch.where(self.output_selection == 0, self.get_phase_norm(), self.get_mirror_phase_norm())

        return output_phase_norm[env_ids]

    def get_output_foot_height(self, env_ids=None, type=FOOT_HEIGHT_TYPE_SMOOTH) -> torch.Tensor:
        """
        map the y value to the foot height

        Inputs:
        - env_ids: [num_envs]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_foot_height = torch.where(self.output_selection == 0,
                                         self.get_foot_height(type=type),
                                         self.get_mirror_foot_height(type=type))

        return output_foot_height[env_ids]

    def get_output_foot_height_max(self, env_ids=None):
        """
        get the maximum foot height of the oscillators

        Inputs:
        - env_ids: [num_envs]
        - type: foot height type, Default: FOOT_HEIGHT_TYPE_SMOOTH
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_foot_height_max = torch.where(self.output_selection == 0,
                                             self.get_foot_height_max(),
                                             self.get_mirror_foot_height_max())

        return output_foot_height_max[env_ids]

    def get_output_foot_height_norm(self, env_ids=None, type=FOOT_HEIGHT_TYPE_SMOOTH):
        """
        get the normalized foot height of the oscillators

        Inputs:
        - env_ids: [num_envs]
        - type: foot height type, Default: FOOT_HEIGHT_TYPE_SMOOTH
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_foot_height_norm = torch.where(self.output_selection == 0,
                                              self.get_foot_height_norm(type=type),
                                              self.get_mirror_foot_height_norm(type=type))

        return output_foot_height_norm[env_ids]

    def get_output_foot_contact(self, env_ids=None):
        """
        get the foot contact situation
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_foot_contact = torch.where(self.output_selection == 0,
                                          self.get_foot_contact(),
                                          self.get_mirror_foot_contact())

        return output_foot_contact[env_ids]

    def get_output_phase_diff(self, env_ids=None):
        """
        get the phase difference between the oscillators

        return:
        phase_diff: [num_envs, num_feet, num_feet], range: [0, 2 * pi]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_phase_diff = torch.where(self.output_selection == 0,
                                        self.get_phase_diff(),
                                        self.get_mirror_phase_diff())

        return output_phase_diff[env_ids]

    def get_output_shoulder_swing(self, env_ids=None) -> torch.Tensor:
        """
        get the shoulder swing value

        Inputs:
        - env_ids: [num_envs]
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        shoulder_swing = torch.where(self.output_selection == 0,
                                     self.get_shoulder_swing(),
                                     self.get_mirror_shoulder_swing())

        return shoulder_swing[env_ids]

    def get_output_swing_middle(self, env_ids=None, type=SWING_MIDDLE_TYPE_LINEAR) -> torch.Tensor:
        """
        get the swing middle value

        type:
        - SWING_MIDDLE_TYPE_LINEAR: linear
        - SWING_MIDDLE_TYPE_ACCURATE: accurate

        return:
        swing_middle: [num_envs, num_feet]

        note:
        stand situation will have a swing_middle value of 0
        swing situation will have a swing_middle value of 1
        """
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        else:
            env_ids = env_ids

        output_swing_middle = torch.where(self.output_selection == 0,
                                          self.get_swing_middle(type=type),
                                          self.get_mirror_swing_middle(type=type))

        return output_swing_middle[env_ids]


# ====================================================================================================


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import random

    T = random.randint(20, 20)
    dt = 0.02
    time = range(int(T / dt))

    x_list = []
    y_list = []
    encoder_list = []
    phase_list = []
    phase_diff_list = []
    foot_height_list = []
    foot_contact_list = []
    swing_middle_list = []

    mirror_x_list = []
    mirror_y_list = []
    mirror_encoder_list = []
    mirror_phase_list = []
    mirror_phase_diff_list = []
    mirror_foot_height_list = []
    mirror_foot_contact_list = []
    mirror_swing_middle_list = []

    output_x_list = []
    output_y_list = []
    output_encoder_list = []
    output_phase_list = []
    output_phase_diff_list = []
    output_foot_height_list = []
    output_foot_contact_list = []
    output_swing_middle_list = []

    gait_generator = FourierGaitGenerator(
        num_envs=1,
        num_feet=2,
        dt=dt,
        frequency=(1.0 / 1.0),
        device="cpu")

    gait_generator.reset(env_ids=torch.tensor([0]), randomize=True)

    for i in time:
        if i == len(time) // 9 * 0:
            gait_generator.set_stand_pattern()

        if i == len(time) // 9 * 1:
            gait_generator.set_walk_pattern()

        if i == len(time) // 9 * 2:
            gait_generator.set_stand_pattern()

        if i == len(time) // 9 * 3:
            gait_generator.set_walk_pattern()

        if i == len(time) // 9 * 4:
            gait_generator.set_stand_pattern()

        if i == len(time) // 9 * 5:
            gait_generator.set_walk_pattern()

        if i == len(time) // 9 * 6:
            gait_generator.set_stand_pattern()

        if i == len(time) // 9 * 7:
            gait_generator.set_walk_pattern()

        if i == len(time) // 9 * 8:
            gait_generator.set_stand_pattern()

        gait_generator.step()

        # get original values
        x = gait_generator.get_x_norm()
        y = gait_generator.get_y_norm()
        encoder = gait_generator.get_encoder()
        phase = gait_generator.get_phase_norm()
        foot_height = gait_generator.get_foot_height(type=FourierGaitGenerator.FOOT_HEIGHT_TYPE_NATURAL)
        foot_contact = gait_generator.get_foot_contact()
        swing_middle = gait_generator.get_swing_middle()

        phase_diff = gait_generator.get_phase_diff()
        phase_diff = torch.concat([phase_diff[0],
                                   torch.tensor([gait_generator.phase_diff_threshold_for_stand]),
                                   torch.tensor([1 - gait_generator.phase_diff_threshold_for_stand])])

        # get mirror values
        mirror_x = gait_generator.get_mirror_x_norm()
        mirror_y = gait_generator.get_mirror_y_norm()
        mirror_encoder = gait_generator.get_mirror_encoder()
        mirror_phase = gait_generator.get_mirror_phase_norm()
        mirror_foot_height = gait_generator.get_mirror_foot_height(type=FourierGaitGenerator.FOOT_HEIGHT_TYPE_NATURAL)
        mirror_foot_contact = gait_generator.get_mirror_foot_contact()
        mirror_swing_middle = gait_generator.get_mirror_swing_middle()

        mirror_phase_diff = gait_generator.get_mirror_phase_diff()
        mirror_phase_diff = torch.concat([mirror_phase_diff[0],
                                          torch.tensor([gait_generator.phase_diff_threshold_for_stand]),
                                          torch.tensor([1 - gait_generator.phase_diff_threshold_for_stand])])

        # get output values
        output_x = gait_generator.get_output_x_norm()
        output_y = gait_generator.get_output_y_norm()
        output_encoder = gait_generator.get_output_encoder()
        output_phase = gait_generator.get_output_phase_norm()
        output_foot_height = gait_generator.get_output_foot_height(type=FourierGaitGenerator.FOOT_HEIGHT_TYPE_NATURAL)
        output_foot_contact = gait_generator.get_output_foot_contact()
        output_swing_middle = gait_generator.get_output_swing_middle()

        output_phase_diff = gait_generator.get_output_phase_diff()
        output_phase_diff = torch.concat([output_phase_diff[0],
                                          torch.tensor([gait_generator.phase_diff_threshold_for_stand]),
                                          torch.tensor([1 - gait_generator.phase_diff_threshold_for_stand])])

        # add to list
        x_list.append(x)
        y_list.append(y)
        encoder_list.append(encoder)
        phase_list.append(phase)
        foot_height_list.append(foot_height)
        foot_contact_list.append(foot_contact)
        phase_diff_list.append(phase_diff)
        swing_middle_list.append(swing_middle)

        mirror_x_list.append(mirror_x)
        mirror_y_list.append(mirror_y)
        mirror_encoder_list.append(mirror_encoder)
        mirror_phase_list.append(mirror_phase)
        mirror_foot_height_list.append(mirror_foot_height)
        mirror_foot_contact_list.append(mirror_foot_contact)
        mirror_phase_diff_list.append(mirror_phase_diff)
        mirror_swing_middle_list.append(mirror_swing_middle)

        output_x_list.append(output_x)
        output_y_list.append(output_y)
        output_encoder_list.append(output_encoder)
        output_phase_list.append(output_phase)
        output_foot_height_list.append(output_foot_height)
        output_foot_contact_list.append(output_foot_contact)
        output_phase_diff_list.append(output_phase_diff)
        output_swing_middle_list.append(output_swing_middle)

    x_list = torch.stack(x_list).squeeze().detach().numpy()
    y_list = torch.stack(y_list).squeeze().detach().numpy()
    encoder_list = torch.stack(encoder_list).squeeze().detach().numpy()
    phase_list = torch.stack(phase_list).squeeze().detach().numpy()
    foot_height_list = torch.stack(foot_height_list).squeeze().detach().numpy()
    contact_list = torch.stack(foot_contact_list).squeeze().detach().numpy()
    phase_diff_list = torch.stack(phase_diff_list).squeeze().detach().numpy()
    swing_middle_list = torch.stack(swing_middle_list).squeeze().detach().numpy()

    mirror_x_list = torch.stack(mirror_x_list).squeeze().detach().numpy()
    mirror_y_list = torch.stack(mirror_y_list).squeeze().detach().numpy()
    mirror_encoder_list = torch.stack(mirror_encoder_list).squeeze().detach().numpy()
    mirror_phase_list = torch.stack(mirror_phase_list).squeeze().detach().numpy()
    mirror_foot_height_list = torch.stack(mirror_foot_height_list).squeeze().detach().numpy()
    mirror_contact_list = torch.stack(mirror_foot_contact_list).squeeze().detach().numpy()
    mirror_phase_diff_list = torch.stack(mirror_phase_diff_list).squeeze().detach().numpy()
    mirror_swing_middle_list = torch.stack(mirror_swing_middle_list).squeeze().detach().numpy()

    output_x_list = torch.stack(output_x_list).squeeze().detach().numpy()
    output_y_list = torch.stack(output_y_list).squeeze().detach().numpy()
    output_encoder_list = torch.stack(output_encoder_list).squeeze().detach().numpy()
    output_phase_list = torch.stack(output_phase_list).squeeze().detach().numpy()
    output_foot_height_list = torch.stack(output_foot_height_list).squeeze().detach().numpy()
    output_foot_contact_list = torch.stack(output_foot_contact_list).squeeze().detach().numpy()
    output_phase_diff_list = torch.stack(output_phase_diff_list).squeeze().detach().numpy()
    output_swing_middle_list = torch.stack(output_swing_middle_list).squeeze().detach().numpy()

    # subplots
    fig, axs = plt.subplots(8, 3, figsize=(12, 6))
    axs[0, 0].plot(time, x_list, label='x')
    axs[0, 0].legend()
    axs[1, 0].plot(time, y_list, label='y')
    axs[1, 0].legend()
    axs[2, 0].plot(time, encoder_list, label='encoder')
    axs[2, 0].legend()
    axs[2 + 1, 0].plot(time, phase_list, label='phase')
    axs[2 + 1, 0].legend()
    axs[3 + 1, 0].plot(time, foot_height_list, label='height')
    axs[3 + 1, 0].legend()
    axs[4 + 1, 0].plot(time, contact_list, label='contact')
    axs[4 + 1, 0].legend()
    axs[5 + 1, 0].plot(time, phase_diff_list, label='phase_diff_list')
    axs[5 + 1, 0].legend()
    axs[6 + 1, 0].plot(time, swing_middle_list, label='swing_middle')
    axs[6 + 1, 0].legend()

    axs[0, 1].plot(time, mirror_x_list, label='mirror_x')
    axs[0, 1].legend()
    axs[1, 1].plot(time, mirror_y_list, label='mirror_y')
    axs[1, 1].legend()
    axs[2, 1].plot(time, mirror_encoder_list, label='mirror_encoder')
    axs[2, 1].legend()
    axs[2 + 1, 1].plot(time, mirror_phase_list, label='mirror_phase')
    axs[2 + 1, 1].legend()
    axs[3 + 1, 1].plot(time, mirror_foot_height_list, label='mirror_height')
    axs[3 + 1, 1].legend()
    axs[4 + 1, 1].plot(time, mirror_contact_list, label='mirror_contact')
    axs[4 + 1, 1].legend()
    axs[5 + 1, 1].plot(time, mirror_phase_diff_list, label='mirror_phase_diff_list')
    axs[5 + 1, 1].legend()
    axs[6 + 1, 1].plot(time, mirror_swing_middle_list, label='mirror_swing_middle')
    axs[6 + 1, 1].legend()

    axs[0, 2].plot(time, output_x_list, label='output_x')
    axs[0, 2].legend()
    axs[1, 2].plot(time, output_y_list, label='output_y')
    axs[1, 2].legend()
    axs[2, 2].plot(time, output_encoder_list, label='output_encoder')
    axs[2, 2].legend()
    axs[2 + 1, 2].plot(time, output_phase_list, label='output_phase')
    axs[2 + 1, 2].legend()
    axs[3 + 1, 2].plot(time, output_foot_height_list, label='output_height')
    axs[3 + 1, 2].legend()
    axs[4 + 1, 2].plot(time, output_foot_contact_list, label='output_contact')
    axs[4 + 1, 2].legend()
    axs[5 + 1, 2].plot(time, output_phase_diff_list, label='output_phase_diff_list')
    axs[5 + 1, 2].legend()
    axs[6 + 1, 2].plot(time, output_swing_middle_list, label='output_swing_middle')
    axs[6 + 1, 2].legend()

    plt.xlabel('Time')
    plt.ylabel('x')
    plt.grid(True)
    plt.show()
