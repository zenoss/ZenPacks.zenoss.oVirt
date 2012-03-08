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
    adapts(ExampleDevice)

    def relations(self, type=TAG_ALL):
        """
        ExampleDevices impact all of their ExampleComponents.
        """
        if type in (TAG_ALL, TAG_IMPACTS):
            for exampleComponent in self._adapted.exampleComponents():
                yield self.constructRelationTo(exampleComponent, TAG_IMPACTS)


class ExampleComponentRelationsProvider(BaseRelationsProvider):
    adapts(GenericComponent)

    def relations(self, type=TAG_ALL):
        """
        ExampleComponents are impacted by their ExampleDevice.
        """
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(
                self._adapted.exampleDevice(), TAG_IMPACTED_BY)
