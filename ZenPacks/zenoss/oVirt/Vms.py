###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2012, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from Products.ZenRelations.RelSchema import ToManyCont, ToMany, ToOne

from ZenPacks.zenoss.oVirt import BaseComponent


class Vms(BaseComponent):
    meta_type = portal_type = "oVirtVms"

    vms_type = None
    state = None
    memory = None
    cpu_cores = None
    cpu_sockets = None
    os_type = None
    os_boot = None
    os_kernel = None
    os_initrd = None
    os_cmdline = None
    high_availability_enabled = None
    high_availability_priority = None
    display_type = None
    display_address = None
    display_port = None
    display_secureport = None
    display_monitors = None
    #template
    start_time = None
    creation_time = None
    origin = None
    stateless = None
    placement_policy_affinity = None
    memory_policy_guaranteed = None
    usb_enabled = None

    _relations = BaseComponent._relations + (
        ('cluster', ToOne(ToManyCont,
             'ZenPacks.zenoss.oVirt.Cluster.Cluster',
             'vms')
              ),

        ('disks', ToMany(ToOne,
             'ZenPacks.zenoss.oVirt.Disk.Disk',
             'vm')
              ),

        ('nics', ToManyCont(ToOne,
             'ZenPacks.zenoss.oVirt.VmNic.VmNic',
             'vm')
              ),
        )

    def device(self):
        return self.cluster().device()
