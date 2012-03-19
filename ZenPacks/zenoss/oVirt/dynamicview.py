######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging
log = logging.getLogger('zen.oVirt.dynamicview')

from zope.component import adapts

from ZenPacks.zenoss.DynamicView import TAG_IMPACTED_BY, TAG_IMPACTS, TAG_ALL
from ZenPacks.zenoss.DynamicView.model.adapters import DeviceComponentRelatable
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelationsProvider

from ZenPacks.zenoss.oVirt.Device import Device

from ZenPacks.zenoss.Liberator.GenericComponent import GenericComponent


### IRelatable Adapters

class OVirtComponentRelatable(DeviceComponentRelatable):
    """
    This maps a generic component class to a group name, which is then
    linked to a view.
    """
    adapts(GenericComponent)

    @property
    def group(self):
        compType = self._adapted.component_type
        return {
            'vms': 'Virtual Machines',
            'clusters': 'Clusters',
            'datacenters': 'Datacenters',
            'hosts': 'Hosts',
        }.get(compType, compType)


### IRelationsProvider Adapters

class DeviceRelationsProvider_ovirt_datacenter(BaseRelationsProvider):
    adapts(Device)

    def relations(self, type=TAG_ALL):
        """
        oVirt manager relates to data centers
        """
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            for dc in self._adapted.getComponents(meta_type='datacenters'):
                yield self.constructRelationTo(dc, TAG_IMPACTED_BY)


class OVirtComponentRelationsProvider(BaseRelationsProvider):
    adapts(GenericComponent)

    impactsChain = {
        'vms': ['clusters',],
        'hosts': ['clusters',],
        'clusters': ['datacenters',],
    }

    impactedByChain = {
        'datacenters': ['clusters',],
        'clusters': ['hosts', 'vms'],
        'hosts': ['vms',],
    }

    def relations(self, type=TAG_ALL):
        """
        Match all oVirt types
        """
        # FIXME: make zp-specific component types to make matching easier
        # FIXME: define a generic way to relate components via XML
        element = self._adapted.component_type
        if element not in (
            'vms', 'vmpools', 'storage_domains', 'networks', 'hosts', 'clusters',
            'datacenters',
        ):
            raise StopIteration

        dev = self._adapted.host()
        guid = self._adapted.attributes.get('guid')
        if guid is None:
            # Model is broken as all components must have a guid
            log.error("Noticed a broken component %s on device %s -- missing GUID %s",
                      self._adapted.component_type, dev.id, guid)
            raise StopIteration

        # What is this element impacted by?
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            nextElementTypes = self.impactedByChain.get(element)
            if nextElementTypes is not None:
                for nextElementType in nextElementTypes:
                    for obj in dev.getRelatedComponents(guid, nextElementType):
                        yield self.constructRelationTo(obj, TAG_IMPACTED_BY)

            elif element == 'vms':
                guest = self.getGuest(dev)
                if guest is not None:
                    yield self.constructRelationTo(guest, TAG_IMPACTED_BY)
            else:
                log.critical("No mapping from %s to an IMPACTED_BY element -- skipping", element)

        # What does this element impact?
        elif type in (TAG_IMPACTS,):
            nextElementTypes = self.impactsChain.get(element)
            if nextElementTypes is not None:
                for nextElementType in nextElementTypes:
                    for obj in dev.getRelatedComponents(guid, nextElementType):
                        yield self.constructRelationTo(obj, TAG_IMPACTS)

            elif element == 'datacenters':
                    yield self.constructRelationTo(dev, TAG_IMPACTS)

            else:
                log.warn("No mapping from %s to an IMPACTS element -- skipping", element)

            if element == 'vms':
                guest = self.getGuest(dev)
                if guest is not None:
                    yield self.constructRelationTo(guest, TAG_IMPACTS)

    def getGuest(self, dev):
        mac = self._adapted.attributes.get('mac')
        if mac is not None:
            return dev.getDeviceByMac([mac])

