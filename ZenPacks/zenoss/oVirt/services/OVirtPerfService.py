######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

__doc__ = """OVirtPerfService
ZenHub service for providing configuration to the zenovirtperf performance collector daemon.

"""

import logging
log = logging.getLogger('zen.OVirtPerfService')

import Globals

from Products.PageTemplates.Expressions import getEngine

from Products.ZenUtils.ZenTales import talesCompile
from Products.ZenCollector.services.config import CollectorConfigService
from Products.ZenEvents.ZenEventClasses import Error, Cmd_Fail


from ZenPacks.zenoss.oVirt.componenttypes.ovirt.DeviceProxyConfig import DeviceProxyConfig


class OVirtPerfService(CollectorConfigService):

    def _filterDevice(self, device):
        filter = CollectorConfigService._filterDevice(self, device)

        if filter:
            # FIXME: This is a little clumsy.  Should change the Liberator framework to account for this use case.
            proxyconfig = DeviceProxyConfig(device)
            proxyconfig.log = log
            return proxyconfig.filter(device)

        return filter

    def _createDeviceProxy(self, device):
        proxyconfig = DeviceProxyConfig(device)
        self._deviceProxyAttributes += proxyconfig.attributes
        proxy = CollectorConfigService._createDeviceProxy(self, device)

        proxy.configCycleInterval = 3600
        proxy.datasources = {}
        proxy.thresholds = []

        perfServer = device.getPerformanceServer()
        self._getDataPoints(proxy, device, device.id, None, perfServer)
        proxy.thresholds += device.getThresholdInstances('oVirt')

        for component in device.getMonitoredComponents():
            self._getDataPoints(
                proxy, component, component.device().id, component.id,
                perfServer)

            proxy.thresholds += component.getThresholdInstances('oVirt')

        return proxy

    def _getDataPoints(self, proxy, deviceOrComponent, deviceId,
                       componentId, perfServer):
        for template in deviceOrComponent.getRRDTemplates():
            dataSources = [ds for ds
                           in template.getRRDDataSources('oVirt')
                           if ds.enabled]

            for ds in dataSources:
                for dp in ds.datapoints():
                    path = '/'.join((deviceOrComponent.rrdPath(), dp.name()))
                    
                    url = self._evalTales(deviceOrComponent, template, ds)
                    if url is None:
                        continue

                    dpInfo = dict(
                        devId=deviceId,
                        compId=componentId,
                        dsId=ds.id,
                        cycleTime=ds.cycletime,
                        dpId=dp.id,
                        path=path,
                        rrdType=dp.rrdtype,
                        rrdCmd=dp.getRRDCreateCommand(perfServer),
                        minv=dp.rrdmin,
                        maxv=dp.rrdmax,
                        url=url,
                        eventKey=ds.eventKey,
                        )

                    dpList = proxy.datasources.setdefault(url, [])
                    dpList.append(dpInfo)

    def _evalTales(self, context, templ, ds):
        url = ds.url
        if not url.startswith('string:') and not url.startswith('python:'):
            url = 'string:%s' % url

        compiled = talesCompile(url)
        dev = context.device()
        environ = {'dev' : dev,
                   'device': dev,
                   'devname': dev.id,
                   'ds': ds,
                   'datasource': ds,
                   'here' : context,
                   'nothing' : None,
                  }
        try:
            result = compiled(getEngine().getContext(environ))
        except Exception:
            self._sendBadTalesEvent(dev, context, templ, ds)
            return None

        if isinstance(result, Exception):
            self._sendBadTalesEvent(dev, context, templ, ds)
            return None

        return result

    def _sendBadTalesEvent(self, dev, comp, templ, ds):
        msg = "TALES error for device %s datasource %s" % (
                               dev.id, ds.id)
        evt = dict(
                  msg=msg,
                  template=templ.id,
                  datasource=ds.id,
                  affected_device=dev.id,
                  affected_component=comp.id,
                  resolution='Could not create a command to send to zenovirtperf' \
                      ' because TALES evaluation failed.  The most likely' \
                      ' cause is unescaped special characters in the datasource.' \
                      ' eg $ or %',
                  device='localhost', # Dedup on the localhost as it will affect everything
                  eventClass=Cmd_Fail,
                  severity=Error,
                  component='zenovirtperf',
                  summary=msg,
        )                  
        self.sendEvent(evt)           


if __name__ == '__main__':
    from Products.ZenHub.ServiceTester import ServiceTester
    tester = ServiceTester(OVirtPerfService)
    def printer(config):
        print "%s:%s %s@%s" % (config.zOVirtServerName, config.zOVirtPort,
                               config.zOVirtUser, config.zOVirtDomain)
        
        print '\t'.join(["DS", "URL", '', 'Datapoints'])
        for url, dpList in sorted(config.datasources.items()):
            dp= dpList[0]
            print '\t'.join([ dp['dsId'], url])

            for dp in dpList:
                print '\t'.join(['\t', '', dp['dpId']])

    tester.printDeviceProxy = printer
    tester.showDeviceInfo()

