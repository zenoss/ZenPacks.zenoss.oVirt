(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('oVirtVmDisk', _t('Disk'), _t('Disks'));
ZC.registerName('oVirtHost', _t('Host'), _t('Hosts'));
ZC.registerName('oVirtCluster', _t('Cluster'), _t('Clusters'));
ZC.registerName('oVirtStorageDomain', _t('Storage Domain'), _t('Storage Domains'));
ZC.registerName('oVirtVms', _t('Virtual Machine'), _t('Virtual Machines'));
ZC.registerName('oVirtDataCenter', _t('Datacenter'), _t('Datacenters'));

Zenoss.types.TYPES.DeviceClass[0] = new RegExp(
    "^/zport/dmd/Devices(/(?!devices)[^/*])*/?$");

Zenoss.types.register({
     'oVirtVmDisk': "^/zport/dmd/Devices/.*/devices/.*/storagedomains/.*/disks/[^/]*/?$",
     'oVirtHost': "^/zport/dmd/Devices/.*/devices/.*/datacenters/.*/clusters/.*/hosts/[^/]*/?$",
     'oVirtCluster': "^/zport/dmd/Devices/.*/devices/.*/datacenters/.*/clusters/[^/]*/?$",
     'oVirtStorageDomain': "^/zport/dmd/Devices/.*/devices/.*/storagedomains/[^/]*/?$",
     'oVirtVms': "^/zport/dmd/Devices/.*/devices/.*/datacenters/.*/clusters/.*/vms/[^/]*/?$",
     'oVirtDataCenter': "^/zport/dmd/Devices/.*/devices/.*/datacenters/[^/]*/?$"
});

Ext.apply(Zenoss.render, {
    oVirt_entityLinkFromGrid: function(obj) {
        if (obj && obj.uid && obj.title && obj.meta_type) {
            if (!this.subComponentGridPanel && this.componentType == obj.meta_type) {
                return obj.title;
            } else {
                return '<a href="javascript:Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\''+obj.uid+'\', \''+obj.meta_type+'\');">'+obj.title+'</a>';
            }
        }
    },

    checkbox: function(bool) {
        if (bool) {
            return '<input type="checkbox" checked="true" disabled="true">';
        } else {
            return '<input type="checkbox" disabled="true">';
        }
    }
});

ZC.oVirtComponentGridPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    jumpToEntity: function(uid, meta_type) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel;
        var tree_selection_model = tree.getSelectionModel();
        var components_node = tree.getRootNode().findChildBy(
            function(n) {
                return n.text == 'Components' || n.data.text == 'Components';
            });

        // Reset context of component card.
        var component_card = Ext.getCmp('component_card');
        component_card.setContext(
            components_node.data ? components_node.data.id : components_node.id,
            meta_type);

        // Select chosen row in component grid.
        component_card.selectByToken(uid);

        // Select chosen component type from tree.
        var component_type_node = components_node.findChildBy(
            function(n) {
                return n.id == meta_type || n.data.id == meta_type;
            });

        if (component_type_node.select) {
            tree_selection_model.suspendEvents();
            component_type_node.select();
            tree_selection_model.resumeEvents();
        } else {
            tree_selection_model.select([component_type_node], false, true);
        }
    }
});


