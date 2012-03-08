######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################


from zope.component import adapts
from zope.interface import implements

from Products.ZenUtils.guid.interfaces import IGlobalIdentifier

from ZenPacks.zenoss.Impact.impactd import Trigger
from ZenPacks.zenoss.Impact.stated.interfaces import IStateProvider
from ZenPacks.zenoss.Impact.impactd.relations import ImpactEdge
from ZenPacks.zenoss.Impact.impactd.interfaces \
    import IRelationshipDataProvider, INodeTriggers

from .Device import Device


class DeviceRelationsProvider(object):
    implements(IRelationshipDataProvider)
    adapts(Device)

    relationship_provider = "oVirtImpact"

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

