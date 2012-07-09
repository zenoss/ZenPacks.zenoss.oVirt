###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2012 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import logging
log = logging.getLogger('zen.oVirt')

from twisted.internet.defer import DeferredList

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from ZenPacks.zenoss.oVirt.utils import add_local_lib_path
add_local_lib_path()

import txovirt


class oVirt(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'zOVirtUrl',
        'zOVirtUser',
        'zOVirtPassword',
        'zOVirtDomain',
    )
    collector_map_order = ['data_centers', 'clusters', 'hosts','vms']
    collector_map = {'data_centers':
                              {'command': 'datacenters',
                                #'attributes': ['name','guid','href','description','storage_type','major_version','minor_version','element_status'],
                                'relname': 'datacenters',
                                'modname': 'ZenPacks.zenoss.oVirt.DataCenter',
                                'attributes': ['guid', 'name'], # This needs to have the guid first because its the id we are using else where.
                                'name': {'default': '',
                                          'lookup': "find('name').text",
                                          'prepId': True,
                                          'name': 'title',
                                        },
                                'guid': {'default': '',
                                          'lookup': "attrib['id']",
                                          'prepId': True,
                                          'name': 'id',
                                        },
                              },
                      'clusters':
                               {'command': 'clusters',
                                'relname': 'clusters',
                                'modname': 'ZenPacks.zenoss.oVirt.Cluster',
                                'attributes': ['guid', 'name', 'datacenter_guid'],  # This needs to have the guid first because its the id we are using else where
                                'compname': '"datacenters/%s" % self.prepId(data["clusters"][id]["datacenter_guid"])',
                                'name': {'default': '',
                                          'lookup': "find('name').text",
                                          'prepId': True,
                                          'name': 'title',
                                        },
                                'guid': {'default': '',
                                          'lookup': "attrib['id']",
                                          'prepId': True,
                                          'name': 'id',
                                        },
                                'datacenter_guid': {'default': '',
                                          'lookup': "find('data_center').attrib['id']",
                                        },
                               },
                      'hosts':
                            {'command': 'hosts',
                             'relname': 'hosts',
                             'modname': 'ZenPacks.zenoss.oVirt.Host',
                             'attributes': ['guid', 'name', 'cluster_guid'],  # This needs to have the guid first because its the id we are using else where
                             'compname': '"datacenters/%s/clusters/%s" % self.host_compname(data,id)',
                             'name': {'default': '',
                                          'lookup': "find('name').text",
                                          'prepId': True,
                                          'name': 'title',
                                        },
                             'guid': {'default': '',
                                          'lookup': "attrib['id']",
                                          'prepId': True,
                                          'name': 'id',
                                        },
                             'cluster_guid': {'default': '',
                                          'lookup': "find('cluster').attrib['id']",
                                        },
                            },
                      'vms':
                            {'command': 'vms',
                             'relname': 'vms',
                             'modname': 'ZenPacks.zenoss.oVirt.Vms',
                             'attributes': ['guid', 'name', 'cluster_guid'],  # This needs to have the guid first because its the id we are using else where
                             'compname': '"datacenters/%s/clusters/%s" % self.vm_compname(data,id)',
                             'name': {'default': '',
                                          'lookup': "find('name').text",
                                          'prepId': True,
                                          'name': 'title',
                                        },
                             'guid': {'default': '',
                                          'lookup': "attrib['id']",
                                          'prepId': True,
                                          'name': 'id',
                                        },
                             'cluster_guid': {'default': '',
                                          'lookup': "find('cluster').attrib['id']",
                                        },
                            },
                     }
    #Helper Method
    def host_compname(self, data, host_id):
        cluster_guid = self.prepId(data["hosts"][host_id]["cluster_guid"])
        datacenter_guid = self.prepId(data["clusters"][cluster_guid]["datacenter_guid"])
        return (datacenter_guid, cluster_guid)

    #Helper Method
    def vm_compname(self, data, vm_id):
        cluster_guid = self.prepId(data["vms"][vm_id]["cluster_guid"])
        datacenter_guid = self.prepId(data["clusters"][cluster_guid]["datacenter_guid"])
        return (datacenter_guid, cluster_guid)

    def _combine(self, results):
        """Combines all responses within results into a single data structure"""

        data = []
        for success, result in results:
            if not success:
                log.error("API Error: %s", result.getErrorMessage())
                continue
            data.append(result)
        return data

    def collect(self, device, unused):
        """Collect model-related information using the txovirt library."""

        if not device.zOVirtUrl:
            log.error('zOVirtUrl is not set. Not discovering')
            return None

        if not device.zOVirtUser:
            log.error('zOVirtUser is not set. Not discovering')
            return None

        if not device.zOVirtDomain:
            log.error('zOVirtDomain is not set. Not discovering')
            return None

        if not device.zOVirtPassword:
            log.error('zOVirtPassord is not set. Not discovering')
            return None

        client = txovirt.Client(
             device.zOVirtUrl,
             device.zOVirtUser,
             device.zOVirtDomain,
             device.zOVirtPassword)

        deferreds = []
        for key in self.collector_map_order:
            deferreds.append(client.request(self.collector_map[key]['command']))
        d = DeferredList(deferreds, consumeErrors=True).addCallback(self._combine)
        return d

    def process(self, device, results, unused):
        relmap = []
        data = {}
        for result in results:
            key = result.tag
            data.setdefault(key, {})
            if 'compname' in self.collector_map[key].keys():
                objmaps = {} 
            else:
                objmaps = []

            for entry in result.getchildren():
                skey = None
                id = None

                for attribute in self.collector_map[key]['attributes']:
                    if 'name' in self.collector_map[key][attribute].keys():
                        skey = self.collector_map[key][attribute]['name']
                    else:
                        skey = attribute

                    results = None
                    try:
                        if 'prepId' in self.collector_map[key][attribute].keys():
                            results = self.prepId(eval('entry.' + self.collector_map[key][attribute]['lookup']))
                        else:
                            results = eval('entry.' + self.collector_map[key][attribute]['lookup'])
                    except:
                        log.warn("attribute not found, using default")
                        if 'prepId' in self.collector_map[key][attribute].keys():
                            results = self.prepId(eval('entry.' + self.collector_map[key][attribute]['default']))
                        else:
                            results = eval('entry.' + self.collector_map[key][attribute]['default'])

                    # Store the id mapping
                    if skey == 'id':
                        id = results
                        data[key].setdefault(id, {})

                    # Abort if the id isnt found first. All elements must have an id.
                    if not id:
                        log.error("Modeller Error: No id set for %s", key)
                        return None

                    # store the results to the data dict
                    data[key][id][skey] = results
                
            if 'compname' in self.collector_map[key].keys():
                for id in set(data[key].keys()):
                    compname = eval(self.collector_map[key]['compname'])
                    print "%s %s %s" % (key,id,compname)
                    objmaps.setdefault(compname, [])
                    print compname,data[key][id]
                    objmaps[compname].append(ObjectMap(data=data[key][id]))
            else:
                for id in set(data[key].keys()):
                    objmaps.append(ObjectMap(data=data[key][id]))

            print 
            print objmaps
            print 
            if 'compname' in self.collector_map[key].keys():
                for compname, objmap in objmaps.items():
                    rm = RelationshipMap(
                        compname=compname,
                        relname=self.collector_map[key]['relname'],
                        modname=self.collector_map[key]['modname'],
                        objmaps=objmap
                        )
                    relmap.append(rm)
            else:
                rm = RelationshipMap(
                    relname=self.collector_map[key]['relname'],
                    modname=self.collector_map[key]['modname'],
                    objmaps=objmaps
                    )
                relmap.append(rm)
        
        from pprint import pprint
        pprint(data)
        #pprint(relmap)
        return relmap

"""
(Pdb) result.getchildren()[1].find('name').txt
*** AttributeError: 'Element' object has no attribute 'txt'
(Pdb) result.getchildren()[1].find('name').text
'Default'
(Pdb) result.getchildren()[0].find('name').text

results[0].tag
'clusters'
"""
