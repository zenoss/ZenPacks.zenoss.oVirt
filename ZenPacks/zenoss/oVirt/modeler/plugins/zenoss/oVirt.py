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

from twisted.internet.defer import DeferredList, inlineCallbacks, returnValue

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps \
    import ObjectMap, RelationshipMap, MultiArgs

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

    # Order to collect from the ovirt server
    collector_map_order = ['data_centers', 'storage_domains', 'clusters', 'hosts', 'vms']

    # Order to build the datamap
    data_map_order = ['data_centers', 'storage_domains', 'clusters', 'hosts', 'vms', 'disks', 'nics', 'host_nics']

    collector_map = {'data_centers':
                              {'command': 'datacenters',
                                #'attributes': ['name','guid','href','description','storage_type','major_version','minor_version','element_status'],
                                'relname': 'datacenters',
                                'modname': 'ZenPacks.zenoss.oVirt.DataCenter',
                                'attributes': ['guid', 'name', 'description', 'storage_type', 'storage_format', 'version_major', 'version_minor', 'element_status'],  # This needs to have the guid first because its the id we are using else where.
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
                                'description': {'default': "",
                                          'lookup': "find('description').text",
                                        },
                                'storage_type': {'default': "",
                                          'lookup': "find('storage_type').text",
                                        },
                                'storage_format': {'default': '',
                                          'lookup': "find('storage_format').text",
                                        },
                                'version_major': {'default': '',
                                          'lookup': "find('version').attrib['major']",
                                        },
                                'version_minor': {'default': '',
                                          'lookup': "find('version').attrib['minor']",
                                        },
                                'element_status': {'default': '',
                                          'lookup': "find('status').find('state').text",
                                          'name': 'status'
                                        },
                              },
                      'clusters':
                               {'command': 'clusters',
                                'relname': 'clusters',
                                'modname': 'ZenPacks.zenoss.oVirt.Cluster',
                                'attributes': ['guid', 'name', 'datacenter_guid', 'description'],  # This needs to have the guid first because its the id we are using else where
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
                                          'delete': True,
                                        },
                                'description': {'default': '',
                                          'lookup': "find('description').text",
                                        },
                               },
                      'hosts':
                            {'command': 'hosts',
                             'relname': 'hosts',
                             'modname': 'ZenPacks.zenoss.oVirt.Host',
                             'attributes': ['guid', 'name', 'cluster_guid',
                                            'address', 'status_state', 'status_detail',
                                            'memory', 'cpu_sockets', 'cpu_cores',
                                            'cpu_name', 'cpu_speed', 'storage_manager'],  # This needs to have the guid first because its the id we are using else where
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
                                          'delete': True,
                                        },
                             'address': {'default': '',
                                          'lookup': "find('address').text",
                                        },
                             'status_state': {'default': '',
                                          'lookup': "find('status').find('state').text",
                                        },
                             'status_detail': {'default': '',
                                          'lookup': "find('status').find('detail').text",
                                        },
                             'memory': {'default': '',
                                          'lookup': "find('memory').text",
                                        },
                             'cpu_cores': {'default': '',
                                          'lookup': "find('cpu').find('topology').attrib['cores']",
                                        },
                             'cpu_sockets': {'default': '',
                                          'lookup': "find('cpu').find('topology').attrib['sockets']",
                                        },
                             'cpu_name': {'default': '',
                                          'lookup': "find('cpu').find('name').text",
                                        },
                             'cpu_speed': {'default': '',
                                          'lookup': "find('cpu').find('speed').text",
                                        },
                             'storage_manager': {'default': '',
                                          'lookup': "find('storage_manager').text",
                                        },
                            },
                      'host_nics':
                            {'relname': 'nics',
                             'modname': 'ZenPacks.zenoss.oVirt.HostNic',
                             'attributes': ['guid', 'name', 'host_guid',
                                            'mac', 'ip', 'netmask',
                                            'gateway', 'status', 'speed'],  # This needs to have the guid first because its the id we are using else where
                             'compname': '"datacenters/%s/clusters/%s/hosts/%s" % self.hostnic_compname(data,id)',
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
                             'host_guid': {'default': '',
                                          'lookup': "find('host').attrib['id']",
                                          'delete': True,
                                        },
                             'mac': {'default': '',
                                          'lookup': "find('mac').attrib['address']",
                                        },
                             'ip': {'default': '',
                                          'lookup': "find('ip').attrib['address']",
                                        },
                             'netmask': {'default': '',
                                          'lookup': "find('ip').attrib['netmask']",
                                        },
                             'gateway': {'default': '',
                                          'lookup': "find('ip').attrib['gateway']",
                                        },
                             'speed': {'default': '',
                                          'lookup': "find('speed').text",
                                        },
                             'status': {'default': '',
                                          'lookup': "find('status').find('state').text",
                                        },
                            },
                      'vms':
                            {'command': 'vms',
                             'relname': 'vms',
                             'modname': 'ZenPacks.zenoss.oVirt.Vm',
                             'attributes': ['guid', 'name', 'cluster_guid',
                             'vm_type', 'state', 'memory', 'cpu_cores', 'cpu_sockets',
                             'os_type', 'os_boot', 'creation_time', 'setHostId',
                             'affinity', 'memory_policy_guaranteed'],  # This needs to have the guid first because its the id we are using else where
                                                                       # Took start_time out because it wasnt consistent from the api and it was causing
                                                                       # the modeller to update objects on every run.
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
                                          'delete': True,
                                        },
                             'setHostId': {'default': '',
                                          'lookup': "find('host').attrib['id']",
                                        },
                             'vm_type': {'default': '',
                                          'lookup': "find('type').text",
                                        },
                              'state': {'default': '',
                                          'lookup': "find('status').find('state').text",
                                        },
                              'memory': {'default': '',
                                          'lookup': "find('memory').text",
                                        },
                              'cpu_cores': {'default': '',
                                          'lookup': "find('cpu').find('topology').attrib['cores']",
                                        },
                              'cpu_sockets': {'default': '',
                                          'lookup': "find('cpu').find('topology').attrib['sockets']",
                                        },
                              'os_type': {'default': '',
                                          'lookup': "find('os').attrib['type']",
                                        },
                              'os_boot': {'default': '',
                                          'lookup': "find('os').find('boot').attrib['dev']",
                                        },
                              'start_time': {'default': '',
                                          'lookup': "find('start_time').text",
                                        },
                              'creation_time': {'default': '',
                                          'lookup': "find('creation_time').text",
                                        },
                              'affinity': {'default': '',
                                          'lookup': "find('placement_policy').find('affinity').text",
                                        },
                              'memory_policy_guaranteed': {'default': '',
                                          'lookup': "find('memory_policy').find('guaranteed').text",
                                        },
                            },
                      'nics':
                            {'relname': 'nics',
                             'modname': 'ZenPacks.zenoss.oVirt.VmNic',
                             'attributes': ['guid', 'name', 'vm_guid',
                             'mac', 'interface'],  # This needs to have the guid first because its the id we are using else where
                             'compname': '"datacenters/%s/clusters/%s/vms/%s" % self.vmnic_compname(data,id)',
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
                             'vm_guid': {'default': '',
                                          'lookup': "find('vm').attrib['id']",
                                          'delete': True,
                                        },
                             'mac': {'default': '',
                                          'lookup': "find('mac').attrib['address']",
                                        },
                             'interface': {'default': '',
                                          'lookup': "find('interface').text",
                                        },
                            },
                      'disks':
                            {'command': 'disks',
                             'relname': 'disks',
                             'modname': 'ZenPacks.zenoss.oVirt.VmDisk',
                             'attributes': ['guid', 'name',
                                            'vm_guid', 'storagedomain_guid',
                                            'setVmId', 'bootable', 'format',
                                            'interface', 'size', 'status'],  # This needs to have the guid first because its the id we are using else where

                             'compname': '"storagedomains/%s" % self.disk_compname(data,id)',
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
                             'setVmId': {'default': '',
                                          'lookup': "find('vm').attrib['id']",
                                        },
                             'bootable': {'default': '',
                                          'lookup': "find('bootable').text",
                                        },
                             'format': {'default': '',
                                          'lookup': "find('format').text",
                                        },
                             'interface': {'default': '',
                                          'lookup': "find('interface').text",
                                        },
                             'size': {'default': '',
                                          'lookup': "find('size').text",
                                        },
                             'status': {'default': '',
                                          'lookup': "find('status').find('state').text",
                                        },
                             'vm_guid': {'default': '',
                                          'lookup': "find('vm').attrib['id']",
                                          'delete': True,
                                        },
                             'storagedomain_guid': {'default': '',
                                          'lookup': "find('storage_domains').find('storage_domain').attrib['id']",
                                          'delete': True,
                                        },
                            },
                      'storage_domains':
                            {'command': 'storagedomains',
                             'relname': 'storagedomains',
                             'modname': 'ZenPacks.zenoss.oVirt.StorageDomain',
                             'attributes': ['guid', 'name', 'setDatacenterId',
                                            'storage_type', 'storage_format', 'storagedomain_type',
                                            'status'],  # This needs to have the guid first because its the id we are using else where
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
                             'setDatacenterId': {'default': '',
                                          'lookup': "find('data_center').attrib['id']",
                                          'array': True
                                        },
                             'storage_type': {'default': '',
                                          'lookup': "find('storage').find('type').text"
                                        },
                             'storage_format': {'default': '',
                                          'lookup': "find('storage_format').text"
                                        },
                             'storagedomain_type': {'default': '',
                                          'lookup': "find('type').text"
                                        },
                             'status': {'default': '',
                                          'lookup': "find('status').find('state').text"
                                        },
                            },
                     }

    #Helper Method
    def host_compname(self, data, host_id):
        cluster_guid = self.prepId(data["hosts"][host_id]["cluster_guid"])
        datacenter_guid = self.prepId(data["clusters"][cluster_guid]["datacenter_guid"])
        return (datacenter_guid, cluster_guid)

    #Helper Method
    def hostnic_compname(self, data, hostnic_id):
        host_guid = self.prepId(data['host_nics'][hostnic_id]["host_guid"])
        cluster_guid = self.prepId(data["hosts"][host_guid]["cluster_guid"])
        datacenter_guid = self.prepId(data["clusters"][cluster_guid]["datacenter_guid"])
        return (datacenter_guid, cluster_guid, host_guid)

    #Helper Method
    def vm_compname(self, data, vm_id):
        cluster_guid = self.prepId(data["vms"][vm_id]["cluster_guid"])
        datacenter_guid = self.prepId(data["clusters"][cluster_guid]["datacenter_guid"])
        return (datacenter_guid, cluster_guid)

    #Helper Method
    def vmnic_compname(self, data, vmnic_id):
        vm_guid = self.prepId(data['nics'][vmnic_id]["vm_guid"])
        cluster_guid = self.prepId(data["vms"][vm_guid]["cluster_guid"])
        datacenter_guid = self.prepId(data["clusters"][cluster_guid]["datacenter_guid"])
        return (datacenter_guid, cluster_guid, vm_guid)

    #Helper Method
    def disk_compname(self, data, disk_id):
        storagedomain_guid = self.prepId(data["disks"][disk_id]["storagedomain_guid"])
        #datacenter_guid = self.prepId(data["storage_domains"][storagedomain_guid]["datacenter_guid"])
        return (storagedomain_guid)

    def product_key(self, product_info):
        """Return a Zenoss product key from oVirt product_info element."""

        vendor = product_info.find('vendor')
        name = product_info.find('name')
        version = product_info.find('version')

        product_key = None
        if name is not None and name.text:
            if version is not None and version.get('major') is not None:
                product_key = '%s %s.%s.%s-%s' % (
                    name.text,
                    version.get('major'),
                    version.get('minor', 0),
                    version.get('revision', 0),
                    version.get('build', 0))
            else:
                product_key = name

        if vendor is not None and vendor.text:
            return MultiArgs(product_key, vendor.text)

        return product_key


    @inlineCallbacks
    def collect(self, device, unused):
        """Collect model-related information using the txovirt library."""

        if not device.zOVirtUrl:
            log.error('zOVirtUrl is not set. Not discovering')
            returnValue(None)

        if not device.zOVirtUser:
            log.error('zOVirtUser is not set. Not discovering')
            returnValue(None)

        if not device.zOVirtDomain:
            log.error('zOVirtDomain is not set. Not discovering')
            returnValue(None)

        if not device.zOVirtPassword:
            log.error('zOVirtPassord is not set. Not discovering')
            returnValue(None)

        client = txovirt.getClient(
             device.zOVirtUrl,
             device.zOVirtUser,
             device.zOVirtDomain,
             device.zOVirtPassword)

        deferreds = []
        data_centers = None

        # Get the /api overview.
        deferreds.append(client.request_elementtree(''))

        for key in self.collector_map_order:
            if key == 'data_centers':
                data_centers = yield client.request_elementtree(self.collector_map[key]['command'])
                for datacenter in data_centers.getchildren():
                    for link in datacenter.findall('link'):
                        if 'storage' in link.attrib['href']:
                            command = link.attrib['href'].rsplit('/api/')[1]
                            deferreds.append(client.request_elementtree(command))

            elif key == 'vms':
                vms = yield client.request_elementtree(self.collector_map[key]['command'])
                for vm in vms.getchildren():
                    for link in vm.findall('link'):
                        if 'disks' in link.attrib['href']:
                            command = link.attrib['href'].rsplit('/api/')[1]
                            deferreds.append(client.request_elementtree(command))
                        if 'nics' in link.attrib['href']:
                            command = link.attrib['href'].rsplit('/api/')[1]
                            deferreds.append(client.request_elementtree(command))

            elif key == 'hosts':
                hosts = yield client.request_elementtree(self.collector_map[key]['command'])
                for host in hosts.getchildren():
                    for link in host.findall('link'):
                        if 'nics' in link.attrib['href']:
                            command = link.attrib['href'].rsplit('/api/')[1]
                            deferreds.append(client.request_elementtree(command))
            else:
                deferreds.append(client.request_elementtree(self.collector_map[key]['command']))

        results = yield DeferredList(deferreds, consumeErrors=True)

        #  Insert data_centers result at the beginning of the list.
        results.insert(0, (True, data_centers))

        # append the vms to the list
        results.append((True, vms))

        # append the hosts to the list
        results.append((True, hosts))

        data = []
        for success, result in results:
            if not success:
                log.error("API Error: %s", result.getErrorMessage())
                # Try to reset the login connection on an error.
                client.login()
            data.append(result)

        returnValue(data)

    def process(self, device, results, unused):
        relmap = []
        data = {}
        for result in results:  # an array of Elements from the txovirt library.
            key = result.tag

            # Special processing for /api overview.
            if key == 'api':
                product_info = result.find('product_info')
                if product_info is not None:
                    relmap.append(ObjectMap(compname='os', data={
                        'setProductKey': self.product_key(product_info),
                        }))

                # Skip to next result after processing /api.
                continue

            data.setdefault(key, {})
            for entry in result.getchildren():
                # Skip any action sub elements
                if entry.tag == 'actions':
                    continue

                skey = None
                id = None
                # Rewrite the key based on the name in the configuration dictionary above, if it exists.
                for attribute in self.collector_map[key]['attributes']:
                    if 'name' in self.collector_map[key][attribute].keys():
                        skey = self.collector_map[key][attribute]['name']
                    else:
                        skey = attribute

                    # lookup the value from the results here
                    results = None
                    try:
                        # run the result through prepid if this field needs to be stored in that manner.
                        if 'prepId' in self.collector_map[key][attribute].keys():
                            results = self.prepId(eval('entry.' + self.collector_map[key][attribute]['lookup']))
                        else:
                            results = eval('entry.' + self.collector_map[key][attribute]['lookup'])
                    except Exception:
                        # The value couldnt be found, lets fall back to a default value.
                        log.debug("attribute [%s] not found, using default" % attribute)
                        # run the result through prepid if this field needs to be stored in that manner.
                        if 'prepId' in self.collector_map[key][attribute].keys():
                            results = self.prepId(self.collector_map[key][attribute]['default'])
                        else:
                            results = self.collector_map[key][attribute]['default']

                    # Store the id mapping and create the sub-dictionary.
                    if skey == 'id':
                        id = results
                        data[key].setdefault(id, {})

                    # Abort if the id isn't found first. All devices/components must have an id.
                    if not id:
                        log.error("Modeller Error: No id set for %s", key)
                        return None

                    # store the results to the data dict
                    if self.collector_map[key][attribute].get('array'):
                        if results:
                            data[key][id].setdefault(skey, []).append(results)
                    else:
                        data[key][id][skey] = results

        for key in self.data_map_order:
            try:
                log.info("[%s] %s found: %s" % (device.zOVirtUrl, key, len(data[key].keys())))
            except Exception,e:
                 data[key] = {}
            # objmaps are a dictionary if we are processing a component
            if 'compname' in self.collector_map[key].keys():
                objmaps = {}
            else:
                # use an array if we are processing a device
                objmaps = []

            # Generate the ObjectMaps for each component and group them by compname
            if 'compname' in self.collector_map[key].keys():
                temp_data = {}
                for id in set(data[key].keys()):
                    compname = eval(self.collector_map[key]['compname'])
                    objmaps.setdefault(compname, [])
                    # Delete temporary attributes used to generate the compname
                    for attribute in data[key][id].keys():
                        temp_data[attribute] = data[key][id][attribute]
                    for attribute in self.collector_map[key]['attributes']:
                        if 'delete' in self.collector_map[key][attribute].keys():
                            del(temp_data[attribute])
                    objmaps[compname].append(ObjectMap(data=temp_data))
            else:
                # Generate the Objectmaps for a Device.
                temp_data = {}
                for id in set(data[key].keys()):
                    # Delete temporary attributes used to generate the compname
                    for attribute in data[key][id].keys():
                        temp_data[attribute] = data[key][id][attribute]
                    for attribute in self.collector_map[key]['attributes']:
                        if 'delete' in self.collector_map[key][attribute].keys():
                            del(temp_data[attribute])
                    objmaps.append(ObjectMap(data=temp_data))

           # Generate the Relationship map based on each compname, this handles components.
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
                # Generate the Relationship map based on the Device.
                if len(objmaps) > 0:
                    rm = RelationshipMap(
                        relname=self.collector_map[key]['relname'],
                        modname=self.collector_map[key]['modname'],
                        objmaps=objmaps
                        )
                    relmap.append(rm)
        return relmap
