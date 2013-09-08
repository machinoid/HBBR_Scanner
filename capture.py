#!/usr/bin/python
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
from sys import platform as _platform

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, OptionProperty, \
        ListProperty, NumericProperty, AliasProperty

# Use fabscan
import fabscan as Table
from fabscan import FabScanTurnTable as TurnTable
port = ""



class Scanner(Thread):
    EXIT         = -1
    DO_NOTHING   = 0
    DO_DONE      = 1
    GRAB_IMAGE   = 2
    DETECT_LASER = 3
    SCAN_START   = 4
    SCAN_RUN     = 5
    SCAN_STOP    = 6
    ROTATE_LEFT  = 7
    ROTATE_RIGHT = 8

    def __init__(self, *largs, **kwargs):
#        super(Thread, self).__init__(*largs, **kwargs)
        super(Scanner, self).__init__()

	self.table = None
	self.laser_angle = 0.0
	self.quit = False
	self.name = 'image'
	self.do = Scanner.DO_NOTHING
	self.texture = None
	self.camera = None
	self.controller = None
	self.scan_cnt  = 0
	self.scan_max_cnt = 0


    def grab_texture(self, texture, name):
         texture.save(name)
         print('Grab '+name+'.png')
  
    def run(self):
        while not self.quit:
           time.sleep(.1)
           if self.do == Scanner.EXIT:
              break
           # grab laser image
           if self.do == Scanner.DETECT_LASER:
              print('Detect laser - start')
              laser = self.get_laser()
              self.laser_off()
              time.sleep(2)
              self.controller.on_grab(False,'_laser_off')
              self.laser_on()
              time.sleep(2)
              self.controller.on_grab(False,'_laser_on')
              if laser == Table.LASER_ON:
                 self.laser_on()
              else:
                 self.laser_off()
              self.do = Scanner.DO_DONE
              time.sleep(2)
              # create scan settings
              cmd=['python','scan_settings.py', self.controller.get_current_image_name_root()]
              print str(cmd)
              try:
                  subprocess.call(cmd)
#                  subprocess.check_call([cmd, self.name])
              except subprocess.CalledProcessError:
                  print("CalledProcessError")
                  pass # handle errors in the called executable
              except OSError as e:
                  print e.errno
                  print e.filename
                  print e.strerror
                  print("OSError")
                  pass # executable not found
              # detect lines
              cmd=['python','houghlines.py', self.controller.get_current_image_name_root()]
              print str(cmd)
              try:
                  subprocess.call(cmd)
#                  subprocess.check_call([cmd, self.name])
              except subprocess.CalledProcessError:
                  print("CalledProcessError")
                  pass # handle errors in the called executable
              except OSError as e:
                  print e.errno
                  print e.filename
                  print e.strerror
                  print("OSError")
                  pass # executable not found
              print('Detect laser - done')
              # process

           if self.do == Scanner.SCAN_START:
              print('Scan - start')
              laser = self.get_laser()
              self.scan_cnt  = 0
              self.scan_max_cnt = int (360 / float(self.controller.table_step)) - 1
              print("Max scan steps "+str(self.scan_max_cnt))
              self.do = Scanner.SCAN_RUN

           if self.do == Scanner.SCAN_RUN:
              
              self.laser_off()
              time.sleep(1)         
              self.controller.on_grab(True,'_laser_off')
              self.laser_on()
              time.sleep(1)
              self.controller.on_grab(True,'_laser_on')
              self.controller.on_turn_right()
              time.sleep(1 + float(self.controller.table_step)/2) # wait 5s for 10 degrees of table movement

              # increment counters
              self.controller.increment_image_cnt()
              print('Step '+str(self.scan_cnt))
              self.scan_cnt  +=1
              if self.scan_cnt > self.scan_max_cnt:
                  self.do = Scanner.DO_DONE

           if self.do == Scanner.SCAN_STOP:
               self.do = Scanner.DO_DONE

           if self.do == Scanner.DO_DONE:
               print('Done')
               self.do = Scanner.DO_NOTHING

    def set_direction(self, d):
        if self.table is not None:
            if d == Scanner.ROTATE_LEFT:
               self.table.set_direction(Table.DIRECTION_CCW)

            if d == Scanner.ROTATE_RIGHT:
                self.table.set_direction(Table.DIRECTION_CW)

    def toggle_direction(self):
        if self.table is not None:
            self.table.toggle_direction(d)

    def enable(self):
        if self.table is not None:
            self.table.enable()

    def disable(self):
        if self.table is not None:
            self.table.disable()

    def turn_by_n_steps(self, steps):
        if self.table is not None:
            self.table.turn_by_n_steps(steps)

    def turn_by_angle(self, angle):
        if self.table is not None:
            self.table.turn_by_angle(angle)

    def laser_on(self):
        if self.table is not None:
            self.table.laser_on()

    def laser_off(self):
        if self.table is not None:
            self.table.laser_off()

    def toggle_laser(self):
        if self.table is not None:
            if self.table.laser == Table.LASER_ON:
                self.table.laser_off()
            else:
                self.table.laser_on()

    def get_laser(self):
        if self.table is not None:
            return self.table.laser
        return Table.LASER_OFF


    def get_laser_angle(self):
         return self.laser_angle

    def on_connect(self, port):
         self.table = Table.FabScanTurnTable()
         self.table.on_connect(port)
         print('scanner opened')
         


