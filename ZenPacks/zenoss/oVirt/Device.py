######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from Products.ZenModel.Device import Device as BaseDevice


class Device(BaseDevice):
    meta_type = portal_type = 'Device'

    lastEvent = 0

    _properties = BaseDevice.BaseDevice + (
        {'id':'lastEvent', 'type':'int', 'mode':'w'},
    )

    def getRelatedComponents(self, guid, meta_type):
        """
        Find all components that reference the provided guid.

        Specifying the meta-type of a component which matches the guid
        returns the component.
        """
        if not meta_type.startswith('GenericComponent_'):
            meta_type = 'GenericComponent_' + meta_type

        comps = []
        for comp in self.getDeviceComponents(type=meta_type):
            values = comp.attributes.values()
            if guid in values:
                comps.append(comp)
        return comps

    def getComponentByGuid(self, guid):
        """
        Find the components that matches the provided guid.
        """
        for comp in self.genericComponents():
            if comp.attributes.get('guid') == guid:
                return comp

