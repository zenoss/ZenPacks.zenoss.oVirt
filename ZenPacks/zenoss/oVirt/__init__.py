######################################################################
#
# Copyright 2012 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import Globals

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.Zuul.interfaces import ICatalogTool
from Products.ZenUtils.Utils import unused, monkeypatch
from Products.ZenModel.Device import Device

unused(Globals)


#
# Dear gods, do we *really* need to do this to muck with the links?
# Haven't we done this like 30 times already?
#
@monkeypatch("Products.ZenModel.Device.Device")
def getOVirtComponentOnHost(self):
    macaddrs, ips = self.getMacsIpsFromInterfaces()

    gcType = 'ZenPacks.zenoss.Liberator.GenericComponent.GenericComponent'
    path = '/zport/dmd/Devices/oVirt'

    catalog = ICatalogTool(self.dmd)
    for brain in catalog.search(types=(gcType), paths=(path)):
        try:
            obj = brain.getObject()
        except Exception:
            continue

        if obj.component_type != 'vms_nics':
            continue

        ip = obj.attributes.get('ip_address')
        if ip == self.manageIp or ip in ips:
            return obj.parentComponent()

        mac = obj.attributes.get('mac')
        if mac in macaddrs:
            return obj.parentComponent()

@monkeypatch("Products.ZenModel.Device.Device")
def getMacsIpsFromInterfaces(self):
    macaddrs = []
    ips = []
    for iface in self.os.interfaces():
        mac = iface.getInterfaceMacaddress().lower()
        macaddrs.append(mac)

        ifips = [ip.split('/')[0] for ip in iface.getIpAddresses()]
        ips.extend(ifips)

    return macaddrs, ips


# Old-school monkeypatch -- because we can't fix in core.
orig_getExpandedLinks = Device.getExpandedLinks


def ovirt_getExpandedLinks(self):
    links = orig_getExpandedLinks(self)
    host = self.getOVirtComponentOnHost()
    if host:
        links = '<a href="%s">oVirt VM %s</a><br/>%s' % (
            host.getPrimaryUrlPath(),
            host.titleOrId(),
            links)

    return links

Device.getExpandedLinks = ovirt_getExpandedLinks

class ZenPack(ZenPackBase):

     packZProperties = [
         ('zOVirtServerName', '', 'string'),
         ('zOVirtUser', 'admin', 'string'),
         ('zOVirtPassword', '', 'password'),
         ('zOVirtDomain', 'internal', 'string'),
         ('zOVirtPort', 8080, 'int'),
         #('zOVirtProtocol', 'http', 'string'),
         ]

