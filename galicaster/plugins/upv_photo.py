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

import sys, traceback
import gst
import os
import shutil
from galicaster.core import context
from galicaster.mediapackage import mediapackage

logger = context.get_logger()
worker = context.get_worker()
conf = context.get_conf()
repository = context.get_repository()
rectemp = repository.get_rectemp_path()

# config parameters
videoencoder = conf.get('upv_photo', 'videoencoder') or "jpegenc"
device = conf.get('upv_photo', 'device') or "/dev/blackboard"
photo_interval = conf.get_int('upv_photo', 'photo_interval') or 30
filenames = conf.get('upv_photo', 'filenames') or "blackboard_%06d.jpg"
mimetype = conf.get('upv_photo', 'mimetype') or "image/jpeg"
flavour = conf.get('upv_photo', 'flavour') or "blackboard"


# gstreamer pipeline
pipe = gst.Pipeline("upv_photo")

pipestr = (' v4l2src name=gc-photo-src ! queue ! '
           ' ffmpegcolorspace ! gc-photo-vrate ! '
           ' queue ! ffmpegcolorspace ! queue ! '
           ' gc-photo-enc ! queue ! multifilesink name=gc-photo-sink')


def init():
	try:
		vrate_caps = 'videorate ! video/x-raw-yuv,framerate=1/%s' % (str(photo_interval))	
		full_filenames = os.path.join(rectemp, filenames)
		
		aux = (pipestr.replace('gc-photo-enc', videoencoder)
						.replace('gc-photo-vrate', vrate_caps))		
		bin = gst.parse_launch("( {} )".format(aux))
				
		bin.get_by_name('gc-photo-src').set_property("device", "{0}".format(device))
		bin.get_by_name('gc-photo-sink').set_property("location", "{0}".format(full_filenames))
				
		pipe.add(bin)
		pipe.set_state(gst.STATE_PAUSED)
		
		dispatcher = context.get_dispatcher()
		dispatcher.connect('starting-record', record)
		dispatcher.connect('restart-preview', stop)		
		dispatcher.connect('upv-mediapackage-finished', collect_images)		
	except:
	    traceback.print_exc(file=sys.stdout)




def record(self):
	# start recording
	pipe.get_by_name('gc-photo-sink').set_property("index", 0)
	pipe.set_state(gst.STATE_PLAYING)


def stop(self):
	# stop recording
	pipe.set_state(gst.STATE_NULL)
	pipe.set_state(gst.STATE_PAUSED)


def collect_images(source, mp):
	name, extension = os.path.splitext(filenames)
	offset = name.find('%')
	start = name[:offset]
	for f in os.listdir(rectemp):
		if f.startswith(start) and f.endswith(extension):
			index = f[offset:].replace(extension,'')
			delta = int(index) * photo_interval
			minutes, seconds = divmod(delta, 60)  
			hour, minutes = divmod(minutes, 60)
			ref = "track:undefined;time=T%02d:%02d:%02d:0F1000" % (hour, minutes, seconds)
			filename = os.path.join(rectemp, f)
			dest = os.path.join(mp.getURI(), os.path.basename(filename))
			os.rename(filename, dest)
			mp.add(dest, mediapackage.TYPE_ATTACHMENT, flavour+'/source', mimetype, None, ref)
	repository.update(mp);
