######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

__doc__ = """zenovirtperf
Capture events from an oVirt datacenter manager.
"""

COLLECTOR_NAME = 'zenovirtperf'

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

unused(Globals)
unused(DeviceProxy)


class ZenOVirtPerfPreferences(object):
    zope.interface.implements(ICollectorPreferences)

    def __init__(self):
        self.collectorName = COLLECTOR_NAME
        self.configurationService = "ZenPacks.zenoss.oVirt.services.OVirtPerfService"

        # How often the daemon will collect events from each oVirt manager. Specified in seconds.
        self.cycleInterval = 60
        self.configCycleInterval = 5 * 3600

        self.options = None

    def buildOptions(self, parser):
        pass

    def postStartup(self):
        pass


class ZenOVirtPerfTask(ObservableMixin):
    zope.interface.implements(IScheduledTask)

    STATE_FETCH_DATA = 'FETCH_DATA'
    STATE_PARSE_DATA = 'PARSING_DATA'
    STATE_STORE_PERF = 'STORE_PERF_DATA'

    def __init__(self, taskName, deviceId, interval, taskConfig):
        super(ZenOVirtPerfTask, self).__init__()
        self._taskConfig = taskConfig

        self._eventService = zope.component.queryUtility(IEventService)
        self._dataService = zope.component.queryUtility(IDataService)
        self._preferences = zope.component.queryUtility(
            ICollectorPreferences, COLLECTOR_NAME)

        self.name = taskName
        self.configId = deviceId
        self.interval = interval
        self.state = TaskStates.STATE_IDLE
        self.config = taskConfig

        self._serverName = taskConfig.zOVirtServerName
        self._port = int(taskConfig.zOVirtPort)

        creds = '%s@%s:%s' % (taskConfig.zOVirtUser, taskConfig.zOVirtDomain, taskConfig.zOVirtPassword)
        creds = creds.encode('Base64').strip('\r\n')
        self._headers = {
            'Authorization': 'Basic %s' % creds,
            'Accept': 'application/xml'
        }

    def doTask(self):
        deferreds = []
        for url, dpList in self.config.datasources.items():
            d = defer.maybeDeferred(self._httpGet, url)
            d.addCallback(self._processResults, dpList)
            d.addCallback(self._storeResults)
            d.addErrback(self._getError, url)
            deferreds.append(d)

        dl = defer.DeferredList(deferreds)
        dl.addCallback(self.clientFinished)
        return dl

    def _httpGet(self, url):
        """
        Open a HTTP connection to grab the information about a component and return the response.
        """
        self.state = ZenOVirtPerfTask.STATE_FETCH_DATA
        conn = HTTPConnection(self._serverName, port=self._port)
        conn.request('GET', url, headers=self._headers)
        resp = conn.getresponse()
        body = resp.read()
        return body

    def _processResults(self, resultXml, dpList):
        """
        Convert oVirt statistics into perf metrics.

    <statistic href="/api/vms/b890351a-23fb-4a4a-9ed8-98350e828544/statistics/2ec286fe-4bec-32f5-8d63-dba7bed58763" id="2ec286fe-4bec-32f5-8d63-dba7bed58763"> 
        <name>cpu.current.total</name>
        <description>Total CPU used</description>
        <values type="DECIMAL">
            <value>
                <datum>0</datum>
            </value>
        </values>
        <type>GAUGE</type>
        <unit>PERCENT</unit>
        <vm href="/api/vms/b890351a-23fb-4a4a-9ed8-98350e828544" id="b890351a-23fb-4a4a-9ed8-98350e828544"/>
    </statistic>

        """
        self.state = ZenOVirtPerfTask.STATE_PARSE_DATA

        statistics = ElementTree.fromstring(resultXml)
        if statistics.tag != 'statistics':
            log.warn("The result from %s was a '%s' element, rather than " \
                     "the expected 'statistics' element -- skipping",
                     dpList[0]['url'], statistics.tag)
            return

        dpByName = dict( (dp['dpId'], dp) for dp in dpList)
        perfData= []
        for resultNode in statistics:
            dpName = resultNode.find('name').text
            dp = dpByName.get(dpName)
            if dp is None:
                continue

            try:
                datum = resultNode.find('values').find('value').find('datum')
                value = float(datum.text)
            except Exception:
                continue
            perfData.append( (dp, value) )

        return perfData

    def _storeResults(self, resultList):
        """
        Store the values in RRD files

        @parameter resultList: results of running the commands
        @type resultList: array of (datasource, dictionary)
        """
        self.state = ZenOVirtPerfTask.STATE_STORE_PERF
        for dp, value in resultList:
            threshData = {
                'eventKey': dp['eventKey'],
                'component': dp['compId'],
            }
            self._dataService.writeRRD(
                    dp['path'], value,
                    dp['rrdType'], dp['rrdCmd'], dp['cycleTime'],
                    dp['minv'], dp['maxv'],
                    threshData)

        return resultList

    def _getError(self, result, url):
        log.warn("Error requesting URL for %s: %s", url, result)
        import pdb;pdb.set_trace()

    def clientFinished(self, result):
        log.info("Yay! All done")

    def cleanup(self):
        pass


if __name__ == '__main__':
    myPreferences = ZenOVirtPerfPreferences()
    myTaskFactory = SimpleTaskFactory(ZenOVirtPerfTask)
    myTaskSplitter = SimpleTaskSplitter(myTaskFactory)

    daemon = CollectorDaemon(myPreferences, myTaskSplitter)
    daemon.run()
