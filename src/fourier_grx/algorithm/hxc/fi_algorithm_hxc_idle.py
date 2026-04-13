import numpy

from fourier_core.predefine import *

from fourier_grx.algorithm.hxc.fi_algorithm_hxc_base import (
    AlgorithmHXCBaseControlModel,
)


class AlgorithmHXCIdleControlModel(AlgorithmHXCBaseControlModel):
    def __init__(self):
        super().__init__()

    def run(self, **kwargs):
        pass
