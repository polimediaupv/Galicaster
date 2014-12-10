# -*- coding:utf-8 -*-
# Galicaster, Multistream Recorder and Player
#
#       galicaster/plugins/upv_leedscreen
#
# Copyright (c) 2014, Universitat Politècnica de València <polimedia@upvnet.upv.es>
#
# This work is licensed under the Creative Commons Attribution-
# NonCommercial-ShareAlike 3.0 Unported License. To view a copy of 
# this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California, 94105, USA.

from threading import Timer
from threading import _Timer
from os import path
from os import system

from galicaster.core import context

dispatcher = context.get_dispatcher()
conf = context.get_conf()
logger = context.get_logger()

timer_show = None
interval = conf.get_int('upv_ledscreen', 'interval') or 2
executable = conf.get('upv_ledscreen', 'executable') or '/home/mmedia/dcled/dcled'
device = conf.get('upv_ledscreen', 'device') or '/dev/ledscreen'
disable = conf.get_boolean('upv_ledscreen', 'disable')

class RepeatingTimer(object):
    def __init__(self,interval, function, *args, **kwargs):
        super(RepeatingTimer, self).__init__()
	self.args = args
	self.kwargs = kwargs
	self.function = function
	self.interval = interval

    def start(self):
	self.callback()

    def stop(self):
	self.interval = False

    def callback(self):
	if self.interval:
	    self.function(*self.args, **self.kwargs)
            Timer(self.interval, self.callback, ).start()

def init():
    dispatcher.connect("galicaster-notify-quit", do_stop_timers)
    dispatcher.connect('starting-record', create_timer)
    dispatcher.connect('restart-preview', do_stop_timers)

def create_timer(sender=None):
    global timer_show
    do_stop_timers()
    if not disable and path.islink(device) and path.isfile(executable):
        timer_show = RepeatingTimer(interval, show_message)
        timer_show.start()
        logger.debug("Init Timer to show messages every {} seconds".format(interval))

def show_message(sender=None):
    command = '%s -f -m " REC"' % (executable)
    system(command)

def do_stop_timers(sender=None):
    global timer_show
    if isinstance(timer_show, RepeatingTimer):
        timer_show.stop()
        logger.debug("Reset Show Timer")

