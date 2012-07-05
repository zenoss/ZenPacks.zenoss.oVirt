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

from Products.ZenRelations.RelSchema import ToManyCont, ToOne


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


    _relations = Device._relations + (
        ('cluster', ToManyCont(ToOne, 
             'ZenPacks.zenoss.oVirt.Cluster.Cluster',
             'vms')
              ),
        #nics
        #snapshots
        #disks
        #cdroms
        #statistics
        )

    def device(self):
        return self.cluster().device()