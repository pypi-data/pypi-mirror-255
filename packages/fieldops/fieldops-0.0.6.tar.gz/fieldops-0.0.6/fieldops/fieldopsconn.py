#!/usr/bin/env python3


import sys
import os
import requests


class FieldOpsConn:
    def __init__(self):
        self.host = None
        self.email = None
        self.password = None
        self.token = None
        self.isConnected = False
        self.apiPath = '/api/v1'

    def connect(self, host = None, email = None, password = None, token = None):

        if token is not None:
            self.token = token
            self.isConnected = True
            #test connection
        
        if host is not None:
            self.host = host

        if email is not None and password is not None:
            self.email = email
            self.password = password
            self.login() 

        if not self.isConnected:
            raise Exception('Not connected to FieldOps')
    

    def login(self):

        if self.host is None:
            raise Exception('Host not set')
        
        if self.email is None or self.password is None:
            raise Exception('User or password not set')
        
        url = self.host + self.apiPath + '/auth/login'
        data = {'email': self.email, 'password': self.password} 
        r = requests.post(url, data=data)

        resp = r.json()

        if(r.status_code != 200):
            raise Exception('Login failed: ' + resp['message'])
        

        self.token = resp['token']
        self.isConnected = True

    def normalizePath(self, path):
        if path[0] != '/':
            path = '/' + path
        return path

    def getToken(self, path):

        path = self.normalizePath(path) 

        if path.endswith('/token') is False:
            path += '/token'
        
        resp = self.get(path)
        return resp.json()['token']

    def get(self, path):

        path = self.normalizePath(path)
        
        if self.isConnected is False:
            raise Exception('Not connected to FieldOps')

        url = self.host + self.apiPath +  path
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        return r

    def post(self, path, data):

        path = self.normalizePath(path)

        if self.isConnected is False:
            raise Exception('Not connected to FieldOps')

        url = self.host + self.apiPath +  path
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.post(url, headers=headers, data=data)
        return r
    
    def put(self, path, data):

        path = self.normalizePath(path)

        if self.isConnected is False:
            raise Exception('Not connected to FieldOps')

        url = self.host + self.apiPath +  path
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.put(url, headers=headers, data=data)
        return r

    def delete(self, path):

        path = self.normalizePath(path)

        if self.isConnected is False:
            raise Exception('Not connected to FieldOps')

        url = self.host + self.apiPath +  path
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.delete(url, headers=headers)
        return r

    def upload(self, path, file, version, track, release_notes):
        path = self.normalizePath(path)

        if path.endswith('/versions') is False:
            path += '/versions'

        #post as formdata 
        if self.isConnected is False:
            raise Exception('Not connected to FieldOps')
        
        url = self.host + self.apiPath +  path
        headers = {'Authorization': 'Bearer ' + self.token}
        data = {'name': version, 'track': track, 'releaseNotes': release_notes}
        files = {'file': open(file, 'rb')}
        r = requests.post(url, headers=headers, data=data, files=files)
        return r
    

    def download(self, path, outpath ):
        path = self.normalizePath(path)
        filename = outpath

        if self.isConnected is False:
            raise Exception('Not connected to FieldOps')
        
        if path.endswith('.gz'):
            url = self.host + self.apiPath +  path
        else:
            url = self.host + self.apiPath +  path + '/download'

        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)

        if r.status_code == 200:

            if filename == '':
                content_disposition = r.headers.get('content-disposition')

                if content_disposition:
                    filename = content_disposition.split("filename=")[-1].strip("'\"").lower()

            with open(filename, 'wb') as f:
                f.write(r.content)

        else:
            raise Exception('Download failed: ' + r.text)
        
        return filename
        
        






    