ZC.oVirtDataCenterPanel = Ext.extend(ZC.oVirtComponentGridPanel, {

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'description',
            componentType: 'oVirtDataCenter',
            fields: [
                {name: 'meta_type'},
                {name: 'uid'},
                {name: 'title'},
                {name: 'entity'},
                {name: 'severity'},
                {name: 'description'},
                {name: 'storagedomain_count'},
                {name: 'cluster_count'},
                {name: 'storage_type'},
                {name: 'storage_format'},
                {name: 'status'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            sortInfo: {
                field: 'entity',
                direction: 'ASC'
            },
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Name'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                width: 100
            },{
                id: 'description',
                dataIndex: 'description',
                header: _t('Description'),
                sortable: true
            },{
                id: 'storage_type',
                dataIndex: 'storage_type',
                header: _t('Storage Type'),
                sortable: true,
                width: 80
            },{
                id: 'storage_format',
                dataIndex: 'storage_format',
                header: _t('Storage Format'),
                sortable: true,
                width: 90
            },{
                id: 'storagedomain_count',
                dataIndex: 'storagedomain_count',
                header: _t('# StorageDomains'),
                sortable: true,
                width: 100
            },{
                id: 'cluster_count',
                dataIndex: 'cluster_count',
                header: _t('# Clusters'),
                sortable: true,
                width: 70
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.oVirtDataCenterPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('oVirtDataCenterPanel', ZC.oVirtDataCenterPanel);

ZC.oVirtClusterPanel = Ext.extend(ZC.oVirtComponentGridPanel, {

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'oVirtCluster',
            fields: [
                {name: 'meta_type'},
                {name: 'uid'},
                {name: 'title'},
                {name: 'severity'},
                {name: 'datacenter'},
                {name: 'entity'},
                {name: 'status'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            sortInfo: {
                field: 'entity',
                direction: 'ASC'
            },
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Cluster'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                width: 70
            },{
                id: 'datacenter',
                dataIndex: 'datacenter',
                header: _t('Datacenter'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                sortable: true,
                width: 100
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.oVirtClusterPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('oVirtClusterPanel', ZC.oVirtClusterPanel);

ZC.oVirtStorageDomainPanel = Ext.extend(ZC.oVirtComponentGridPanel, {

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'oVirtStorageDomain',
            fields: [
                {name: 'meta_type'},
                {name: 'uid'},
                {name: 'title'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'datacenter'},
                {name: 'status'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            sortInfo: {
                field: 'entity',
                direction: 'ASC'
            },
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Storage Domain'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                width: 70
            },{
                id: 'datacenter',
                dataIndex: 'datacenter',
                header: _t('Datacenter'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                width: 70
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.oVirtStorageDomainPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('oVirtStorageDomainPanel', ZC.oVirtStorageDomainPanel);

ZC.oVirtVmsPanel = Ext.extend(ZC.oVirtComponentGridPanel, {

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'oVirtVms',
            fields: [
                {name: 'meta_type'},
                {name: 'uid'},
                {name: 'title'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'cluster'},
                {name: 'status'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            sortInfo: {
                field: 'entity',
                direction: 'ASC'
            },
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Virtual Machine'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                width: 70
            },{
                id: 'cluster',
                dataIndex: 'cluster',
                header: _t('Cluster'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                sortable: true,
                width: 100
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.oVirtVmsPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('oVirtVmsPanel', ZC.oVirtVmsPanel);

ZC.oVirtHostPanel = Ext.extend(ZC.oVirtComponentGridPanel, {

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'oVirtHost',
            fields: [
                {name: 'meta_type'},
                {name: 'uid'},
                {name: 'title'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'cluster'},
                {name: 'status'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            sortInfo: {
                field: 'entity',
                direction: 'ASC'
            },
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Host'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                width: 70
            },{
                id: 'cluster',
                dataIndex: 'cluster',
                header: _t('Cluster'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                sortable: true,
                width: 100
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.oVirtHostPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('oVirtHostPanel', ZC.oVirtHostPanel);

ZC.oVirtVmDiskPanel = Ext.extend(ZC.oVirtComponentGridPanel, {

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'entity',
            componentType: 'oVirtVmDisk',
            fields: [
                {name: 'meta_type'},
                {name: 'uid'},
                {name: 'title'},
                {name: 'severity'},
                {name: 'entity'},
                {name: 'vm'},
                {name: 'storagedomain'},
                {name: 'status'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'size'},
                {name: 'interface'},
                {name: 'format'},
                {name: 'locking'}
            ],
            sortInfo: {
                field: 'entity',
                direction: 'ASC'
            },
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'entity',
                dataIndex: 'entity',
                header: _t('Disk'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                sortable: true,
                width: 70
            },{
                id: 'status',
                dataIndex: 'status',
                header: _t('Status'),
                sortable: true,
                width: 45
            },{
                id: 'size',
                dataIndex: 'size',
                header: _t('Size'),
                renderer: Zenoss.render.memory,
                sortable: true,
                width: 70
            },{
                id: 'vm',
                dataIndex: 'vm',
                header: _t('Virtual Machine'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                sortable: true,
                width: 100
            },{
                id: 'storagedomain',
                dataIndex: 'storagedomain',
                header: _t('Storage Domain'),
                renderer: Zenoss.render.oVirt_entityLinkFromGrid,
                sortable: true,
                width: 100
            },{
                id: 'interface',
                dataIndex: 'interface',
                header: _t('Interface'),
                sortable: true,
                width: 75
            },{
                id: 'format',
                dataIndex: 'format',
                header: _t('Format'),
                sortable: true,
                width: 60
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.oVirtVmDiskPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('oVirtVmDiskPanel', ZC.oVirtVmDiskPanel);

//Add cluster dropdown to the DataCenter Component.
Zenoss.nav.appendTo('Component', [{
    id: 'component_clusters',
    text: _t('Related Clusters'),
    xtype: 'oVirtClusterPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'oVirtDataCenter') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.oVirtClusterPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

//Add Storage Domain dropdown to the DataCenter Component.
Zenoss.nav.appendTo('Component', [{
    id: 'component_storagedomain',
    text: _t('Related StorageDomains'),
    xtype: 'oVirtStorageDomainPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'oVirtDataCenter') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.oVirtStorageDomainPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

//Add host dropdown to the cluster component
Zenoss.nav.appendTo('Component', [{
    id: 'component_hosts',
    text: _t('Related Hosts'),
    xtype: 'oVirtHostPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'oVirtCluster') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.oVirtHostPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

//Add vms dropdown to the cluster component
Zenoss.nav.appendTo('Component', [{
    id: 'component_vms',
    text: _t('Related Vms'),
    xtype: 'oVirtVmsPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'oVirtCluster') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.oVirtVmsPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

//Add disks dropdown to the storage domain or vms component
Zenoss.nav.appendTo('Component', [{
    id: 'component_disks',
    text: _t('Related Disks'),
    xtype: 'oVirtVmDiskPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        if (navpanel.refOwner.componentType == 'oVirtStorageDomain') {
            return true;
        }
        else if (navpanel.refOwner.componentType == 'oVirtVms') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.oVirtVmDiskPanel.superclass.setContext.apply(this, [uid]);
    }
}]);


})();