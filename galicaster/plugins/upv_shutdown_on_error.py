# -*- coding:utf-8 -*-
# Galicaster, Multistream Recorder and Player
#
#       galicaster/plugins/upv_shutdown_on_error
#
# Copyright (c) 2012, Teltek Video Research <galicaster@teltek.es>
#
# This work is licensed under the Creative Commons Attribution-
# NonCommercial-ShareAlike 3.0 Unported License. To view a copy of 
# this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California, 94105, USA.

"""
"""

import datetime
import os
import sys

from galicaster.core import context

logger = context.get_logger()


def init():
    try:
        dispatcher = context.get_dispatcher()
        dispatcher.connect('recorder-error', restart_galicaster)
        
    except ValueError:
        pass


def restart_galicaster(self, error_message):
    if error_message.startswith("Internal GStreamer error: negotiation problem"):
        logger.info("GStreamer error: " + error_message)
        galicaster_kill_script = os.path.abspath(os.path.dirname(sys.argv[0])) + "/contrib/scripts/kill_gc"
        if not os.path.isfile(galicaster_kill_script):
            logger.info("Galicaster can not be killed. script not found: " + galicaster_kill_script)
        else:
            logger.info("Killing Galicaster")
            os.system(galicaster_kill_script)
