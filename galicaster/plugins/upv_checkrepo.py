# -*- coding:utf-8 -*-
# Galicaster, Multistream Recorder and Player
#
#       galicaster/plugins/upv_checkrepo
#
# Copyright (c) 2012, Teltek Video Research <galicaster@teltek.es>
#
# This work is licensed under the Creative Commons Attribution-
# NonCommercial-ShareAlike 3.0 Unported License. To view a copy of 
# this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California, 94105, USA.

"""This plugin check repository mediapackages. If anyone it's SCHEDULED when must be RECORDING, change start_time and duration, then start recording
"""

import datetime
import os
import sys
import shutil

from galicaster.core import context
from galicaster.mediapackage import mediapackage

logger = context.get_logger()
worker = context.get_worker()
conf = context.get_conf()



def init():
    try:
        dispatcher = context.get_dispatcher()
        dispatcher.connect('after-process-ical', check_repository)  
        dispatcher.connect('upv-mediapackage-finished', merge_recordings)
        
    except ValueError:
        pass


def merge_recordings(self, mp):
    mpUri = mp.getURI()
    repo = context.get_repository()
    rectemp = repo.get_rectemp_path()
    
    
    if (mp.manual):
        logger.debug("Manual recording. Do nothing!")
    else:
        check_repo_file = os.path.join(mpUri, "CHECK_REPO")
        if os.path.isfile(check_repo_file):
            # Checking Temporals
            logger.info("Checking temporals for " + mpUri)
            timesfile = open(check_repo_file, "r")
            times = timesfile.readline().split(',')
            timesfile.close()
            start = datetime.datetime.strptime(times[0], "%Y-%m-%d %H:%M:%S")
            end = datetime.datetime.strptime(times[1], "%Y-%m-%d %H:%M:%S")
            
            rectemp = repo.get_rectemp_path()
            for fname in os.listdir(rectemp):
                filepath = os.path.join(rectemp, fname)
                if os.path.isdir(filepath):
                    timestamp = os.path.getmtime(filepath)
                    time = datetime.datetime.utcfromtimestamp(timestamp)
                    if start < time and end > time:
                        dst = os.path.join(mpUri, os.path.basename(filepath))
                        try:
                            logger.info("Move " + filepath + " to " + dst)
                            shutil.move(filepath, dst)
                        except:
                            logger.error("Error moving " + filepath + " to " + dst)
            # Moving last recording as failed!
            backup_dir = os.path.join(mpUri, datetime.datetime.now().replace(microsecond=0).isoformat())
            logger.info("Moving last recording to " + backup_dir)
            if not os.path.isdir(backup_dir):
                os.mkdir(backup_dir)
            for track in mp.getTracks():
                try:
                    shutil.move(track.getURI(), backup_dir)
                except:
                    logger.info("Error moving " + track.getURI() + " to " + backup_dir)
                    pass



def check_repository(self):
    #mp_list is collection of mediapackages ID's
    if context.get_state().is_recording:
        return
    mp_list = context.get_repository()

    for uid,mp in mp_list.iteritems():
        if (not mp.manual):
            start = mp.getDate()
            end = start + datetime.timedelta(seconds=(mp.getDuration()/1000))
            if mp.status == mediapackage.SCHEDULED and start < datetime.datetime.utcnow() and end > datetime.datetime.utcnow():
                dest = os.path.join(mp.getURI(),"CHECK_REPO")
                if not os.path.isfile(dest):
                    repocheck = open(dest, "w")
                    repocheck.write(str(start) + "," + str(end) + ",\n")
                    repocheck.close()
                #duration update
                now = datetime.datetime.utcnow().replace(microsecond=0)
                x = now - start
                x = x.seconds-2            
                mp.setDuration(mp.getDuration() - x*1000)
                #start-datetime update
                mp.setDate(now+datetime.timedelta(seconds=2))
                #repository update
                mp_list.update(mp)

                scheduler = context.get_scheduler()
                try:
                    scheduler.create_new_timer(mp)
                except ValueError:
                    #log or set default value
                    pass
                #logging
                logger.info("Mediapackage with UID:%s have been reprogrammed", uid)



