#!/usr/bin/env python
###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, 2012 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import os
import sys
import md5
import tempfile
import json
import time


from twisted.internet import reactor
from twisted.internet.defer import DeferredList

from utils import add_local_lib_path

add_local_lib_path()

import txovirt


def elementtree_to_dict(element):
    """Recursively convert An ElementTree to a Dictionary.
    This misses cases, but is good enough for event processing"""

    node = {}

    text = getattr(element, 'text', None)
    if text is not None:
        node['text'] = text

    node.update(element.items())  # element's attributes

    child_nodes = {}
    for child in element:  # element's children
        child_nodes.setdefault(child.tag, []).append(elementtree_to_dict(child))

    # convert all single-element lists into non-lists
    # This makes major assumptions and simplifications
    for key, value in child_nodes.items():
        if len(value) == 1:
            if 'text' in value[0].keys():
                child_nodes[key] = value[0]['text']
            else:
                child_nodes[key] = value[0]

    node.update(child_nodes.items())
    return node


class oVirtCounter(object):
    """Caching poller that gathers counts from an ovirt system"""

    def __init__(self, url, username, domain, password, ovirt_id):
        self._url = url
        self._username = username
        self._domain = domain
        self._password = password
        self._id = ovirt_id
        self._values = {}
        self._events = []
        self.client = txovirt.Client(
            self._url,
            self._username,
            self._domain,
            self._password)

    def _temp_filename(self, key):
        """Create a tempfile for the cache based on a key"""
        target_hash = md5.md5('%s+%s+%s+counts' % (self._url, self._username, self._domain)).hexdigest()

        return os.path.join(
            tempfile.gettempdir(),
            '.zenoss_ovirt_%s_%s' % (key, target_hash))

    def _save(self, data, key):
        tmpfile = self._temp_filename(key=key)
        tmp = open(tmpfile, 'w')
        json.dump(data, tmp)
        tmp.close()

    def _saved(self, key):
        tmpfile = self._temp_filename(key=key)
        if not os.path.isfile(tmpfile):
            return None

        # Make sure temporary data isn't too stale.
        if os.stat(tmpfile).st_mtime < (time.time() - 50):
            try:
                os.unlink(tmpfile)
            except Exception:
                pass
            return None

        try:
            tmp = open(tmpfile, 'r')
            values = json.load(tmp)
            tmp.close()
        except ValueError:
            try:
                # Error loading the json out of the cache, lets remove the cache.
                os.unlink(tmpfile)
                return None
            except Exception:
                return None

        return values

    def _saved_values(self):
        return self._saved(key='values')

    def _print_output(self):
        print json.dumps({'events': self._events, 'values': self._values}, sort_keys=True, indent=4)
        sys.stdout.flush()

    def _callback(self, results):
        data = {}
        for success, result in results:
            if not success:
                error = result.getErrorMessage()
                self._events.append(dict(
                    severity=4,
                    summary='oVirt count error: %s' % error,
                    eventKey='ovirt_count_failure',
                    eventClassKey='ovirt_count_error',
                    ))

                self._print_output()
                os._exit(1)

            data.setdefault(result.tag, []).append(result)

        results = {}
        results.setdefault(self._id, {})

        # Store the counts of the components by the component id as the key.
        # increment the cluster, hosts, vms etc as we find them.
        # liberal use of setdefault to set the nested datastructures properly.
        for key in data.keys():
            results[self._id]['type'] = 'system'
            if 'storage_domains' in key:
                results[self._id]['storagedomainCount'] = len(data[key][0].getchildren())
            if 'clusters' in key:
                results[self._id]['clusterCount'] = len(data[key][0].getchildren())
                for cluster in data[key][0].getchildren():
                    if cluster.find('data_center') is not None:
                        results.setdefault(cluster.find('data_center').attrib['id'], {'clusterCount': 0, 'hostCount': 0, 'vmCount': 0, 'clusterids': [], 'type': 'datacenter'})
                        results[cluster.find('data_center').attrib['id']]['clusterCount'] += 1
                        results[cluster.find('data_center').attrib['id']]['clusterids'].append(cluster.attrib['id'])

            if 'data_centers' in key:
                results[self._id]['datacenterCount'] = len(data[key][0].getchildren())
                for datacenter in data[key][0].getchildren():
                    results.setdefault(datacenter.attrib['id'], {'clusterCount': 0, 'hostCount': 0, 'vmCount': 0, 'clusterids': [], 'type': 'datacenter'})
            if 'hosts' in key:
                results[self._id]['hostCount'] = len(data[key][0].getchildren())
                for host in data[key][0].getchildren():
                    results.setdefault(host.attrib['id'], {'vmCount': 0, 'type': 'host'})
                    if host.find('cluster') is not None:
                        results.setdefault(host.find('cluster').attrib['id'], {'vmCount': 0, 'hostCount': 0,'type': 'cluster'})
                        results[host.find('cluster').attrib['id']]['hostCount'] += 1
            if 'vms' in key:
                results[self._id]['vmCount'] = len(data[key][0].getchildren())
                for vm in data[key][0].getchildren():
                    if vm.find('cluster') is not None:
                        results.setdefault(vm.find('cluster').attrib['id'], {'vmCount': 0, 'hostCount': 0,'type': 'cluster'})
                        results[vm.find('cluster').attrib['id']]['vmCount'] += 1
                    if vm.find('host') is not None:
                        results.setdefault(vm.find('host').attrib['id'], {'vmCount': 0, 'clusterCount': 0,'type': 'host'})
                        results[vm.find('host').attrib['id']]['vmCount'] += 1

        # post process the resulting dictionary to copy the cluster counts inside a datacenter.
        # remove the temporary clusterids key.
        for key in results:
            if 'clusterids' in results[key].keys():
                for clusterid in results[key]['clusterids']:
                    for clusterkeys in results[clusterid].keys():
                        if clusterkeys == 'type': continue
                        results[key][clusterkeys] += results[clusterid][clusterkeys]
                del results[key]['clusterids']

        self._values.update(results)

        if len(self._values.keys()) > 0:
            self._save(self._values, key='values')

        self._events.append(dict(
            severity=0,
            summary='oVirt counted successfully',
            eventKey='ovirt_count_failure',
            eventClassKey='ovirt_count_success',
            ))

        self._print_output()

        # We are not needing any more data, stop the reactor.
        if reactor.running:
            reactor.stop()

    def run(self):
        deferreds = []

        # Try the cache if its available
        saved_values = self._saved_values()
        if saved_values is not None:
            self._values = saved_values
            # Send success that we read from the cache.
            self._events.append(dict(
                severity=0,
                summary='oVirt polled successfully',
                eventKey='ovirt_failure',
                eventClassKey='ovirt_success',
                ))

            #Print the results for the parser to read.
            self._print_output()
            return

        deferreds.extend((
            self.client.request('hosts'),
            self.client.request('vms'),
            self.client.request('storagedomains'),
            self.client.request('datacenters'),
            self.client.request('clusters'),
            ))

        # Now start processing our tasks with the results going to the self._callback method.
        DeferredList(deferreds, consumeErrors=True).addCallback(self._callback)

        reactor.run()
        #Nothing will run after this line, unless the reactor is stopped.

if __name__ == '__main__':
    usage = "Usage: %s <url> <username> <domain> <password> <id>"
    url = username = domain = password = ovirt_id = None

    try:
        url, username, domain, password, ovirt_id = sys.argv[1:6]
    except ValueError:
        print >> sys.stderr, usage % sys.argv[0]
        sys.exit(1)

    #time.sleep(random.randint(1, 5))
    counter = oVirtCounter(url, username, domain, password, ovirt_id)
    counter.run()
