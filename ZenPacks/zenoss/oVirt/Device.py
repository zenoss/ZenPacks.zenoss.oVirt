######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from Products.ZenModel.Device import Device as BaseDevice


class Device(BaseDevice):
    meta_type = portal_type = 'Device'

    lastEvent = 0

    _properties = BaseDevice._properties + (
        {'id':'lastEvent', 'type':'int', 'mode':'w'},
    )

    def getRelatedComponents(self, guid, meta_type):
        """
        Find all components that reference the provided guid.

        Specifying the meta-type of a component which matches the guid
        returns the component.
        """
        comps = []
        for comp in self.getComponents(meta_type=meta_type):
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

    def getComponents(self, meta_type):
        """
        Find all components by that match the meta_type.
        """
        if not meta_type.startswith('GenericComponent_'):
            meta_type = 'GenericComponent_' + meta_type

        return self.getDeviceComponents(type=meta_type)

    def getManagedDeviceLink(self, comp):
        if comp.component_type == 'vms':
            macaddrs = [x.attributes.get('mac') for x in comp.subcomponents() \
                               if x.component_type == 'vms_nics' ]
            guest = self.getDeviceByMac(macaddrs)
            if guest is not None:
                return """<a href="%s">%s</a>""" % (
                    guest.absolute_url(),
                    comp.attributes['name']
                )

        elif comp.component_type == 'hosts':
            ipaddrs = [x.attributes.get('ip_address') for x in comp.subcomponents() \
                               if x.component_type == 'hosts_nics' ]
            guest = self.getDeviceByIp(ipaddrs)
            if guest is not None:
                return """<a href="%s">%s</a>""" % (
                    guest.absolute_url(),
                    comp.attributes['name']
                )

            macaddrs = [x.attributes.get('mac') for x in comp.subcomponents() \
                               if x.component_type == 'hosts_nics' ]
            guest = self.getDeviceByMac(macaddrs)
            if guest is not None:
                return """<a href="%s">%s</a>""" % (
                    guest.absolute_url(),
                    comp.attributes['name']
                )

        return comp.attributes['name']

    def getMacAddressLink(self, mac=None):
        if mac is None:
            return
 
        device = self.getDeviceByMac([mac])
        if device is not None:
            return """<a href="%s">%s</a>""" % (
                    device.absolute_url(),
                    mac
                    )
        return mac

    def getDeviceByMac(self, macaddrs):
        cat = self.dmd.ZenLinkManager._getCatalog(layer=2)
        if cat is None:
            return

        for mac in macaddrs:
            brains = cat(macaddress=mac)
            if brains:
                try:
                    return brains[0].getObject().device()
                except Exception:
                    pass

    def getDeviceByIp(self, ips):
        for ip in ips:
            device = self.dmd.Devices.findDeviceByIdOrIp(ip)
            if device:
                return device
            
            foundip = self.dmd.Networks.findIp(ip)
            if foundip and foundip.device():
                return foundip.device()

