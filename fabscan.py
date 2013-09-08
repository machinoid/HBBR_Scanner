#!/usr/bin/env python
#
#   www.combinatorialdesign.com
#
#   Copyright 2013 Pawel Wodnicki
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/
 

import sys
import os
import sys
import time
import serial
import subprocess
from threading import Thread
from collections import deque
#from time import sleep


port = "/dev/ttyUSB0"
baudrate = 9600

# FabScan protocol
# FabScan - http://hci.rwth-aachen.de/fabscan
# 
#  by Francis Engelmann
#  Copyright 2011 Media Computing Group, RWTH Aachen University. All rights reserved.
TURN_LASER_OFF =      200
TURN_LASER_ON  =      201
PERFORM_STEP   =      202
SET_DIRECTION_CW  =   203
SET_DIRECTION_CCW =   204
TURN_STEPPER_ON   =   205
TURN_STEPPER_OFF  =   206
TURN_LIGHT_ON     =   207
TURN_LIGHT_OFF    =   208
ROTATE_LASER      =   209
FABSCAN_PING      =   210
FABSCAN_PONG      =   211
SELECT_STEPPER    =   212
LASER_STEPPER     =  11
TURNTABLE_STEPPER =  10
#the protocol: we send one byte to define the action what to do.
#If the action is unary (like turnung off the light) we only need one byte so we are fine.
#If we want to tell the stepper to turn, a second byte is used to specify the number of steps.
#These second bytes are defined here below.

ACTION_BYTE      =      1    #normal byte, first of new action
LIGHT_INTENSITY  =      2
TURN_TABLE_STEPS =      3
LASER1_STEPS     =      4
LASER2_STEPS     =      5
LASER_ROTATION   =      6
STEPPER_ID       =      7

# Same as commands
LASER_OFF =          200
LASER_ON  =          201
DIRECTION_CW  =      203
DIRECTION_CCW =      204


class FabScanTurnTable():
    def __init__(self, *largs, **kwargs):
#        super(FabScanTurnTable, self).__init__()
        self.degreesPerStep = 0.0176 #the size of a microstep
        #self.degreesPerStep = 360.0/200.0/16.0 #the size of a microstep
        self.direction = SET_DIRECTION_CW
        self.rotation = 0.0
        self.laser = LASER_ON 
	self.serial = None
        self.quit = False


    def write_cmd(self,cmd, num):
        if self.serial is not None:
           if self.serial.isOpen():
#               print cmd[0:num]
               ba = bytearray(cmd[0:num])
               self.serial.write(ba)
           else:
               print('Serial is not opened')
        else:
               print('Serial is not connected')

    def select_stepper(self):
        cmd[SELECT_STEPPER, TURNTABLE_STEPPER]
        self.write_cmd(c,2)

    def set_direction(self, d):
        cmd=[None]
        self.direction = d
        if d == DIRECTION_CW:
            cmd=[SET_DIRECTION_CW]
        else:
            cmd=[SET_DIRECTION_CCW]
        self.write_cmd(cmd,1)

    def toggle_direction(self):
        if self.direction == DIRECTION_CW:
            self.set_direction[DIRECTION_CCW]
        else:
            self.set_direction[DIRECTION_CW]

    def enable(self):
        cmd[TURN_STEPPER_ON]
        self.write_cmd(cmd,1)

    def disable(self):
        cmd[TURN_STEPPER_OFF]
        self.write_cmd(cmd,1)

    def turn_by_n_steps(self, steps):
        print('size ' + str(steps))
        c=[None]*1024
        s = steps
        i = 0
        while(i<=int(steps/255)):
            c[2*i]=PERFORM_STEP
            if s < 256:
                c[2*i+1]=int(s%256)
            else:
               c[2*i+1]=int(255)
               s-=255
            i+=1
        #print i
        #print c
        # we need to send i*2 charcters
        self.write_cmd(c,i*2)


    def turn_by_angle(self, angle):
        steps = int(angle/self.degreesPerStep)
        if(self.direction==SET_DIRECTION_CW):
          self.rotation -= angle
        elif (self.direction==SET_DIRECTION_CCW):
          self.rotation += angle
        self.turn_by_n_steps(steps)

    def laser_on(self):
        cmd=[TURN_LASER_ON]
        self.write_cmd(cmd,1)
        self.laser = LASER_ON
        print('laser turned on')

    def laser_off(self):
        cmd=[TURN_LASER_OFF]
        self.write_cmd(cmd,1)
        self.laser = LASER_OFF
        print('laser turned off')


    def on_connect(self,port):
         self.serial = serial.Serial(port, baudrate, timeout=3)
         print('serial opened')
         

if __name__ == '__main__':
    import sys
    import os


