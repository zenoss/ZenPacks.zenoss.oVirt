######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging
from time import time
from httplib import HTTPConnection, HTTPSConnection
from xml.etree import ElementTree

from twisted.internet import defer

from zope.interface import implements

from Products.ZenCollector.tasks import TaskStates

from ZenPacks.zenoss.Liberator.zengenericmodeler import GenericModelerCollectionTask
from ZenPacks.zenoss.Liberator.interfaces import IGenericCollectionTask

COLLECTOR_NAME = "zengenericmodeler"
TASK_NAME = "OVirtCollectionTask"

log = logging.getLogger("zen.%s.%s" % (COLLECTOR_NAME, TASK_NAME))


class ModelerTask(object):
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
        d = self._modelComponents()
        #d.addCallback(self._modelSubComponents)
        return d

    def _modelComponents(self):
        self._parent.state = GenericModelerCollectionTask.STATE_FETCH_MODEL

        deferreds = []
        for plugin in self._plugins:
            url = plugin.compdef.virtualElement
            log.debug("Collecting %s from %s", url, self._device.id)
            d = defer.maybeDeferred(self._httpGet, url)

            # Make sure that the first item in the list is primary component
            self._tabledata[plugin] = []
            d.addCallback(self._processResponse, plugin)

            if plugin.compdef.subcomponents:
                d.addCallback(self._modelSubComponents, plugin)

            d.addErrback(self._getError, plugin)
            deferreds.append(d)

        dl = defer.DeferredList(deferreds)
        dl.addCallback(self.processResults)
        dl.addCallback(self.sanitizeMaps)
        dl.addErrback(self._failure)
        return dl

    def _httpGet(self, url):
        """
        Open a HTTP connection to grab the information about a component and return the response.
        """
        url = url if url.startswith(self._baseUrl) else self._baseUrl + url

        conn = HTTPConnection(self._serverName, port=self._port)
        conn.request('GET', url, headers=self._headers)
        resp = conn.getresponse()
        body = resp.read()
        conn.close()
        return body

    def _processResponse(self, resultXml, plugin):
        log.debug("Converting response for %s into XML doc", plugin.compdef.virtualElement)
        doc = None
        try:
            doc = ElementTree.fromstring(resultXml)
            self._tabledata[plugin].append(doc)
        except Exception:
            log.error("Received invalid XML from modeler code -- skipping %s",
                      plugin.name())

        return doc

    def _getError(self, result, plugin):
        log.warn("Error requesting URL for %s: %s", plugin.compdef.virtualElement, result)

    def _modelSubComponents(self, container, plugin):
        self._parent.state = GenericModelerCollectionTask.STATE_FETCH_MODEL

        for item in container:
            baseUrl = item.attrib['href']
            deferreds = []
            for subcompdef in plugin.compdef.subcomponents:
                url = baseUrl + '/' + subcompdef.parentRelation
                log.debug("Collecting %s from %s", url, self._device.id)
                d = defer.maybeDeferred(self._httpGet, url)
                d.addCallback(self._processResponse, plugin)
                d.addErrback(self._getError, plugin)
                deferreds.append(d)

        return defer.DeferredList(deferreds)

    def processResults(self, ignoredData):
        allrelmaps = []
        for plugin, results in self._tabledata.items():
            if len(results) == 0:
                # Kicked off modeling but not results returned
                continue

            # Process primary components
            try:
                relmaps = plugin.process(self._parent._device, results[0], log)
            except Exception, ex:
                self._parent.pluginFailure(plugin.name(), ex)
                continue

            # Process subcomponents
            tag2def = dict( (x.virtualElement, x) for x in plugin.compdef.subcomponents)
            for xmldoc in results[1:]:
                compdef = tag2def.get(xmldoc.tag)
                if compdef is None:
                    continue

                try:
                    subrelmaps = plugin.processSubComponents(xmldoc, compdef, log)
                    relmaps.extend(subrelmaps)
                except Exception, ex:
                    self._parent.pluginFailure(plugin.name(), ex)

            allrelmaps.extend(relmaps)

        return allrelmaps

    def sanitizeMaps(self, results):
        maps = {}
        for relmaps in results:
            if relmaps is None: # Expecting []
                log.warning("No relmaps returned from %s from %s",
                            self._comptype, self._device.id)
                continue

            if not isinstance(relmaps, list):
                relmaps = [relmaps]

            for relmap in relmaps:
                key = (relmap.compname, relmap.relname)
                if key in maps:
                    maps[key].maps.extend(relmap.maps)
                else:
                    maps[key] = relmap

        return maps

    def _failure(self, fail):
        import pdb;pdb.set_trace()
