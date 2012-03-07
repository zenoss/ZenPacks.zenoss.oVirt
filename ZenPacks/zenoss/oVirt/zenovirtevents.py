######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

__doc__ = """zenovirtevents
Capture events from an oVirt datacenter manager.
"""

COLLECTOR_NAME = 'zenovirtevents'

import logging
log = logging.getLogger('zen.%s' % COLLECTOR_NAME)

from httplib import HTTPConnection, HTTPSConnection
from xml.etree import ElementTree

import Globals
import zope.component
import zope.interface

from twisted.internet import defer

from Products.ZenCollector.daemon import CollectorDaemon
from Products.ZenCollector.interfaces \
    import ICollectorPreferences, IScheduledTask, IEventService, IDataService

from Products.ZenCollector.tasks \
    import SimpleTaskFactory, SimpleTaskSplitter, TaskStates

from Products.ZenUtils.observable import ObservableMixin

from Products.ZenUtils.Utils import unused

from Products.ZenCollector.services.config import DeviceProxy

from ZenPacks.zenoss.oVirt.event_codes import codes2msg

unused(Globals)
unused(DeviceProxy)


class ZenOVirtEventsPreferences(object):
    zope.interface.implements(ICollectorPreferences)

    def __init__(self):
        self.collectorName = COLLECTOR_NAME
        self.configurationService = "ZenPacks.zenoss.oVirt.services.OVirtEventService"

        # How often the daemon will collect events from each oVirt manager. Specified in seconds.
        self.cycleInterval = 60
        self.configCycleInterval = 5 * 3600

        self.options = None

    def buildOptions(self, parser):
        pass

    def postStartup(self):
        pass


class ZenOVirtEventTask(ObservableMixin):
    zope.interface.implements(IScheduledTask)

    ovirt2zenSeverity = {
        'normal':  0,  # Clear
        'warning': 3,  # Warning
        'error':   4,   # Error
        'alert':   5,  # Critical
    }

    def __init__(self, taskName, deviceId, interval, taskConfig):
        super(ZenOVirtEventTask, self).__init__()
        self._taskConfig = taskConfig

        self._eventService = zope.component.queryUtility(IEventService)
        self._dataService = zope.component.queryUtility(IDataService)
        self._preferences = zope.component.queryUtility(
            ICollectorPreferences, COLLECTOR_NAME)

        self.name = taskName
        self.configId = deviceId
        self.interval = interval
        self.state = TaskStates.STATE_IDLE

        self._serverName = taskConfig.zOVirtServerName
        self._port = int(taskConfig.zOVirtPort)

        creds = '%s@%s:%s' % (taskConfig.zOVirtUser, taskConfig.zOVirtDomain, taskConfig.zOVirtPassword)
        creds = creds.encode('Base64').strip('\r\n')
        self._headers = {
            'Authorization': 'Basic %s' % creds,
            'Accept': 'application/xml'
        }
        self._baseUrl = '/api/'

    def doTask(self):
        d = defer.maybeDeferred(self._httpGet, 'events')
        d.addCallback(self._processEvents)
        return d

    def _httpGet(self, url):
        """
        Open a HTTP connection to grab the information about a component and return the response.
        """
        conn = HTTPConnection(self._serverName, port=self._port)
        conn.request('GET', self._baseUrl + url, headers=self._headers)
        resp = conn.getresponse()
        body = resp.read()
        return body

    def _processEvents(self, eventXml):
        events = ElementTree.fromstring(eventXml)
        for eventNode in events:
            code = int(eventNode.find('code').text)
            evt = {
                'oVirtEventId': eventNode.attrib['id'],
                'summary': eventNode.find('description').text,
                'device': self._serverName,
                'oVirtCode': code,
                'oVirtCodeText': codes2msg.get(code, 'Unknown'),
            }
            evt['severity'] = self.ovirt2zenSeverity.get(eventNode.find('severity').text, 'error')
            self._eventService.sendEvent(evt)
        #import pdb;pdb.set_trace()

    def cleanup(self):
        pass


if __name__ == '__main__':
    myPreferences = ZenOVirtEventsPreferences()
    myTaskFactory = SimpleTaskFactory(ZenOVirtEventTask)
    myTaskSplitter = SimpleTaskSplitter(myTaskFactory)

    daemon = CollectorDaemon(myPreferences, myTaskSplitter)
    daemon.run()
