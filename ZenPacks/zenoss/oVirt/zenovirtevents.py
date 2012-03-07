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

    extraFields = (
        'vm', 'vmpool', 'storage_domain', 'network', 'host', 'cluster', 'domain',
        'template', 'tags', 'data_center',
    )

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

        self.lastMessageId = 0

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
        """
        Convert and send oVirt events as Zenoss events.
        """
        events = ElementTree.fromstring(eventXml)
        for eventNode in events:
            msgId = int(eventNode.attrib['id'])

            # Don't send events we've already sent
            if msgId <= self.lastMessageId:
                continue
            self.lastMessageId = msgId
            
            # Add in information guaranteed to be in the event
            code = int(eventNode.find('code').text)
            evt = {
                'ovirt_event_id': msgId,
                'summary': eventNode.find('description').text,
                'device': self._serverName,
                'ovirt_code': code,
                'ovirt_code_text': codes2msg.get(code, 'Unknown'),
            }
            evt['severity'] = self.ovirt2zenSeverity.get(eventNode.find('severity').text, 'error')

            # Add in extra bits...
            self._updateEventWithExtraData(evt, eventNode)

            self._eventService.sendEvent(evt)

    def _updateEventWithExtraData(self, evt, eventNode):
        """
        Add in the object ids for the related entities.
        """
        for virtualElement in self.extraFields:
            item = eventNode.find(virtualElement)
            if item is not None:
                evt[virtualElement] = item.text

    def cleanup(self):
        pass


if __name__ == '__main__':
    myPreferences = ZenOVirtEventsPreferences()
    myTaskFactory = SimpleTaskFactory(ZenOVirtEventTask)
    myTaskSplitter = SimpleTaskSplitter(myTaskFactory)

    daemon = CollectorDaemon(myPreferences, myTaskSplitter)
    daemon.run()
