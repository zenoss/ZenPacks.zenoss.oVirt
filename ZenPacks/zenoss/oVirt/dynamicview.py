######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from zope.component import adapts

from ZenPacks.zenoss.DynamicView import TAG_IMPACTED_BY, TAG_IMPACTS, TAG_ALL
from ZenPacks.zenoss.DynamicView.model.adapters import DeviceComponentRelatable
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelationsProvider

from Products.ZenModel.Device import Device as BaseDevice

from ZenPacks.zenoss.Liberator.GenericComponent import GenericComponent


### IRelatable Adapters

class ExampleComponentRelatable(DeviceComponentRelatable):
    adapts(GenericComponent)

    group = 'Liberator Components'


### IRelationsProvider Adapters

class DeviceRelationsProvider_ovirt_datacenter(BaseRelationsProvider):
    adapts(BaseDevice)

    def relations(self, type=TAG_ALL):
        """
        oVirt manager relates to data centers
        """
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            for dc in self._adapted.getComponents(meta_type='datacenters'):
                yield self.constructRelationTo(dc, TAG_IMPACTED_BY)


class OVirtComponentRelationsProvider(BaseRelationsProvider):
    adapts(GenericComponent)

    impactedByChain = {
        'vms': 'hosts',
        'hosts': 'clusters',
        'clusters': 'datacenters',
    }

    impactsChain = {
        'datacenters': 'clusters',
        'clusters': 'hosts',
        'hosts': 'vms',
    }

    def relations(self, type=TAG_ALL):
        """
        Match all oVirt types
        """
        # FIXME: make zp-specific component types to make matching easier
        # FIXME: define a generic way to relate components via XML
        element = self._adapted.component_type
        if element not in (
            'vm', 'vmpool', 'storage_domain', 'network', 'host', 'cluster', 'domain',
            'data_center',
        ):
            raise StopIteration

        dev = self._adapted.host()
        guid = self._adapted.attributes.get('guid')
        if guid is None:
            # Model is broken as all components must have a guid
            raise StopIteration

        # What is this element impacted by?
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            nextElementType = self.impactedByChain.get(element)
            try:
                obj = dev.getRelatedComponents(guid, nextElementType)[0]
                if obj:
                    yield self.constructRelationTo(obj, TAG_IMPACTED_BY)
            except IndexError:
                pass

        # What does this element impact?
        elif type in (TAG_IMPACTS,):
            nextElementType = self.impactsChain.get(element)
            try:
                obj = dev.getRelatedComponents(guid, nextElementType)[0]
                if obj:
                    yield self.constructRelationTo(obj, TAG_IMPACTS)
            except IndexError:
                pass

