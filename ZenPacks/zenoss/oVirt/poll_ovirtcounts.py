#!/usr/bin/env python
import Globals
import sys
import os
import json
import md5
import time
import tempfile

from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from Products.ZenUtils.Utils import unused

unused(Globals)


class oVirtCounter(object):
    """Caching Counter that counts subcomponents"""

    def __init__(self, device):
        self._device = device
        self._values = {}
        self._events = []

    def _temp_filename(self, key):
        """Create a tenpfile for the cache based on devicename"""

        target_hash = md5.md5('ovirt+%s' % self._device).hexdigest()

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
            os.unlink(tmpfile)
            return None

        try:
            tmp = open(tmpfile, 'r')
            values = json.load(tmp)
            tmp.close()
        except ValueError:
            # Error loading the json out of the cache, lets remove the
            # cache.
            os.unlink(tmpfile)
            return None
        return values

    def _saved_values(self):
        return self._saved(key='values')

    def _print_output(self):
        print json.dumps({'events': self._events, 'values': self._values},
                        sort_keys=True, indent=4)

    def _process(self):
        results = {}
        device = self._device
        results.setdefault(device.id, {})
        results[device.id]['storagedomainCount'] = device.storagedomains._count
        results[device.id]['datacenterCount'] = device.datacenters._count
        clusters = 0
        hosts = 0
        vms = 0

        for datacenter in device.datacenters():
            results.setdefault(datacenter.id, {})
            results[datacenter.id]['clusterCount'] = datacenter.clusters._count
            clusters += datacenter.clusters._count
            for cluster in datacenter.clusters():
                results.setdefault(cluster.id, {})
                results[cluster.id]['hostCount'] = cluster.hosts._count
                results[datacenter.id]['hostCount'] = cluster.hosts._count
                hosts += cluster.hosts._count

                results[cluster.id]['vmsCount'] = cluster.vms._count
                results[datacenter.id]['vmsCount'] = cluster.vms._count
                vms += cluster.vms._count

        results[device.id]['clusterCount'] = clusters
        results[device.id]['hostCount'] = hosts
        results[device.id]['vmsCount'] = vms
        self._save(results, key='values')
        self._values.update(results)

    def run(self):
        saved_values = self._saved_values()
        if saved_values is not None:
            self._values = saved_values

            # Print the results for the parser to read.
            self._print_output()
            return
        else:
            self._process()
            self._print_output()
            return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage %s <device>" % (sys.argv[0],)
        sys.exit(1)

    dmd = ZenScriptBase(connect=True).dmd
    device = dmd.Devices.findDeviceByIdOrIp(sys.argv[1])
    ovCounter = oVirtCounter(device)

    ovCounter.run()
