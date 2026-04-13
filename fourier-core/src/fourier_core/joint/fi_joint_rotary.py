from fourier_core.joint.fi_joint_base import JointBase


class JointRotary(JointBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.id = kwargs.get('id', 'joint_rotary')
