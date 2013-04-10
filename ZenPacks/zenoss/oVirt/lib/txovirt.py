###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, 2012 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

__all__ = ['Client']

import logging
log = logging.getLogger('zen.txovirt')

import twisted.web.client
#from twisted.internet.defer import inlineCallbacks, returnValue
import sys
from xml.etree import ElementTree

import urllib2,cookielib

txovirt_clients = {}

def CamelCase(data, separator='.'):
    temp = [x.title() for x in data.split(separator)]
    result = temp[0].lower()
    if len(temp) > 1:
        result += ''.join(temp[1:])

    return result


def getText(element):
    return element.childNodes[0].data


def getClient(url, user, domain, password):
    '''return a client object based on the passed in parameters'''
    key = "%s%s%s_%s" % (url, user, domain, password)

    if key in txovirt_clients:
        log.debug("Using txovirt client cache for %s %s %s" % (url, user, domain))
        return txovirt_clients[key]
    else:
        log.debug("Creating a new txovirt client for %s %s %s" % (url, user, domain))
        client = Client(url, user, domain, password)
        txovirt_clients[key] = client
        return client 

class Client(object):
    """oVirt Client"""

    def __init__(self, base_url, username, domain, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.domain = domain
        self.password = password
        self.cookies = {}
        self.login()

    def reset(self):
        ''' Reset login state so the next login will get a new cookie.'''

        #Build the credential string
        creds = '%s@%s:%s' % (self.username, self.domain, self.password)
        creds = creds.encode('Base64').strip('\r\n')

        self.headers = {
            'Authorization': 'Basic %s' % creds,
            'Accept': 'application/xml',
            'Prefer': 'persistent-auth'
            }
        self.cookies = {}

    def login(self):
        self.reset()
        url = '%s/api' % (self.base_url)
  
        # Use urllib2 here so the login is syncronous and all other calls will use the same cookie
        cookies = cookielib.LWPCookieJar()
        handlers = [ urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
        opener = urllib2.build_opener(*handlers)
        req = urllib2.Request(url,headers=self.headers)
        log.debug("login: %s %s %s" % (url,self.headers,self.cookies))
        opener.open(req)
        try:
            self.cookies['JSESSIONID'] = [(c.name,c.value) for c in cookies if c.name == 'JSESSIONID' ][0][1]
        except:
            self.cookies = {}

        if self.cookies and 'Authorization' in self.headers:
            del(self.headers['Authorization'])

    def request_elementtree(self, command, **kwargs):
        ''' return elementtree wrapped results.'''
        ''' the modeler plugins still use element tree. '''
        def process_result(results):
            doc = ElementTree.fromstring(results)
            return doc

        url = '%s/api/%s' % (self.base_url, command)
        log.debug("request_elementtree: %s %s %s" % (url,self.headers,self.cookies))
        result = twisted.web.client.getPage(url, headers=self.headers, cookies=self.cookies).addCallback(process_result)
        return result

    def request(self, command, **kwargs):
        ''' return raw results.'''
        url = '%s/api/%s' % (self.base_url, command)
        log.debug("request: %s %s %s" % (url,self.headers,self.cookies))
        result =  twisted.web.client.getPage(url, headers=self.headers, cookies=self.cookies)
        return result

    def listEvents(self, last=None, **kwargs):
        if not last:
            return self.request_elementtree('events', **kwargs)


if __name__ == '__main__':
    import os

    from twisted.internet import reactor
    from twisted.internet.defer import DeferredList

    client = Client(
        os.environ.get('OVIRT_URL', 'http://127.0.0.1:8080'),
        os.environ.get('OVIRT_USERNAME', 'admin'),
        os.environ.get('OVIRT_DOMAIN', 'internal'),
        os.environ.get('OVIRT_PASSWORD', 'password'))

    def callback(results):
        reactor.stop()
        for success, result in results:
            if success:
                print ElementTree.dump(result)
            else:
                print result.printTraceback()

    deferreds = []
    if len(sys.argv) < 2:
        deferreds.extend((
            client.request_elementtree('clusters'),
            client.request_elementtree('datacenters'),
            client.request_elementtree('hosts'),
            client.request_elementtree('networks'),
            client.request_elementtree('roles'),
            client.request_elementtree('storagedomains'),
            client.request_elementtree('templates'),
            client.request_elementtree('tags'),
            client.request_elementtree('users'),
            client.request_elementtree('groups'),
            client.request_elementtree('domains'),
            client.request_elementtree('vmpools'),
            client.request_elementtree('vms'),
            ))
    else:
        for command in sys.argv[1:]:
            deferreds.append(client.request_elementtree(command))

    DeferredList(deferreds, consumeErrors=True).addCallback(callback)
    reactor.run()


"""
<link href="/api/capabilities" rel="capabilities"/>
<link href="/api/clusters" rel="clusters"/>
<link href="/api/clusters?search={query}" rel="clusters/search"/>
<link href="/api/datacenters" rel="datacenters"/>
<link href="/api/datacenters?search={query}" rel="datacenters/search"/>
<link href="/api/events" rel="events"/>
<link href="/api/events?search={query}&from={event_id}" rel="events/search"/>
<link href="/api/hosts" rel="hosts"/>
<link href="/api/hosts?search={query}" rel="hosts/search"/>
<link href="/api/networks" rel="networks"/>
<link href="/api/roles" rel="roles"/>
<link href="/api/storagedomains" rel="storagedomains"/>
<link href="/api/storagedomains?search={query}" rel="storagedomains/search"/>
<link href="/api/tags" rel="tags"/>
<link href="/api/templates" rel="templates"/>
<link href="/api/templates?search={query}" rel="templates/search"/>
<link href="/api/users" rel="users"/>
<link href="/api/users?search={query}" rel="users/search"/>
<link href="/api/groups" rel="groups"/>
<link href="/api/groups?search={query}" rel="groups/search"/>
<link href="/api/domains" rel="domains"/>
<link href="/api/vmpools" rel="vmpools"/>
<link href="/api/vmpools?search={query}" rel="vmpools/search"/>
<link href="/api/vms" rel="vms"/>
<link href="/api/vms?search={query}" rel="vms/search"/>



xml.getElementsByTagName('vm')[0].attributes['id'].value
"""
