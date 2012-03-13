######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import logging
log = logging.getLogger('zen.ovirt.impact')

from zope.component import adapts
from zope.interface import implements

from Products.ZenUtils.guid.interfaces import IGlobalIdentifier

from ZenPacks.zenoss.Impact.impactd import Trigger
from ZenPacks.zenoss.Impact.stated.interfaces import IStateProvider
from ZenPacks.zenoss.Impact.impactd.relations import ImpactEdge
from ZenPacks.zenoss.Impact.impactd.interfaces \
    import IRelationshipDataProvider, INodeTriggers

from Products.ZenModel.Device import Device as CoreDevice
from .Device import Device


class GuestRelationsProvider(object):
    implements(IRelationshipDataProvider)
    adapts(CoreDevice)

    relationship_provider = "oVirt"

    def __init__(self, adapted):
        self._object = adapted

    def belongsInImpactGraph(self):
        return True

    def getEdges(self):

        comp = self._object.getOVirtComponentOnHost()
        if comp:
            # we are a device monitored thru SNMP or ssh that is an oVirt VM. The
            # call above found the host we are running on, and the component representing
            # us underneath it. We are now going to say that we *are* the component, from
            # the VM device's perspective. We depend on it, and it depends on us:

            log.critical("KABOOM")
            e1 = IGlobalIdentifier(comp).getGUID()
            e2 = IGlobalIdentifier(self._object.device()).getGUID()

            yield ImpactEdge( e1, e2, self.relationship_provider )
            yield ImpactEdge( e2, e1, self.relationship_provider )


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

        for exampleComponent in self._object.exampleComponents():
            c_guid = IGlobalIdentifier(exampleComponent).getGUID()
            yield ImpactEdge(guid, c_guid, self.relationship_provider)


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

