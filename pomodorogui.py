#!/usr/bin/env python3

import pygame
from sys import exit
from pomodoro import PomodoroTimer


class PomodoroGUI:

    def __init__(self):

        self.running = True
        self.surface = pygame.display.set_mode((250, 150))
        pygame.display.set_caption('Pomodoro Timer')

        self.timer = PomodoroTimer()
        self.timer_running = False

    def update(self):

        if self.timer_running:
            timer.tick()

    def draw(self):

        pygame.display.update()

    def run(self):

        while self.running:
            self.update()
            self.draw()


if __name__ == '__main__':

    pygame.init()
    PomodoroGUI().run()
