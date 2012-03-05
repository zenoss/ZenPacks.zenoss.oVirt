######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging
from time import time
from httplib import HTTPConnection, HTTPSConnection


from twisted.internet import defer


from zope.interface import implements

from Products.ZenCollector.tasks import TaskStates

from ZenPacks.zenoss.Liberator.zengenericmodeler import GenericModelerCollectionTask
from ZenPacks.zenoss.Liberator.interfaces import IGenericCollectionTask

COLLECTOR_NAME = "zengenericmodeler"
TASK_NAME = "OVirtCollectionTask"

log = logging.getLogger("zen.%s.%s" % (COLLECTOR_NAME, TASK_NAME))


class CollectionTask(object):
    implements(IGenericCollectionTask)

    STATE_FETCH_MODEL = 'FETCH_MODEL_DATA'
    STATE_PROCESS_MODEL = 'FETCH_PROCESS_MODEL_DATA'

    def __init__(self, device):
        self._device = device
        self._manageIp = self._device.manageIp

        self._serverName = device.zOVirtServerName
        self._port = int(device.zOVirtPort)

        creds = '%s@%s:%s' % (device.zOVirtUser, device.zOVirtDomain, device.zOVirtPassword)
        creds = creds.encode('Base64').strip('\r\n')
        self._headers = {
            'Authorization': 'Basic %s' % creds,
            'Accept': 'application/xml'
        }
        self._baseUrl = '/api/'

    def doTask(self, parentTask, plugins):
        self._parent = parentTask
        self._parent.state = TaskStates.STATE_IDLE

        self._plugins = plugins

        self._tabledata = {}

        # Used for nicer reporting
        self._parent._lastCollectionTime = None
        self._parent._startTime = None
        self._parent._finishTime = None

        self._parent._startTime = time()
        d = self._collect()
        return d

    def _collect(self):
        self._parent.state = GenericModelerCollectionTask.STATE_FETCH_MODEL
        deferreds = []
        for plugin in self._plugins:
            url = plugin.compdef.virtualElement
            log.debug("Collecting %s from %s", url, self._device.id)
            self._tabledata[plugin] = {}
            d = defer.maybeDeferred(self._httpGet, url)
            d.addCallback(self._processResponse, plugin)
            d.addErrback(self._getError, plugin)
            deferreds.append(d)
        dl = defer.DeferredList(deferreds)
        dl.addCallback(self.clientFinished)

        return dl

    def _httpGet(self, url):
        """
        Open a HTTP connection to grab the information about a component and return the response.
        """
        conn = HTTPConnection(self._serverName, port=self._port)
        conn.request('GET', self._baseUrl + url, headers=self._headers)
        resp = conn.getresponse()
        body = resp.read()
        return body

    def _processResponse(self, result, plugin):
        log.debug("Processing response for %s", plugin.compdef.virtualElement)
        self._tabledata[plugin] = result

    def _getError(self, result, plugin):
        log.warn("Error requesting URL for %s: %s", plugin.compdef.virtualElemen, result)

    def clientFinished(self, result):
        return self._parent.processResults(self.getResults())

    def getResults(self):
        data = {}
        for plugin in self._plugins:
            data[plugin] = ({}, self._tabledata.get(plugin, {}))
        return data

