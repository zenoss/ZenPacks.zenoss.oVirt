###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, 2012 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from zope.interface import implements

from Products.Zuul.decorators import info
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.infos.component import ComponentInfo

from ZenPacks.zenoss.oVirt.interfaces import (
    IoVirtInfo, IDatacenterInfo, IClusterInfo,
    IVmInfo, IHostInfo, IStorageDomainInfo, IDiskInfo)


class oVirtInfo(DeviceInfo):
    """oVirt API (Info) adapter factory."""

    implements(IoVirtInfo)

    @property
    def vm_count(self):
        return 1


class BaseComponentInfo(ComponentInfo):
    """Abstract base component API (Info) adapter factory."""
    title = ProxyProperty('title')

    @property
    def entity(self):
        return {
           'uid': self._object.getPrimaryUrlPath(),
           'title': self._object.titleOrId(),
           'meta_type': self._object.meta_type,
        }

    @property
    def icon(self):
        return self._object.getIconPath()


class DatacenterInfo(BaseComponentInfo):
    """Datacenter API (Info) adapter factory."""

    implements(IDatacenterInfo)

    description = ProxyProperty('description')
    storage_type = ProxyProperty('storage_type')
    storage_format = ProxyProperty('storage_format')

    @property
    def storagedomain_count(self):
        return 1

class ClusterInfo(BaseComponentInfo):
    """Cluster API (Info) adapter factory."""

    implements(IClusterInfo)

    @property
    @info
    def datacenter(self):
        return self._object.datacenter()


class HostInfo(BaseComponentInfo):
    """Host API (Info) adapter factory."""

    implements(IHostInfo)

    @property
    @info
    def cluster(self):
        return self._object.cluster()

class VmInfo(BaseComponentInfo):
    """VM API (Info) adapter factory."""

    implements(IVmInfo)

    @property
    @info
    def cluster(self):
        return self._object.cluster()

class StorageDomainInfo(BaseComponentInfo):
    """Storage Domain API (Info) adapter factory."""

    implements(IStorageDomainInfo)

    @property
    @info
    def datacenter(self):
        return self._object.datacenter()

class DiskInfo(BaseComponentInfo):
    """Disk API (Info) adapter factory."""

    implements(IDiskInfo)

    @property
    @info
    def storagedomain(self):
        return self._object.storagedomains()

    @property
    @info
    def vm(self):
        return self._object.vm()
