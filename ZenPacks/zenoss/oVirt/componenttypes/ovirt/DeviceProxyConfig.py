######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from zope.interface import implements

from Products.ZenHub.services.PerformanceConfig import ATTRIBUTES

from ZenPacks.zenoss.Liberator.DeviceProxyConfig import DeviceProxyConfig
from ZenPacks.zenoss.Liberator.interfaces import IDeviceProxyConfig


class DeviceProxyConfig(DeviceProxyConfig):
    implements(IDeviceProxyConfig)

    attributes = (
      'zOVirtServerName', 'zOVirtPort',
      'zOVirtUser', 'zOVirtDomain', 'zOVirtPassword',
    )

    def filter(self, device):
        include = True

        if not getattr(device, 'zOVirtServerName', '').strip():
            self.log.debug("Device %s skipped by Liberator (ovirt) because zOVirtServerName is not set.",
                          device.id)
            include = False

        if not getattr(device, 'zOVirtUser', '').strip():
            self.log.debug("Device %s skipped by Liberator (ovirt) because zOVirtUser is not set.",
                          device.id)
            include = False

        if not getattr(device, 'zOVirtDomain', '').strip():
            self.log.debug("Device %s skipped by Liberator (ovirt) because zOVirtDomain is not set.",
                          device.id)
            include = False

        if not getattr(device, 'zOVirtPassword', '').strip():
            self.log.debug("Device %s skipped by Liberator (ovirt) because zOVirtPassword is not set.",
                          device.id)
            include = False

        return include

