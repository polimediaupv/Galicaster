#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Galicaster, Multistream Recorder and Player
#
#       run_dashboard_push
#
# Copyright (c) 2011, Teltek Video Research <galicaster@teltek.es>
#
# This work is licensed under the Creative Commons Attribution-
# NonCommercial-ShareAlike 3.0 Unported License. To view a copy of 
# this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California, 94105, USA.

import os
import sys
import gtk
from StringIO import StringIO
import pycurl
import time


import sys

path = os.environ.get('GALICASTER_PATH', '/usr/share/galicaster')
sys.path.insert(0, path)
from galicaster.core import context

sleep_period = 60

def get_screenshot():
    """makes screenshot of the current root window, yields gtk.Pixbuf"""
    window = gtk.gdk.get_default_root_window()
    size = window.get_size()
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, size[0], size[1])
    pixbuf.get_from_drawable(window, window.get_colormap(),
                                    0, 0, 0, 0, size[0], size[1])
    b = StringIO()
    pixbuf.save_to_callback(b.write, 'png')
    return b.getvalue()    


def push_pic(sender=None):
    conf = context.get_conf()
    mhclient = context.get_mhclient()

    endpoint = "/dashboard/rest/agents/{hostname}/snapshot.png".format(hostname=conf.hostname)
    postfield = [ ("snapshot", get_screenshot() ) ]
    
    try:
        aux = mhclient._MHHTTPClient__call('POST', endpoint, {}, {}, postfield, False, None, False)
    except IOError as e:
        # This endpoint return 204, not 200.
        aux = None
        
    return aux


if __name__ == '__main__':
   while True:
       print "." 
       push_pic()      
       time.sleep(sleep_period)
   sys.exit(0) 
