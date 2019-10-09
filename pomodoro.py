#!/usr/bin/env python3

import os
# Removes pygame welcome message. Simply just to remove clutter as this
# Is a terminal program and doesn't make use of a GUI.
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import argparse
from sys import platform, exit
import subprocess
from pushbullet import PushBullet


'''
Pomodoro Timer

Author: Tristan
Date: 08/10/2019

Inspired from the PyBite Challenge to write a pomodoro timer.

Features:
    - Basic sprint times, break times, and iteration counts.
    - PushBullet API intergration for phone notifications.
    - Linux notify-send notifications.
    - Basic sounds.
    - Sprint and break extensions.
'''


def flash_terminal_on():
    '''Turns terminal to reverse display mode if on linux'''

    if platform.startswith('linux'):
        subprocess.run(['printf', '\\e[?5h'])

def flash_terminal_off():
    '''Turns terminal to normal display mode if on linux'''

    if platform.startswith('linux'):
        subprocess.run(['printf', '\\e[?5l'])

def send_notifcation(message):
    '''Uses notify-send to display notification if on linux'''

    if platform.startswith('linux'):
        subprocess.run(['notify-send', str(message), '-a', 'Pomodoro Timer',
                        '-i', 'icon.png'])




class PomodoroTimer:
    '''
    PomodoroTimer

    Args:
        **s_time: Sprint time in minutes.
        **b_time: Break time in minutes.
        **iterations: Iterations count.
        **push_bullet: PushBullet API key.

    Attributes:
        break_time_sound: PyGame sound to play at start of break time.
        sprint_time_sound: PyGame sound to play at start of sprint time.

        clock: PyGame clock.
        tick_speed: Ticks per second to run.
        counter: Timer (ms) that tracks current progress through sprint or break.
        run_time: Overall (ms) run time of the Pomodoro Timer.

        in_sprint: Are we currently in a sprint.
        sprint_time: Sprint length (ms)
        break_time: Break length (ms)

        max_iterations: How many iterations to run.
        iterations: Current iteration

        pb: PushBullet object.
    '''

    def __init__(self, s_time=20, b_time=5, iterations=5, push_bullet=None):

        self.break_time_sound = pygame.mixer.Sound('breaktime.wav')
        self.sprint_time_sound = pygame.mixer.Sound('sprinttime.wav')

        self.clock = pygame.time.Clock()
        self.tick_speed = 1.5
        self.counter = 0   # Tracks progress of current sprint or break
        self.run_time = 0  # Tracks progress of entire process

        # In minutes
        self.in_sprint = True
        self.sprint_time = s_time * 60 * 1000
        self.break_time = b_time * 60 * 1000

        # Amount of times to iterate process
        self.max_iterations = iterations
        self.iterations = 0

        self.pb = None
        if push_bullet:
            self.pb = PushBullet(push_bullet)

        self.print_welcome()

    def print_welcome(self):
        '''Print welcome message and display some variables'''

        # Get a boolean var on whether Push Bullet has been initted
        if self.pb is not None:
            push_bullet = True
        else:
            push_bullet = False

        print(' Welcome to Pomodoro!\n----------------------')
        # Display variables
        print('Sprint time:\t{} minute(s)\nBreak time:\t{} minute(s)\nIterations:\t{}\nPushBullet?\t{}\nTick Speed:\t{}\n'.format(
              int(self.sprint_time / 60 / 1000),
              int(self.break_time / 60 / 1000),
              self.max_iterations,
              push_bullet,
              self.tick_speed
        ))
        print('Press enter to start your first {} minute sprint...'.format(
            int(self.sprint_time / 60 / 1000)
        ))
        input()
        print('Let\'s Go!')

    def tick(self):
        '''Update counter and check if sprint or break time has been finished'''

        dt = self.clock.tick(self.tick_speed)
        self.run_time += dt
        self.counter += dt

        if self.in_sprint:
            if self.counter > self.sprint_time:
                self.start_break()
        else:
            if self.counter > self.break_time:
                self.start_sprint()


    def start_break(self, wait=True):
        '''Starts break and resets variables for next sprint'''

        flash_terminal_on()
        send_notifcation('Time to start your break, confirm in terminal...')
        if type(self.pb) is PushBullet:
            self.pb.push_note('Break Time!', 'It is time for your break, come back to start the timer.')
        self.break_time_sound.play()
        extend_time = input('Start Break? (or extend your sprint by?)')
        flash_terminal_off()
        if extend_time:
            self.extend(int(extend_time))
            return
        print('Starting Break for {} minute(s).'.format(int(self.break_time / 1000 / 60)))
        self.in_sprint = False
        self.counter = 0

    def start_sprint(self, wait=True):
        '''Starts a new sprint and sets up for next break'''

        flash_terminal_on()
        send_notifcation('Time to start your sprint, confirm in terminal...')
        if type(self.pb) is PushBullet:
            self.pb.push_note('Sprint Time!', 'It is time for your sprint, come back to start the timer.')
        self.sprint_time_sound.play()
        extend_time = input('Start Sprint? (or extend your break by?) ')
        flash_terminal_off()
        if extend_time:
            self.extend(int(extend_time))
            return
        print('Starting Sprint for {} minute(s).'.format(int(self.sprint_time / 1000 / 60)))
        self.in_sprint = True
        self.counter = 0
        self.iterations += 1

    def extend(self, time):
        '''Extends sprint or break by a given time'''

        if self.in_sprint:
            self.counter = self.sprint_time - (time * 60 * 1000)
            print('Your sprint has been extended by {} minutes.'.format(time))
        else:
            self.counter = self.break_time - (time * 60 * 1000)
            print('Your break has been extended by {} minutes.'.format(time))

    def run(self):
        '''Main run function'''

        while self.iterations <= self.max_iterations:
            self.tick()
        print('You have finished all iterations of your sprint. Goodbye :)')
        pygame.quit()
        exit()




if __name__ == '__main__':

    # Setup all arguments and parse them
    parser = argparse.ArgumentParser(prog='pomodoro',
                                     description='A simple Pomodoro Timer')
    parser.add_argument('--sprint_time', action='store',
                                         type=float,
                                         help='Time in minutes for the sprints to run.',
                                         default=20)
    parser.add_argument('--break_time', action='store',
                                        type=float,
                                        help='Time in minutes for breaks to run.',
                                        default=5)
    parser.add_argument('--iterations', action='store',
                                        type=int,
                                        help='Number of iterations',
                                        default=5)
    parser.add_argument('--pushbullet', action='store',
                                        type=str,
                                        help='Push Bullet API key.')

    args = parser.parse_args()

    # Attempt to retrieve push bullet API key
    pb = args.pushbullet
    pbval = pb
    # Try default push bullet file
    if pbval.lower() == 'f' or pbval.lower() == 'false':
        pbval = None
    elif pb is None and os.path.isfile('pushbullet.txt'):
        with open('pushbullet.txt') as f:
            pbval = f.read().strip('\n')
    # Has the user given an alternative api key file
    elif pb is not None and os.path.isfile(pb):
        with open(pb) as f:
            pbval = f.read().strip('\n')

    pygame.mixer.init()
    try:
        p = PomodoroTimer(s_time=args.sprint_time,
                          b_time=args.break_time,
                          iterations=args.iterations,
                          push_bullet=pbval)
        p.run()
    except KeyboardInterrupt:
        print('Goodbye :)')
        exit()
