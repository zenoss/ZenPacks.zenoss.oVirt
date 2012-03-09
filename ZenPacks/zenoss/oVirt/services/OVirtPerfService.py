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

from Products.ZenCollector.services.config import CollectorConfigService

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
        proxy.datapoints = []
        proxy.thresholds = []

        self._getDataPoints(proxy, device, device.id, None, perfServer)
        proxy.thresholds += device.getThresholdInstances('Example Protocol')

        for component in device.getMonitoredComponents():
            self._getDataPoints(
                proxy, component, component.device().id, component.id,
                perfServer)

            proxy.thresholds += component.getThresholdInstances(
                'Example Protocol')


        return proxy

    def _getDataPoints(
            self, proxy, deviceOrComponent, deviceId, componentId, perfServer
            ):
        for template in deviceOrComponent.getRRDTemplates():
            dataSources = [ds for ds
                           in template.getRRDDataSources('Example Protocol')
                           if ds.enabled]

            for ds in dataSources:
                for dp in ds.datapoints():
                    path = '/'.join((deviceOrComponent.rrdPath(), dp.name()))
                    dpInfo = dict(
                        devId=deviceId,
                        compId=componentId,
                        dsId=ds.id,
                        dpId=dp.id,
                        path=path,
                        rrdType=dp.rrdtype,
                        rrdCmd=dp.getRRDCreateCommand(perfServer),
                        minv=dp.rrdmin,
                        maxv=dp.rrdmax,
                        exampleProperty=ds.exampleProperty,
                        )

                    if componentId:
                        dpInfo['componentDn'] = getattr(
                            deviceOrComponent, 'dn', None)

                    proxy.datapoints.append(dpInfo)



if __name__ == '__main__':
    from Products.ZenHub.ServiceTester import ServiceTester
    tester = ServiceTester(OVirtPerfService)
    def printer(config):
        proxyconfig = DeviceProxyConfig(config)
        for attr in proxyconfig.attributes:
            print '\t', attr, '\t', getattr(config, attr, '')
    tester.printDeviceProxy = printer
    tester.showDeviceInfo()

