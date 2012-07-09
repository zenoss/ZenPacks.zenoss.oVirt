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
    collector_map_order = ['data_centers', 'clusters','hosts','vms']
    collector_map = {'data_centers':
                              {'command': 'datacenters',
                                #'attributes': ['name','guid','href','description','storage_type','major_version','minor_version','element_status'],
                                'relname': 'datacenters',
                                'modname': 'ZenPacks.zenoss.oVirt.DataCenter',
                                'attributes': ['name', 'guid'],
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
                                'attributes': ['name', 'guid', 'datacenter_guid'],
                                'compname': '"datacenters/%s" % self.prepId(data["datacenter_guid"])',
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
                             'modname': 'ZenPacks.zenoss.oVirt.Hosts',
                             'attributes': ['name', 'guid', 'cluster_guid'],
                             'compname': '"clusters/%s" % self.prepId(data["cluster_guid"])',
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
                             'attributes': ['name', 'guid', 'cluster_guid'],
                             'compname': '"clusters/%s" % self.prepId(data["cluster_guid"])',
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
        #d = DeferredList((
        #     client.request('datacenters'),
             #client.request('clusters'),
             #client.request('vms'),
             #client.request('hosts'),
             #client.request('networks'),
             #client.request('roles'),
             #client.request('storagedomains'),
             #client.request('templates'),
             #client.request('tags'),
             ##client.request('users'),
             #client.request('groups'),
             #client.request('domains'),
             #client.request('vmpools')
           #), consumeErrors=True).addCallback(self._combine)

    def process(self, device, results, unused):
        relmap = []
        for result in results:
            objmaps = {}
            key = result.tag

            for entry in result.getchildren():
                skey = None
                data = {}
                for attribute in self.collector_map[key]['attributes']:
                    if 'name' in self.collector_map[key][attribute].keys():
                        skey = self.collector_map[key][attribute]['name']
                    else:
                        skey = attribute
                    try:
                        if 'prepId' in self.collector_map[key][attribute].keys():
                            data[skey] = self.prepId(eval('entry.' + self.collector_map[key][attribute]['lookup']))
                        else:
                            data[skey] = eval('entry.' + self.collector_map[key][attribute]['lookup'])
                    except:
                        log.warn("attribute not found, using default")
                        if 'prepId' in self.collector_map[key][attribute].keys():
                            data[skey] = self.prepId(eval('entry.' + self.collector_map[key][attribute]['default']))
                        else:
                            data[skey] = eval('entry.' + self.collector_map[key][attribute]['default'])

                if 'compname' in self.collector_map[key].keys():
                    compname = eval(self.collector_map[key]['compname'])
                    objmaps = {}
                    objmaps.setdefault(compname, [])
                    objmaps[compname].append(ObjectMap(data=data))
                    for compname, objmap in objmaps.items():
                        rm = RelationshipMap(
                            compname=compname,
                            relname=self.collector_map[key]['relname'],
                            modname=self.collector_map[key]['modname'],
                            objmaps=objmap
                        )
                        relmap.append(rm)
                else:
                    objmaps = []
                    objmaps.append(ObjectMap(data=data))
                    rm = RelationshipMap(
                        relname=self.collector_map[key]['relname'],
                        modname=self.collector_map[key]['modname'],
                        objmaps=objmaps
                        )
                    relmap.append(rm)
        print relmap
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
