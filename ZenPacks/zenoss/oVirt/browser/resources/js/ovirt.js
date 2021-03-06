/*
  ###########################################################################
  # Copyright (C) 2012, Zenoss Inc.
  ###########################################################################
*/

(function () {

var NS = Ext.namespace('Zenoss.zenpacks.oVirt');


// addoVirtInfra is the action (w/popup dialog) to add to the adddevice
// button on Infrastructure->Devices
var addOVirtInfra = new Zenoss.Action({
    text: _t('Add oVirt Infrastructure') + '...',
    id: 'addovirt-item',
    permissionContext: '/zport/dmd/Devices/oVirt',
    permission: 'Manage DMD',
    handler: function(btn, e){
        var win = new Zenoss.dialog.CloseDialog({
            width: 300,
            title: _t('Add oVirt Infrastructure'),
            items: [{
                xtype: 'form',
                buttonAlign: 'left',
                monitorValid: true,
                labelAlign: 'top',
                footerStyle: 'padding-left: 0',
                border: false,
                items: [{
                    xtype: 'textfield',
                    name: 'url',
                    fieldLabel: _t('URL'),
                    id: "ovirtURLField",
                    width: 260,
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    name: 'domain',
                    width: 260,
                    value: 'internal',
                    fieldLabel: _t('Authentication Domain'),
                    id: 'add-ovirt-domain',
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    name: 'username',
                    width: 260,
                    fieldLabel: _t('Username'),
                    id: "add-ovirt-username",
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    name: 'password',
                    width: 260,
                    inputType: 'password',
                    fieldLabel: _t('Password'),
                    id: "add-ovirt-password",
                    allowBlank: false
                }, {
                    xtype: 'combo',
                    width: 260,
                    name: 'collector',
                    fieldLabel: _t('Collector'),
                    id: 'add-ovirt-collector',
                    mode: 'local',
                    store: new Ext.data.ArrayStore({
                        data: Zenoss.env.COLLECTORS,
                        fields: ['name']
                    }),
                    valueField: 'name',
                    displayField: 'name',
                    forceSelection: true,
                    editable: false,
                    allowBlank: false,
                    triggerAction: 'all',
                    selectOnFocus: false,
                    listeners: {
                        'afterrender': function(component) {
                            var index = component.store.find('name', 'localhost');
                            if (index >= 0) {
                                component.setValue('localhost');
                            }
                        }
                    }
                }],
                buttons: [{
                    xtype: 'DialogButton',
                    id: 'addsingledevice-submit',
                    text: _t('Add'),
                    formBind: true,
                    handler: function(b) {
                        var form = b.ownerCt.ownerCt.getForm();
                        var opts = form.getFieldValues();

                        Zenoss.remote.oVirtRouter.add_ovirt(opts,
                        function(response) {
                            if (response.success) {
                                if (Zenoss.JobsWidget) {
                                    Zenoss.message.success(_t('Add oVirt Infrastructure job submitted.'));
                                } else {
                                    Zenoss.message.success(
                                        _t('Add oVirt Infrastructure job submitted. <a href="/zport/dmd/JobManager/jobs/{0}/viewlog">View Job Log</a>'),
                                        response.jobId);
                                }
                            }
                            else {
                                Zenoss.message.error(_t('Error adding oVirt Infrastructure: {0}'),
                                    response.msg);
                            }
                        });
                    }
                }, Zenoss.dialog.CANCEL]
            }]
        });
        win.show();
    }
});

// push the addOVirtInfra action to the adddevice button
Ext.ns('Zenoss.extensions');
Zenoss.extensions.adddevice = Zenoss.extensions.adddevice instanceof Array ?
                              Zenoss.extensions.adddevice : [];
Zenoss.extensions.adddevice.push(addOVirtInfra);


}());
