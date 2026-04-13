import math

import numpy
import torch

from .fi_tool_logger import Logger


class LowPassFilterNumpy:
    """
    Low pass filter class
    """

    def __init__(self, cutoff_freq, damping_ratio, dt, shape):
        self.cutoff_freq = cutoff_freq
        self.damping_ratio = damping_ratio
        self.dt = dt
        self.shape = shape
        self.omega = 2 * numpy.pi * cutoff_freq
        self.alpha = 2 * numpy.pi * cutoff_freq * damping_ratio
        self.beta = numpy.tan(self.alpha * dt / 2)
        self.gamma = self.beta / (1 + self.beta)
        self.prev_output = numpy.zeros(shape)

    def filter(self, input: numpy.ndarray) -> numpy.ndarray:
        output = self.gamma * input + (1 - self.gamma) * self.prev_output
        self.prev_output = output
        return output


class LowPassFilterTorch:
    """
    Low pass filter class
    """

    def __init__(self, cutoff_freq, damping_ratio, dt, shape):
        self.cutoff_freq = cutoff_freq
        self.damping_ratio = damping_ratio
        self.dt = dt
        self.shape = shape
        self.omega = 2 * torch.pi * cutoff_freq
        self.alpha = 2 * torch.pi * cutoff_freq * damping_ratio
        self.beta = numpy.tan(self.alpha * dt / 2)
        self.gamma = self.beta / (1 + self.beta)
        self.prev_output = torch.zeros(shape)

    def filter(self, input: torch.Tensor) -> torch.Tensor:
        output = self.gamma * input + (1 - self.gamma) * self.prev_output
        self.prev_output = output
        return output


# @torch.jit.script
def torch_low_pass_filter(input: torch.Tensor, prev_output: torch.Tensor, gamma: float) -> torch.Tensor:
    output = gamma * input + (1 - gamma) * prev_output
    return output


if __name__ == "__main__":
    import time

    input_data = torch.zeros((1, 23), dtype=torch.float32)
    output_data = torch.zeros((1, 23), dtype=torch.float32)

    for i in range(100):
        current_time = time.time()

        input_data = torch.ones((1, 23), dtype=torch.float32) * math.sin(i * 0.1)
        output_data = torch_low_pass_filter(input_data.clone().detach(), output_data.clone().detach(), 0.1)
        Logger().print_info("output_data = ", output_data)

        Logger().print_info(time.time() - current_time)

    # low_pass_filter = LowPassFilterTorch(cutoff_freq=50, damping_ratio=0.707, dt=0.02, shape=(1, 23))
    #
    # print("gamma = ", low_pass_filter.gamma)
    #
    # input_data = torch.zeros((1, 23), dtype=torch.float32)
    # output_data = low_pass_filter.filter(input_data)
    #
    # input_data_array = input_data.detach().numpy()
    # output_data_array = output_data.detach().numpy()
    #
    # for i in range(100):
    #     input_data = torch.ones((1, 23), dtype=torch.float32) * math.sin(i * 0.1)
    #     output_data = low_pass_filter.filter(input_data)
    #
    #     input_data_array = numpy.concatenate((input_data_array, input_data.detach().numpy()), axis=0)
    #     output_data_array = numpy.concatenate((output_data_array, output_data.detach().numpy()), axis=0)
    #
    # import matplotlib.pyplot as plt
    #
    # plt.plot(input_data_array)
    # plt.plot(output_data_array)
    # plt.legend(["input", "output"])
    # plt.show()
