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

import twisted.web.client
import sys
from twisted.internet import defer
from xml.dom.minidom import parseString
from xml.etree import ElementTree
from twisted.python import log

def getText(element):
    return element.childNodes[0].data

class Client(object):
    """oVirt Client"""

    def __init__(self, base_url, username,domain, password):
        self.base_url = base_url
        self.username = username
        self.domain = domain
        self.password = password
        #Build the credential string
        creds = '%s@%s:%s' % (self.username, self.domain, self.password)
        print creds
        print self.base_url
        creds = creds.encode('Base64').strip('\r\n')
        self.headers = {
            'Authorization': 'Basic %s' % creds,
            'Accept': 'application/xml'
        }

    def request(self,command,**kwargs):
        def process_result(results):
            doc = ElementTree.fromstring(results)
            return doc 

        url = '%s/api/%s' % (self.base_url,command)
        print "running %s" % command
        return twisted.web.client.getPage(url,headers=self.headers).addCallback(process_result)

if __name__ == '__main__':
    import os
    import sys

    from twisted.internet import reactor
    from twisted.internet.defer import DeferredList

    client = Client(
        os.environ.get('OVIRT_URL', 'http://10.175.213.149:8080'),
        os.environ.get('OVIRT_USERNAME', 'admin'),
        os.environ.get('OVIRT_DOMAIN', 'internal'),
        os.environ.get('OVIRT_PASSWORD', 'zenoss'))

    def callback(results):
        reactor.stop()
        for success, result in results:
            if success:
                print result.toxml()
            else:
                print result.printTraceback()

    deferreds = []
    if len(sys.argv)<2:
        deferreds.extend((
            client.request('clusters'),
            client.request('datacenters'),
            client.request('hosts'),
            client.request('networks'),
            client.request('roles'),
            client.request('storagedomains'),
            client.request('templates'),
            client.request('tags'),
            client.request('users'),
            client.request('groups'),
            client.request('domains'),
            client.request('vmpools'),
            client.request('vms')
        ))
    else:
        for command in sys.argv[1:]:
            deferreds.append(client.request(command))

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
