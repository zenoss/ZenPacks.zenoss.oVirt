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

from Products.Zuul.form import schema
from Products.Zuul.interfaces import IFacade
from Products.Zuul.interfaces import IDeviceInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

# In Zenoss 3 we mistakenly mapped TextLine to Zope's multi-line text
# equivalent and Text to Zope's single-line text equivalent. This was
# backwards so we flipped their meanings in Zenoss 4. The following block of
# code allows the ZenPack to work properly in Zenoss 3 and 4.

# Until backwards compatibility with Zenoss 3 is no longer desired for your
# ZenPack it is recommended that you use "SingleLineText" and "MultiLineText"
# instead of schema.TextLine or schema.Text.
from Products.ZenModel.ZVersion import VERSION as ZENOSS_VERSION
from Products.ZenUtils.Version import Version

# One of the following branches below will not be covered by unit tests on any
# given Zenoss version because it is a Zenoss version test.
if Version.parse('Zenoss %s' % ZENOSS_VERSION) >= Version.parse('Zenoss 4'):
    SingleLineText = schema.TextLine
    MultiLineText = schema.Text
else:
    SingleLineText = schema.Text
    MultiLineText = schema.TextLine


class IoVirtFacade(IFacade):
    def add_ovirt(self, url, username, domain, password, collector):
        """Add ovirt."""


class IoVirtInfo(IDeviceInfo):
    """Interface for oVirt API (Info) adapter."""

    id = SingleLineText(title=_t(u"ID"))
    vm_count = schema.Int(title=_t(u"VM Count"))


class IDatacenterInfo(IComponentInfo):
    """Interface for the DataCenter API (Info) Adapter."""

    id = SingleLineText(title=_t(u"ID"))
    description = SingleLineText(title=_t(u"Description"))
    storage_type = SingleLineText(title=_t(u"Storage Type"))
    storage_format = SingleLineText(title=_t(u"Storage Format"))
    cluster_count = schema.Int(title=_t(u"Cluster Count"))
    storagedomain_count = schema.Int(title=_t(u"StorageDomain Count"))


class IClusterInfo(IComponentInfo):
    """Interface for the Cluster API (Info) Adapter."""

    id = SingleLineText(title=_t(u"ID"))
    host_count = schema.Int(title=_t(u"Host Count"))
    vm_count = schema.Int(title=_t(u"VM Count"))


class IVmInfo(IComponentInfo):
    """Interface for the VM API (Info) Adapter."""

    id = SingleLineText(title=_t(u"ID"))
    vm_type = SingleLineText(title=_t(u"Virtual Machine Type"))
    creation_time = SingleLineText(title=_t(u"Creation Time"))
    memory = SingleLineText(title=_t(u"Memory"))
    memory_policy_guaranteed = SingleLineText(title=_t(u"Guaranteed Memory Policy"))
    cpu_cores = SingleLineText(title=_t(u"Cpu Cores"))
    cpu_sockets = SingleLineText(title=_t(u"Cpu Sockets"))
    os_type = SingleLineText(title=_t(u"OS Type"))
    os_boot = SingleLineText(title=_t(u"OS Boot Device"))
    affinity = SingleLineText(title=_t(u"Affinity"))
    nic_count = schema.Int(title=_t(u"Nic Count"))


class IHostInfo(IComponentInfo):
    """Interface for the Host API (Info) Adapter."""

    id = SingleLineText(title=_t(u"ID"))
    storage_manager = schema.Int(title=_t(u"Storage Manager"))
    address = SingleLineText(title=_t(u"IP Address"))
    memory = SingleLineText(title=_t(u"Memory"))
    cpu_sockets = SingleLineText(title=_t(u"Cpu Sockets"))
    cpu_cores = SingleLineText(title=_t(u"Cpu Cores"))
    cpu_name = SingleLineText(title=_t(u"Cpu Type"))
    cpu_speed = SingleLineText(title=_t(u"Cpu Speed"))
    nic_count = schema.Int(title=_t(u"Nic Count"))
    vm_count = schema.Int(title=_t(u"Vm Count"))


class IStorageDomainInfo(IComponentInfo):
    """Interface for the StorageDomain API (Info) Adapter."""

    id = SingleLineText(title=_t(u"ID"))
    storagedomain_type = SingleLineText(title=_t(u"StorageDomain Type"))
    storage_type = SingleLineText(title=_t(u"Storage Type"))
    storage_format = SingleLineText(title=_t(u"Storage Format"))
    datacenter_count = schema.Int(title=_t(u"DataCenter Count"))


class IDiskInfo(IComponentInfo):
    """Interface for the Disk API (Info) Adapter."""

    id = SingleLineText(title=_t(u"ID"))
    bootable = SingleLineText(title=_t(u"Bootable"))
    interface = SingleLineText(title=_t(u"Interface"))
    format = SingleLineText(title=_t(u"Format"))
    size = schema.Int(title=_t(u"Size"))


class IHostNicInfo(IComponentInfo):
    """Interface for the Host Nic API (Info) Adapter."""

    id = SingleLineText(title=_t(u"ID"))
    mac = SingleLineText(title=_t(u"MAC Address"))
    ip = SingleLineText(title=_t(u"IP Address"))
    netmask = SingleLineText(title=_t(u"Netmask"))
    gateway = SingleLineText(title=_t(u"Gateway"))
    speed = SingleLineText(title=_t(u"Speed"))


class IVmNicInfo(IComponentInfo):
    """Interface for the VM Nic API (Info) Adapter."""

    id = SingleLineText(title=_t(u"ID"))
    interface = SingleLineText(title=_t(u"Interface"))
    mac = SingleLineText(title=_t(u"Mac"))
