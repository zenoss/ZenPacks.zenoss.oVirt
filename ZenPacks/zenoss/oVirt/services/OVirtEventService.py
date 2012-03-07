######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

__doc__ = """OVirtEventService
ZenHub service for providing configuration to the zenovirtevents event collector daemon.

"""

import logging
log = logging.getLogger('zen.OVirtEventService')

import Globals

from Products.ZenCollector.services.config import CollectorConfigService

from ZenPacks.zenoss.oVirt.componenttypes.ovirt.DeviceProxyConfig import DeviceProxyConfig


class OVirtEventService(CollectorConfigService):

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

        proxy.datapoints = []
        proxy.thresholds = []

        # FIXME: this is not set up yet
        proxy.lastEvent = getattr(device, 'lastEvent', 0)

        return proxy


if __name__ == '__main__':
    from Products.ZenHub.ServiceTester import ServiceTester
    tester = ServiceTester(OVirtEventService)
    def printer(config):
        proxyconfig = DeviceProxyConfig(config)
        for attr in proxyconfig.attributes:
            print '\t', attr, '\t', getattr(config, attr, '')
    tester.printDeviceProxy = printer
    tester.showDeviceInfo()

