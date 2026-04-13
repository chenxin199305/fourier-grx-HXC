import sys

import pygame
from fourier_core.logger import *
from fourier_core.predefine import *

from .fi_peripheral_keyboard import PeripheralKeyboard


class PeripheralKeyboardPygame(PeripheralKeyboard):
    def __init__(self):
        super(PeripheralKeyboardPygame, self).__init__()

        result = pygame.init()
        Logger().print_info("pygame.init() result: " + str(result))

        # os.environ["SDL_VIDEODRIVER"] = "dummy"  # or maybe 'fbcon'
        # result = pygame.display.init()

        # 使用 keyboard 进行输入，必须要创建一个窗口，否则无法获取输入
        screen = pygame.display.set_mode((1, 1))  # 使用 pygame.display.set_mode() 创建一个窗口
        Logger().print_info("pygame.display.init() result: " + str(result))

        self.keyboard_up = 0
        self.keyboard_down = 0
        self.keyboard_enter = 0
        self.keyboard_esc = 0

        self.keyboard_up_last = 0
        self.keyboard_down_last = 0
        self.keyboard_enter_last = 0
        self.keyboard_esc_last = 0

    def upload(self):
        self.keyboard_up_last = self.keyboard_up
        self.keyboard_down_last = self.keyboard_down
        self.keyboard_enter_last = self.keyboard_enter
        self.keyboard_esc_last = self.keyboard_esc

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # checking if keydown event happened or not
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    # print("Key UP has been pressed")
                    self.keyboard_up = 1

                if event.key == pygame.K_DOWN:
                    # print("Key DOWN has been pressed")
                    self.keyboard_down = 1

                if event.key == pygame.K_RETURN:
                    # print("Key RETURN has been pressed")
                    self.keyboard_enter = 1

                if event.key == pygame.K_ESCAPE:
                    # print("Key ESCAPE has been pressed")
                    self.keyboard_esc = 1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    # print("Key UP has been released")
                    self.keyboard_up = 0

                if event.key == pygame.K_DOWN:
                    # print("Key DOWN has been released")
                    self.keyboard_down = 0

                if event.key == pygame.K_RETURN:
                    # print("Key RETURN has been released")
                    self.keyboard_enter = 0

                if event.key == pygame.K_ESCAPE:
                    # print("Key ESCAPE has been released")
                    self.keyboard_esc = 0

        return FunctionResult.SUCCESS