# using ids to identify widgets
# https://github.com/kivy/kivy/pull/812

class CaptureController(BoxLayout):
    # properties
    port=StringProperty('')
    scan_name=StringProperty('User')
    image_name=StringProperty('image')
    image_counter=StringProperty('00000')
    table_angle=StringProperty('0')
    table_step=StringProperty('+10.0')
    laser_angle=StringProperty('0')

    def __init__(self, **kwargs):
	self.scanner = Scanner();
        self.scanner.controller = self
        self.scanner.start()
        super(BoxLayout, self).__init__(**kwargs)
        self.scan_name = 'User'
        self.image_name = 'image'
        self.image_usecnt = True
        self.image_postfix =''
        self.image_action = Scanner.DO_NOTHING
         #!!! interval should be tuned to computer speed
        Clock.schedule_interval(self.grab_image_callback, 1 / 4)
        # sanity debug
        print('ids' + str(self.ids))

    def on_port(self, instance, value):
        self.port = value
        print('port changed to ' + value)

    # propeties handling
    def on_scan_name(self, instance, value):
        self.scan_name = value

        # 'User' - use current table_step
        if self.scan_name == 'Poor':
            self.table_step = '0.40'
  
        if self.scan_name == 'Normal':
            self.table_step = '0.20'

        if self.scan_name == 'Good':
            self.table_step = '0.10'

        if self.scan_name == 'Best':
            self.table_step = '0.05'

        print('scan_name changed to ' + value)

    def on_image_name(self, instance, value):
        self.image_name = value
        print('image_name changed to ' + value)

    def on_image_counter(self, instance, value):
        v = 0
        try:
           v = int(value)
        except:
           v = 0
        self.image_counter ="{:0>5d}".format(v)   
        print('image_counter changed to '+self.image_counter)

    def on_table_angle(self, instance, value):
        v = 0.0
        try:
           v = float(value)
        except:
           v = 0.0

        if v<0.0:
            v=360.0 + v
        if v>=360.0:
            v=v - 360.0

        self.table_angle ="{:.2f}".format(v)   
        print('table_angle changed to '+self.table_angle)

    def on_table_step(self, instance, value):
        v = 0.0
        try:
           v = float(value)
        except:
           v = 10.0

        if v<0.0:
            v=0.0
        if v>90.0:
            v=90.0
  
        self.table_step ="{:.2f}".format(v)   
        print('table_step changed to '+self.table_step)

    def on_laser_angle(self, instance, value):
        v = 0.0
        try:
           v = float(value)
        except:
           v = 0.0

        if v<0.0:
            v=0.0
        if v>180:
            v=180.0

        self.laser_angle ="{:.2f}".format(v)   
        print('laser_angle changed to '+self.laser_angle)

    def get_current_image_name_root(self):
        return self.image_name

    def get_current_image_name_with_cnt(self):
        return self.image_name+'_'+self.image_counter

    def get_current_image_name(self):
        if self.image_usecnt:
            return self.image_name+'_'+self.image_counter+self.image_postfix+'.png'
        else:
            return self.image_name+self.image_postfix+'.png'

    def reset_image_cnt(self):
        self.controller.image_counter = "{:0>5d}".format(0)

    def increment_image_cnt(self):
        cnt = int(self.image_counter) + 1
        self.image_counter = "{:0>5d}".format(cnt)

    # callbacks
    def grab_image_callback(self,dt):
        if self.image_action == Scanner.GRAB_IMAGE :
            self.mycamera.texture.save(self.get_current_image_name())
            self.image_action = Scanner.DO_DONE
 
    def on_connect(self):
         self.scanner.on_connect(self.port)

    def on_grab(self, usecnt, postfix):
        if self.image_action == Scanner.DO_NOTHING or  self.image_action == Scanner.DO_DONE:
            self.image_usecnt = usecnt
            self.image_postfix = postfix
            self.image_action = Scanner.GRAB_IMAGE
        print('Grab '+ self.image_name)

    def on_turn_left(self):
         self.scanner.set_direction(Scanner.ROTATE_LEFT)
         self.scanner.turn_by_angle(float(self.table_step))
         self.table_angle = "{:+.2f}".format(float(self.table_angle) - float(self.table_step))
         print('table turned left')

    def on_turn_right(self):
         self.scanner.set_direction(Scanner.ROTATE_RIGHT)
         self.scanner.turn_by_angle(float(self.table_step))
         self.table_angle = "{:+.2f}".format(float(self.table_angle) - float(self.table_step))
         print('table turned right')

    def on_toggle_laser(self):
        self.scanner.toggle_laser()

    # capturing camera from a separate thread does not work
    # looks like camera texture save must be synchronus with mainloop?
    # we could have an event that fires every 1/15 of a second and stores camera frame in image buffer?
    # or have a callback and a state machine
    def on_detect_laser(self):
        self.scanner.do = Scanner.DETECT_LASER
        # process

    def on_start(self):
        self.scanner.do = Scanner.SCAN_START
        # process

    def on_stop(self):
        self.scanner.do = Scanner.SCAN_STOP

    def on_exit(self):
        self.scanner.do = Scanner.SCAN_STOP
        time.sleep(.2)
        self.scanner.do = Scanner.EXIT


class CaptureApp(App):
    controller = None
    def _print_fps(self, *largs):
        print('FPS: %2.4f (real draw: %d)' % (
            Clock.get_fps(), Clock.get_rfps()))

    def _reload_keypress(self, instance, code, *largs):
        if code != 286:
            return
        for child in Window.children[:]:
            Window.remove_widget(child)
        root = Builder.load_file(self.options['filename'])
        Window.add_widget(root)

    def build(self):
	if _platform == "linux" or _platform == "linux2":
		# linux
		port = "/dev/ttyUSB0"
	elif _platform == "darwin":
		# OS X
		port = "/dev/ttyUSB0"
	elif _platform == "win32":
		port = "COM"
    # Windows...
#        Clock.schedule_interval(self._print_fps, 1)
        Window.bind(on_keyboard=self._reload_keypress)
        self.controller = CaptureController()
	self.controller.port = port
	return self.controller


    def on_stop(self):
        self.controller.on_exit()

         

if __name__ == '__main__':
    import sys
    import os

#    if len(sys.argv) < 2:
#        print('Usage: %s filename.kv' % os.path.basename(sys.argv[0]))
#        sys.exit(1)
    CaptureApp(filename="capture.kv").run()
#    CaptureApp(filename=sys.argv[1]).run()
