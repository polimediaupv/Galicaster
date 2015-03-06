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

from os import path
from os import system

from galicaster.core import context

from cStringIO import StringIO
from json import dumps
from json import loads
from pycurl import Curl
from pycurl import CUSTOMREQUEST
from pycurl import error
from pycurl import HTTPHEADER
from pycurl import HTTP_CODE
from pycurl import INFILESIZE
from pycurl import POST
from pycurl import POSTFIELDS
from pycurl import POSTFIELDSIZE
from pycurl import READFUNCTION
from pycurl import TIMEOUT
from pycurl import UPLOAD
from pycurl import URL
from urllib import urlencode



dispatcher = context.get_dispatcher()
conf = context.get_conf()
logger = context.get_logger()

hostname = conf.get('ingest', 'hostname') or ''
server = conf.get('upv_videoapuntes', 'server') or ''
user = conf.get('upv_videoapuntes', 'username') or ''
passwd = conf.get('upv_videoapuntes', 'password') or ''

videoapuntes_client = None
agent_id = None

class VideoApuntesClient:
    def __init__(self, server_url, user, passwd):
        self.server_url = server_url
        self.user = user
        self.passwd = passwd
        self.contents = ''        

    def body_callback(self, buf):
        self.contents = self.contents + buf

    def get_recording(self, id_recording):
        endpoint = '/rest/recordings/' + id_recording
        return self.__get_call(endpoint)

    def get_agent_by_name(self, agent_name):
        endpoint = '/rest/agents?name=' + agent_name
        return self.__get_call(endpoint)


    def update_recording(self, id_recording, new_recording):
        endpoint = '/rest/recordings/' + id_recording
        return self.__put_call(endpoint, new_recording)

    def __get_call(self, endpoint, params=[]):
        self.contents = ""
        fullurl = self.server_url + endpoint
        if (len(params) > 0):
            fullurl = fullurl + "?" + urlencode(params)
        curl = Curl()
        curl.setopt(URL, fullurl)
        curl.setopt(TIMEOUT, 2)
        curl.setopt(curl.SSL_VERIFYPEER, 0)
        curl.setopt(HTTPHEADER, ['Accept: application/json', 'Content-Type: application/json; charset=UTF-8', 'X-Requested-Auth: Digest'])
        curl.setopt(curl.HTTPAUTH, curl.HTTPAUTH_DIGEST)
        curl.setopt(curl.USERPWD, self.user+":"+self.passwd)
        curl.setopt(curl.WRITEFUNCTION, self.body_callback)
        try:
            curl.perform()
        except error, e:
            return {'value' : '', 'error' : True, 'error-msg' : e[1]} 
        retcode = curl.getinfo(HTTP_CODE)
        curl.close()
        if retcode != 200:
            error_msg = 'Return code: %d' % (retcode)
            return {'value' : '', 'error' : True, 'error-msg' : error_msg} 
        else:
            return {'value' : self.contents, 'error' : False, 'error-msg' : ''} 

    def __put_call(self, endpoint, data):
        self.contents = ""
        fullurl = self.server_url + endpoint
        json_data = dumps(data)
        upload_file = StringIO(json_data)
        curl = Curl()
        curl.setopt(URL, fullurl)
        curl.setopt(HTTPHEADER, ['Accept: application/json', 'Content-Type: application/json; charset=UTF-8', 'X-Requested-Auth: Digest'])
        curl.setopt(UPLOAD, 1)
        curl.setopt(READFUNCTION, upload_file.read)
        curl.setopt(INFILESIZE, len(json_data))
        curl.setopt(TIMEOUT, 2)
        curl.setopt(curl.SSL_VERIFYPEER, 0)
        curl.setopt(curl.HTTPAUTH, curl.HTTPAUTH_DIGEST)
        curl.setopt(curl.USERPWD, self.user+":"+self.passwd)
        curl.setopt(curl.WRITEFUNCTION, self.body_callback)
        try:
            curl.perform()
        except error, e:
            return {'value' : '', 'error' : True, 'error-msg' : e[1]} 
        retcode = curl.getinfo(HTTP_CODE)
        curl.close()
        if retcode != 204:
            error_msg = 'Return code: %d' % (retcode)
            return {'value' : '', 'error' : True, 'error-msg' : error_msg} 
        else:
            return {'value' : self.contents, 'error' : False, 'error-msg' : ''} 


def init():
    global videoapuntes_client
    global agent_id

    videoapuntes_client = VideoApuntesClient(server, user, passwd) 

    dispatcher.connect('stop-record', stop_record)
    dispatcher.connect('start-record', start_record)

    agent_id = get_agent_id(hostname)


def start_record(source, identifier=None):
    #print 'Start record: "%s"' % (identifier)
    logger.debug("Starting record {}".format(identifier))

    new_record = { '_id':str(identifier), 'recordedStatus':'recording'}
    if agent_id:
	new_record['recordedByAgent'] = agent_id
    response = videoapuntes_client.update_recording(str(identifier), new_record)

def stop_record(source=None, identifier=None):
    #print 'Stop record: "%s"' % (identifier)
    logger.debug("Stop record {}".format(identifier))
    
    new_record = { '_id':str(identifier), 'recordedStatus':'recorded'}
    response = videoapuntes_client.update_recording(str(identifier), new_record)

def get_agent_id(name):
    iden = None
    response = videoapuntes_client.get_agent_by_name(name)
    if response['error'] is False:
        agent = loads(response['value'])
    	if agent['count'] == 1:
		iden = agent['items'][0]['_id']
    return iden





