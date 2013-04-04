#!/usr/bin/env python
import sys
import Globals
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
dmd = ZenScriptBase(connect=True).dmd

from Products.Zuul import IInfo
from Products.Zuul import getFacade

try:
    from yaml import dump
except:
    print "Yaml not found, try running easy_install PyYaml"
    sys.exit(1)

dc = '/zport/dmd/Devices/oVirt'
tf = getFacade('template')


def modulename_for_class(class_):
    '''
    Return fully qualified module name string for given class.
    '''
    return class_.__module__


def name_for_class(class_):
    '''
    Return fully qualified class name string for given class.
    '''
    return '.'.join([modulename_for_class(class_), class_.__name__])


def printProps(data, primaryKey='uid', excludes=[]):
    lcl_data = {}
    for prop in dir(data):
        if prop.startswith('_') or prop.startswith('set') or prop in excludes \
           or prop == primaryKey or prop in ['rename', 'meta_type', 'inspector_type']:
            continue
        try:
            value = getattr(data, prop)
        except AttributeError:
            continue
        try:
            value = value()
        except:
            pass
        lcl_data[prop] = value
    return lcl_data


data = {}
# Find all the templates starting at a device class
tn=tf.getTree(dc)
for child in tn.children:
    if not child.leaf:
        # Do not recurse into nested organizers
        continue

    rrdTemplate = IInfo(child._object.getObject())
    id_ = "%s|%s" % (rrdTemplate.uid.split('/rrdTemplates')[0], rrdTemplate.name)
    data[id_] = {}
    data[id_]['description'] = rrdTemplate.description
    data[id_]['targetPythonClass'] = rrdTemplate.targetPythonClass

    # Find the datasources
    data_ds = {}
    for ds in tf.getDataSources(rrdTemplate.uid):
        ds = tf.getDataSourceDetails(ds.uid)
        data_ds[ds.name] = printProps(ds, excludes=['id', 'getName', 'getDescription',
                                                    'name', 'newId','source','testable','availableParsers'])
        # Find the datapoints
        data_dp = {}
        for dp in tf.getDataSources(ds.uid):

            data_dp[dp.newId] = printProps(dp, excludes=['aliases', 'isrow', 'leaf',
                                                         'availableRRDTypes', 'getDescription', 'id',
                                                         'getName', 'name', 'newId', 'type'])
            # Find the aliases
            data_dp_alias = {}
            for alias in dp.aliases:
                data_dp_alias[alias.name] = printProps(alias, excludes=['id', 'name', 'getName', 'getDescription',
                                                                        'description'])

                # Setinfo would prefer the Nones be emptry strings here.
                if data_dp_alias[alias.name]['formula'] == None:
                    data_dp_alias[alias.name]['formula'] = ""

            data_dp[dp.newId]['aliases'] = data_dp_alias

        data_ds[ds.name]['datapoints'] = data_dp
    data[id_]["datasources"] = data_ds

    # Find the thresholds
    data_thresh = {}
    for threshold in tf.getThresholds(rrdTemplate.uid):
        data_thresh[threshold.name] = printProps(threshold, excludes=['getDescription', 
                                                                      'eventClass', 'dsnames',
                                                                      'getName', 'getDescription', 'id',
                                                                      'name', 'newId'])
    data[id_]["thresholds"] = data_thresh

    # Find the graphs
    data_graph = {}
    for graph in tf.getGraphs(rrdTemplate.uid):
        data_graph[graph.name] = printProps(graph, excludes=['getDescription', 'getName', 'id', 'name', 'newId', 
                                                             'graphPoints', 'rrdVariables', 'fakeGraphCommands'])

        # Find the graph points
        data_graph_point = {}
        for graph_point in tf.getGraphPoints(graph.uid):
            data_graph_point[graph_point.name] = printProps(graph_point, excludes=['getDescription', 'getName', 'id', 'name', 'newId', 
                                                                                   'rrdVariables'])
      
        data_graph[graph.name]["graphpoints"] = data_graph_point

    data[id_]["graphs"] = data_graph

print dump(data,width=50,indent=4)
