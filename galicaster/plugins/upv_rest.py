# -*- coding:utf-8 -*-
# Galicaster, Multistream Recorder and Player
#
#       galicaster/plugins/upv_rest
#
# Copyright (c) 2014, Universitat Politècnica de València <polimedia@upvnet.upv.es>
#
# This work is licensed under the Creative Commons Attribution-
# NonCommercial-ShareAlike 3.0 Unported License. To view a copy of 
# this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California, 94105, USA.

from json import dumps
from bottle import route
from bottle import response

from galicaster.core import context

"""
Description: Add custom endpoints to Galicaster REST plugin.
Status: Experimental
"""

def init():
    pass

@route('/UPV')
def index():
    response.content_type = 'application/json'
    state = context.get_state()
    text="Galicaster REST endpoint plugin\n\n"
    endpoints = {
            "/repositorystate" : "list mp state" ,
        }    
    return dumps(endpoints)

@route('/UPV/repositorystate')
def list():
    repo = context.get_repository()
    response.content_type = 'application/json'
    results = []
    for key,value in repo.iteritems():
    	mediapackage = {}
        mediapackage['key'] = key
        mediapackage['status'] = value.status
        mediapackage['operation'] = value.getOpStatus("ingest")
        results.append(mediapackage)
    return dumps(results)

