###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from zope.component import adapts

from ZenPacks.zenoss.DynamicView import TAG_IMPACTED_BY, TAG_IMPACTS, TAG_ALL
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelatable
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelationsProvider
from ZenPacks.zenoss.DynamicView.model.adapters import DeviceComponentRelatable

from ZenPacks.zenoss.oVirt.System import System
from ZenPacks.zenoss.oVirt.DataCenter import DataCenter
from ZenPacks.zenoss.oVirt.Cluster import Cluster
from ZenPacks.zenoss.oVirt.Host import Host
from ZenPacks.zenoss.oVirt.Vms import Vms

### IRelatable Adapters

class SystemRelatable(BaseRelatable):
    adapts(System)

    group = 'oVirt'


class DataCenterRelatable(DeviceComponentRelatable):
    adapts(DataCenter)

    group = 'oVirt'


class ClusterRelatable(DeviceComponentRelatable):
    adapts(Cluster)

    group = 'oVirt'


class HostRelatable(DeviceComponentRelatable):
    adapts(Host)

    group = 'oVirt'


class VmsRelatable(DeviceComponentRelatable):
    adapts(Vms)

    group = 'oVirt'

### IRelationsProvider Adapters

class SystemRelationsProvider(BaseRelationsProvider):
    adapts(System)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for datacenter in self._adapted.datacenters():
                yield self.constructRelationTo(datacenter, TAG_IMPACTS)


class DataCenterRelationsProvider(BaseRelationsProvider):
    adapts(DataCenter)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for cluster in self._adapted.clusters():
                yield self.constructRelationTo(cluster, TAG_IMPACTS)

        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(
                self._adapted.system(), TAG_IMPACTED_BY)


class ClusterRelationsProvider(BaseRelationsProvider):
    adapts(Cluster)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for vm in self._adapted.vms():
                yield self.constructRelationTo(vm, TAG_IMPACTS)

        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(
                self._adapted.datacenter(), TAG_IMPACTED_BY)


class VmsRelationsProvider(BaseRelationsProvider):
    adapts(Vms)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(
                self._adapted.cluster(), TAG_IMPACTED_BY)


class HostRelationsProvider(BaseRelationsProvider):
    adapts(Host)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for cluster in self._adapted.clusters():
                yield self.constructRelationTo(cluster, TAG_IMPACTS)
