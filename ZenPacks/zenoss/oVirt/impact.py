######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging
log = logging.getLogger('zen.ovirt.impact')

from zope.component import adapts, subscribers
from zope.interface import implements

from Products.ZenUtils.guid.interfaces import IGlobalIdentifier

from ZenPacks.zenoss.Impact.impactd import Trigger
#from ZenPacks.zenoss.Impact.stated.interfaces import IStateProvider
from ZenPacks.zenoss.Impact.impactd.relations import ImpactEdge
from ZenPacks.zenoss.Impact.impactd.interfaces \
    import IRelationshipDataProvider, INodeTriggers

from Products.ZenModel.Device import Device as CoreDevice
from .Device import Device

from ZenPacks.zenoss.Liberator.GenericComponent import GenericComponent


class GuestRelationsProvider(object):
    implements(IRelationshipDataProvider)
    adapts(CoreDevice)

    relationship_provider = "oVirt"

    def __init__(self, adapted):
        self._object = adapted

    def belongsInImpactGraph(self):
        return True

    def getEdges(self):

        # For ImpactEdges, the second argument depends upon the first argument
        devguid = IGlobalIdentifier(self._object).getGUID()
        comp = self._object.getOVirtComponentOnHost()
        if comp:
            # we are a device monitored thru SNMP or ssh that is an oVirt VM. The
            # call above found the host we are running on, and the component representing
            # us underneath it. We are now going to say that we *are* the component, from
            # the VM device's perspective. We depend on it, and it depends on us:

            component = IGlobalIdentifier(comp).getGUID()
        #    device = IGlobalIdentifier(self._object.device()).getGUID()

            # Device impacted by component
            yield ImpactEdge( component, devguid, self.relationship_provider )
            #yield ImpactEdge( component, device, self.relationship_provider )
            # Component impacted by device
            #yield ImpactEdge( device, component, self.relationship_provider )


class DeviceRelationsProvider(object):
    implements(IRelationshipDataProvider)
    adapts(Device)

    relationship_provider = "oVirt"

    def __init__(self, adapted):
        self._object = adapted

    def belongsInImpactGraph(self):
        return True

    def getEdges(self):
        """
        oVirt manager has multiple datacenters.
        """
        guid = IGlobalIdentifier(self._object).getGUID()
        for dc in self._object.getComponents(meta_type='datacenters'):
            dc_guid = IGlobalIdentifier(dc).getGUID()
            # For ImpactEdges, the second argument depends upon the first argument
            yield ImpactEdge(guid, dc_guid, self.relationship_provider)


class LiberatorComponentRelationsProvider(object):
    implements(IRelationshipDataProvider)
    adapts(GenericComponent)

    relationship_provider = "oVirt"

    impactedByChain = {
        'vms': ['clusters',],
        'clusters': ['datacenters',],
    }

    typeToAttribute = {
        'clusters': 'cluster_guid',
        'datacenters': 'datacenter_guid',
    }

    def __init__(self, adapted):
        self._object = adapted

    def belongsInImpactGraph(self):
        return True

    def getEdges(self):
        element = self._object.component_type
        nextElementTypes = self.impactedByChain.get(element)
        if nextElementTypes is not None:
            guid = IGlobalIdentifier(self._object).getGUID()

            # Search for related component
            oVirtGuid = self._object.attributes.get('guid')
            dev = self._object.device()
            for nextElementType in nextElementTypes:
                obj = self._getRelatedObjOfType(nextElementType, dev)
                if obj is None:
                    continue

                log.critical("Found obj, relating (%s) %s --> %s (%s)", self._object.titleOrId(), element, nextElementType, obj.titleOrId())
                objGuid = IGlobalIdentifier(obj).getGUID()
                # For ImpactEdges, the second argument depends upon the first argument
                yield ImpactEdge(objGuid, guid, self.relationship_provider)

    def _getRelatedObjOfType(self, nextElementType, dev):
        attr = self.typeToAttribute.get(nextElementType)
        if attr is None:
            return

        objOVirtGuid = self._object.attributes.get(attr)
        if objOVirtGuid is None:
            return

        return dev.getComponentByGuid(objOVirtGuid)


def getRedundancyTriggers(guid, format):
    availability = 'AVAILABILITY'
    percent = 'policyPercentageTrigger'
    threshold = 'policyThresholdTrigger'

    return (
        Trigger(guid, format % 'DOWN', percent, availability, dict(
            state='DOWN', dependentState='DOWN', threshold='100',
        )),
        Trigger(guid, format % 'DEGRADED', threshold, availability, dict(
            state='DEGRADED', dependentState='DEGRADED', threshold='1',
        )),
        Trigger(guid, format % 'ATRISK_1', threshold, availability, dict(
            state='ATRISK', dependentState='DOWN', threshold='1',
        )),
        Trigger(guid, format % 'ATRISK_2', threshold, availability, dict(
            state='ATRISK', dependentState='ATRISK', threshold='1',
        )),
    )


class OVirtDatacenterTriggers(object):
    """
    A datacenter is down if all clusters are down.
    """
    implements(INodeTriggers)

    def __init__(self, adapted):
        self._object = adapted

    def get_triggers(self):
        if self._object.meta_type != 'GenericComponent_datacenters':
            return ()

        return getRedundancyTriggers(
            IGlobalIdentifier(self._object).getGUID(),
            'DEFAULT_OVIRT_DATACENTER_TRIGGER_ID_%s',
        )


class OVirtClusterTriggers(object):
    """ 
    A cluster is down if all hosts are down.
    """
    implements(INodeTriggers)

    def __init__(self, adapted):
        self._object = adapted

    def get_triggers(self):
        if self._object.meta_type != 'GenericComponent_clusters':
            return ()

        return getRedundancyTriggers(
            IGlobalIdentifier(self._object).getGUID(),
            'DEFAULT_OVIRT_CLUSTER_TRIGGER_ID_%s',
        )

