##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
log = logging.getLogger('zen.oVirtDataSourcePlugin')

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin

from ZenPacks.zenoss.oVirt.utils import add_local_lib_path, eventKey
add_local_lib_path()
import txovirt

from Products.ZenUtils.ZenTales import talesEvalStr
from Products.ZenModel.MinMaxThreshold import rpneval
from Products.ZenUtils.Utils import prepId
from cStringIO import StringIO
from lxml import etree
from twisted.internet.defer import DeferredList, inlineCallbacks, returnValue

def string_to_lines(string):
    if isinstance(string, (list, tuple)):
        return string
    elif hasattr(string, 'splitlines'):
        return string.splitlines()

    return None

def addCount(xml,ids,arg,increment=1):
    statistics = xml.xpath('//statistics')
    if not statistics:
        statistics = etree.SubElement(xml,'statistics')
    else:
        statistics = statistics[0]
 
    for id in ids:
        statistic = statistics.xpath("/statistic[@id='%s' and @name='%s']" % (id,arg))
        if not statistic:
            statistic = etree.SubElement(statistics,'statistic',id=id,name=arg)
        name = statistic.xpath('/name')
        if not name:
            name = etree.SubElement(statistic,'name')
            name.text = arg
        values = statistic.xpath('/values')
        if not values:
            values = etree.SubElement(statistic,'values')
        value = values.xpath('/value')
        if not value:
            value = etree.SubElement(values,'value')
        datum = value.xpath('/datum')
        if not datum:
            datum = etree.SubElement(value,'datum')
            datum.text = str(increment)
        else:
            datum.text = str(int(datum.text)+increment)

