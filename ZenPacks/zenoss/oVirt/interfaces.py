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

    vm_count = schema.Int(title=_t(u"VM Count"))


class IDatacenterInfo(IComponentInfo):
    """Interface for the DataCenter API (Info) Adapter."""

    cluster_count = schema.Int(title=_t(u"Cluster Count"))
    storagedomain_count = schema.Int(title=_t(u"StorageDomain Count"))


class IClusterInfo(IComponentInfo):
    """Interface for the Cluster API (Info) Adapter."""


class IVmInfo(IComponentInfo):
    """Interface for the VM API (Info) Adapter."""


class IHostInfo(IComponentInfo):
    """Interface for the Host API (Info) Adapter."""


class IStorageDomainInfo(IComponentInfo):
    """Interface for the StorageDomain API (Info) Adapter."""

class IDiskInfo(IComponentInfo):
    """Interface for the Disk API (Info) Adapter."""
