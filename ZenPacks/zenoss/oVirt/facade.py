###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2012, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from urlparse import urlparse

from zope.interface import implements

from Products.Zuul.facades import ZuulFacade
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.oVirt.interfaces import IoVirtFacade


class oVirtFacade(ZuulFacade):
    implements(IoVirtFacade)

    def add_ovirt(self, url, username, domain, password, collector='localhost'):
        """Handles adding a new oVirt environment to the system."""
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        deviceRoot = self._dmd.getDmdRoot("Devices")
        device = deviceRoot.findDeviceByIdExact(hostname)

        if device:
            return False, _t("A device named %s already exists." % hostname)

        zProperties = {
            'zOVirtUrl': url,
            'zOVirtUser': username,
            'zOVirtDomain': domain,
            'zOVirtPassword': password,
        }

        perfConf = self._dmd.Monitors.getPerformanceMonitor('localhost')
        jobStatus = perfConf.addDeviceCreationJob(
            deviceName=hostname,
            devicePath='/Devices/oVirt',
            discoverProto='python',
            performanceMonitor=collector,
            zProperties=zProperties)

        return True, jobStatus.id