class oVirtDataSourcePlugin(PythonDataSourcePlugin):
    proxy_attributes = ('zOVirtUrl', 'zOVirtUser', 'zOVirtDomain', 'zOVirtPassword')
    request_map = [] 
    stats_request_map = [] 

    @classmethod
    def config_key(cls, datasource, context):
            return (
                context.device().id,
                datasource.getCycleTime(context),
                datasource.plugin_classname)


    @classmethod
    def params(cls, datasource, context):
        params = {}

        device = context.device()
        d = {}
        c = {}
        for prop in device.propertyIds():
            try:
                d[prop] = float(device.getProperty(prop))

            except Exception:
                pass

        d['id'] = device.id

        for prop in context.propertyIds():
            try:
                c[prop] = float(context.getProperty(prop))
            except Exception:
                pass
        c['id'] = context.id

        environ = {'dev': d,
                   'device': d,
                   'devname': device.id,
                   'here': c,
                   'nothing': None,
                   }
        params['context'] = environ
        if hasattr(context, 'xpath'):
            params['xpath'] = context.xpath
        elif hasattr(datasource, 'xpath'):
            params['xpath'] = datasource.xpath
        params['delay'] = datasource.delay
        return params

    @inlineCallbacks
    def collect(self, config):
        ds0 = config.datasources[0]
        client = txovirt.getClient(ds0.zOVirtUrl,
                                   ds0.zOVirtUser,
                                   ds0.zOVirtDomain,
                                   ds0.zOVirtPassword)
        request_map = []
        stats_request_map = []
        deferreds = []
        stats_deferreds = []
        for call in ['hosts','vms','storagedomains','datacenters','clusters']:
            self.request_map.append(call)
            deferreds.append(client.request(call))

        results = yield DeferredList(deferreds, consumeErrors=True)
        for success, result in results:
            if not success:
                log.error("%s", result.getErrorMessage())
                returnValue(None)

        host_tree = etree.parse(StringIO(results[0][1]))
       
        # get the nic from a host 
        deferreds = []
        host_tree = etree.parse(StringIO(results[0][1]))
        for nic in host_tree.xpath("//link[@rel='nics']"):
            call = nic.get('href').split('/api/')[1] 
            self.request_map.append(call)
            deferreds.append(client.request(call))
        nic_results = yield DeferredList(deferreds, consumeErrors=True)
        results = results + nic_results

        # host nic statistics
        for success, nic_result in nic_results:
            if success:
                nic_tree = etree.parse(StringIO(nic_result))
                for nic_statistic in nic_tree.xpath("//link[@rel='statistics']"):   
                    call = nic_statistic.get('href').split('/api/')[1] 
                    self.stats_request_map.append(call)
                    stats_deferreds.append(client.request(call))
                del(nic_tree)
            else:
                log.error("%s: %s", device.id, result.getErrorMessage())
                returnValue(None)
 
        # host statistics
        for host_statistic in host_tree.xpath("//link[@rel='statistics']"):
            call = host_statistic.get('href').split('/api/')[1] 
            self.stats_request_map.append(call)
            stats_deferreds.append(client.request(call))

        del(host_tree)
        

        vm_tree = etree.parse(StringIO(results[1][1]))
        # vm statistics
        for vm_statistic in vm_tree.xpath("//link[@rel='statistics']"):
            call = vm_statistic.get('href').split('/api/')[1] 
            self.stats_request_map.append(call)
            stats_deferreds.append(client.request(call))

        # get the nic from a vm
        deferreds = []
        for nic in vm_tree.xpath("//link[@rel='nics']"):
            call = nic.get('href').split('/api/')[1] 
            self.request_map.append(call)
            deferreds.append(client.request(call))
        vm_nic_results = yield DeferredList(deferreds, consumeErrors=True)
        results = results + vm_nic_results
        
        # vm nic statistics
        for success, vm_nic_result in vm_nic_results:
            if success:
                vm_nic_tree = etree.parse(StringIO(vm_nic_result))
                for vm_nic_statistic in vm_nic_tree.xpath("//link[@rel='statistics']"):   
                    call = vm_nic_statistic.get('href').split('/api/')[1] 
                    self.stats_request_map.append(call)
                    stats_deferreds.append(client.request(call))
                del(vm_nic_tree)
            else:
                log.error("%s: %s", device.id, result.getErrorMessage())
                returnValue(None)
        
        # get the disk from a vm
        deferreds = []
        for disk in vm_tree.xpath("//link[@rel='disks']"):
            call = disk.get('href').split('/api/')[1] 
            self.request_map.append(call)
            deferreds.append(client.request(call))
        vm_disk_results = yield DeferredList(deferreds, consumeErrors=True)
        results = results + vm_disk_results
        
        # vm disk statistics
        for success, vm_disk_result in vm_disk_results:
            if success:
                vm_disk_tree = etree.parse(StringIO(vm_disk_result))
                for vm_disk_statistic in vm_disk_tree.xpath("//link[@rel='statistics']"):   
                    call = vm_disk_statistic.get('href').split('/api/')[1] 
                    self.stats_request_map.append(call)
                    stats_deferreds.append(client.request(call))
                del(vm_disk_tree)
            else:
                log.error("%s: %s", device.id, result.getErrorMessage())
                returnValue(None)

        del(vm_tree)
        stats_results = yield DeferredList(stats_deferreds, consumeErrors=True)
      
        results = [r[1] for r in results] 
        stats_results = [r[1] for r in stats_results] 
        returnValue([results,stats_results])

    def onSuccess(self, results, config):
        data = self.new_data()
        root = etree.Element('root')

        # Find and save the cluster tree
        for result in results[0]:
            tree = etree.parse(StringIO(result))
            root.append(tree.getroot())
            if tree.getroot().tag == 'clusters':
                cluster_tree = tree

        for result in results[0]:
            result_tree = etree.parse(StringIO(result))
            if result_tree.getroot().tag == 'storage_domains':
                count = len(result_tree.getroot().getchildren())
                addCount(root,[config.id],'storagedomainCount',count)
            elif result_tree.getroot().tag == 'clusters':
                count = len(result_tree.getroot().getchildren())
                addCount(root,[config.id],'clusterCount',count)
                data_centers = result_tree.xpath('//data_center/@id')
                addCount(root,data_centers,'clusterCount')
            elif result_tree.getroot().tag == 'data_centers':
                count = len(result_tree.getroot().getchildren())
                addCount(root,[config.id],'datacenterCount',count)
            elif result_tree.getroot().tag == 'hosts':
                count = len(result_tree.getroot().getchildren())
                addCount(root,[config.id],'hostCount',count)
                clusters = result_tree.xpath('//cluster/@id')
                addCount(root,clusters,'hostCount')
               
                for cluster in clusters:
                     datacenter = cluster_tree.xpath('//cluster[@id="%s"]/data_center/@id' % cluster)
                     addCount(root,datacenter,'hostCount',1)
                    
            elif result_tree.getroot().tag == 'vms':
                count = len(result_tree.getroot().getchildren())
                addCount(root,[config.id],'vmCount',count)
                clusters = result_tree.xpath('//cluster/@id')
                addCount(root,clusters,'vmCount')

                hosts = result_tree.xpath('//host/@id')
                addCount(root,hosts,'vmCount')
                
                for cluster in clusters:
                     datacenter = cluster_tree.xpath('//cluster[@id="%s"]/data_center/@id' % cluster)
                     addCount(root,datacenter,'vmCount',1)
  
        for result_stat in results[1]:
            root.append(etree.parse(StringIO(result_stat)).getroot())
            # This is the general format ...
            #root.xpath('//*[*/@id="368bf44e-7d29-483a-8c2e-9a79962b1e48"][name/text()="disk.read.latency"]/values/value/datum/text()')[0]

        for ds in config.datasources:
            if ds.component:
                component_id = prepId(ds.component)
            else:
                component_id = None

            for point in ds.points:
                # Handle percentage custom datapoints
                if "ovirt:" in point.xpath and point.rpn:
                    resultsDict = {}
                    try:
                        statdata = [(x.xpath('name/text()'),x.xpath('values/value/datum/text()')) for x in root.xpath(xpath) if x.tag == 'statistic']
                        for item,val in statdata:
                            resultsDict[item[0]] = val[0]
                        rpnstring = talesEvalStr(point.rpn,context=None, extra={'here':resultsDict})
                        results = rpneval(rpnstring.split(',',1)[0],rpnstring.split(',',1)[1])
                        data['values'][component_id][point.id] = (results, 'N')
                    except Exception:
                       pass

                # Do the rest using xpath
                elif 'xpath' in ds.params:
                    try:
                        # Some points may not exist in the xml, skip those...
                        xpath=talesEvalStr(ds.params['xpath'], context=None, extra=ds.params['context'])

                        results = root.xpath(xpath+point.xpath)
                        if 'Count' in point.xpath and not results:
                            results = ['0']
                        results = results[0]
                      
                        # If rpn is defined, lets calculate the new results.
                        if point.rpn:
                            results = rpneval(
                                results, talesEvalStr(point.rpn, context=None, extra=ds.params['context']))
                        data['values'][component_id][point.id] = (results, 'N')
                    except Exception:
                        pass
        data['events'].append({
            'eventClassKey': 'oVirtCollectionSuccess',
            'eventKey': eventKey(config),
            'summary': 'ovirt: successful collection',
            'eventClass': '/Status/Perf/',
            'device': config.id,
            'severity': 0,
        })
        return data

    def onError(self, results, config):
        ds0 = config.datasources[0]
        client = txovirt.getClient(ds0.zOVirtUrl,
                                   ds0.zOVirtUser,
                                   ds0.zOVirtDomain,
                                   ds0.zOVirtPassword)

        # Try to reset the login connection on an error.
        client.login()

        errmsg = "ovirt: %s" % results.getErrorMessage()
        log.error('%s %s', config.id, errmsg)
        data = self.new_data()
        data['events'].append({
            'eventClassKey': 'oVirtCollectionError',
            'eventKey': eventKey(config),
            'eventClass': '/Status/Perf/',
            'summary': errmsg,
            'device': config.id,
            'severity': 4,
        })
        return data
