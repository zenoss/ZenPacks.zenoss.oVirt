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
    IVmInfo, IHostInfo, IStorageDomainInfo, IVmDiskInfo,
    IHostNicInfo, IVmNicInfo)


class oVirtInfo(DeviceInfo):
    """oVirt API (Info) adapter factory."""

    implements(IoVirtInfo)


class BaseComponentInfo(ComponentInfo):
    """Abstract base component API (Info) adapter factory."""

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
    def cluster_count(self):
        return self._object.clusters.countObjects()

    @property
    def storagedomain_count(self):
        return self._object.storagedomains.countObjects()


class ClusterInfo(BaseComponentInfo):
    """Cluster API (Info) adapter factory."""

    implements(IClusterInfo)

    @property
    @info
    def datacenter(self):
        return self._object.datacenter()

    @property
    def host_count(self):
        return self._object.hosts.countObjects()

    @property
    def vm_count(self):
        return self._object.vms.countObjects()


class HostInfo(BaseComponentInfo):
    """Host API (Info) adapter factory."""

    implements(IHostInfo)

    address = ProxyProperty('address')
    memory = ProxyProperty('memory')
    cpu_sockets = ProxyProperty('cpu_sockets')
    cpu_cores = ProxyProperty('cpu_cores')
    cpu_name = ProxyProperty('cpu_name')
    cpu_speed = ProxyProperty('cpu_speed')
    storage_manager = ProxyProperty('storage_manager')

    @property
    @info
    def cluster(self):
        return self._object.cluster()

    @property
    def nic_count(self):
        return self._object.nics.countObjects()

    @property
    def vm_count(self):
        return self._object.vms.countObjects()

    @property
    @info
    def managed_device(self):
        return self._object.managed_device()


class VmInfo(BaseComponentInfo):
    """VM API (Info) adapter factory."""

    implements(IVmInfo)

    vm_type = ProxyProperty('vm_type')
    memory = ProxyProperty('memory')
    cpu_cores = ProxyProperty('cpu_cores')
    cpu_sockets = ProxyProperty('cpu_sockets')
    os_type = ProxyProperty('os_type')
    os_boot = ProxyProperty('os_boot')
    creation_time = ProxyProperty('creation_time')
    affinity = ProxyProperty('affinity')
    memory_policy_guaranteed = ProxyProperty('memory_policy_guaranteed')

    @property
    @info
    def cluster(self):
        return self._object.cluster()

    @property
    def nic_count(self):
        return self._object.nics.countObjects()

    @property
    @info
    def host(self):
        return self._object.host()

    @property
    @info
    def guest(self):
        return self._object.guest()


class StorageDomainInfo(BaseComponentInfo):
    """Storage Domain API (Info) adapter factory."""

    implements(IStorageDomainInfo)

    storagedomain_type = ProxyProperty('storagedomain_type')
    storage_type = ProxyProperty('storage_type')
    storage_format = ProxyProperty('storage_format')

    @property
    def disk_count(self):
        return self._object.disks.countObjects()

    @property
    def datacenter_count(self):
        return self._object.datacenter.countObjects()


class VmDiskInfo(BaseComponentInfo):
    """VmDisk API (Info) adapter factory."""

    implements(IVmDiskInfo)

    bootable = ProxyProperty('bootable')
    interface = ProxyProperty('interface')
    format = ProxyProperty('format')
    size = ProxyProperty('size')

    @property
    @info
    def storagedomain(self):
        return self._object.storagedomains()

    @property
    @info
    def vm(self):
        return self._object.vm()


class HostNicInfo(BaseComponentInfo):
    """HostNic API (Info) adapter factory."""

    implements(IHostNicInfo)

    mac = ProxyProperty('mac')
    ip = ProxyProperty('ip')
    netmask = ProxyProperty('netmask')
    gateway = ProxyProperty('gateway')
    speed = ProxyProperty('speed')

    @property
    def nicespeed(self):
        """
        Return a string that expresses self.speed in reasonable units.
        """
        if not self.speed:
            return 'Unknown'
        speed = int(self.speed)
        for unit in ('bps', 'Kbps', 'Mbps', 'Gbps'):
            if speed < 1000:
                break
            speed /= 1000.0
        return "%.0f %s" % (speed, unit)

    @property
    @info
    def host(self):
        return self._object.host()


class VmNicInfo(BaseComponentInfo):
    """VmNic API (Info) adapter factory."""

    implements(IVmNicInfo)

    mac = ProxyProperty('mac')
    interface = ProxyProperty('interface')

    @property
    @info
    def vm(self):
        return self._object.vm()
