==========================
ZenPacks.zenoss.oVirt
==========================


About
------
This project is a Zenoss_ extension (ZenPack) that allows for monitoring of
oVirt/RHEV.  An explanation of what oVirt is can be found at
`<http://www.ovirt.org>`_::  or `<http://www.redhat.com/products/virtualization/>`_::

> The oVirt Project is an open virtualization project for anyone who cares about
> Linux-based KVM virtualization. Providing a feature-rich server virtualization
> management system with advanced capabilities for hosts and guests, including
> high availability, live migration, storage management, system scheduler, and more.
> This ZenPack models, collects events, and collects performance information from
> an oVirt server ( http://www.ovirt.org/ ) for data centers, clusters, hosts
> and virtual machines.


Features
--------

The ZenPack adds the following items:

================================== ======================================
Feature                            Description
================================== ======================================
Device Class                       /oVirt
Event Class                        /oVirt
Data Source                        oVirt
Daemons                            zenovirtevents, zenovirtperf
================================== ======================================

Metrics
--------
Once you've successfully added a ovirt system to Zenoss you will begin to see
the following metrics available.

* Host Cpu, Memory, Network Utilization
* VM Cpu, Memory, Network, Disk Utilization and Throughput
* Counts of Hosts, VMs residing in the various Containers

Events
--------------
oVirt/Rhev has a single event stream containing both events and alerts.  The api
does not appear to map an opening event to a closing event.  For this reason
automatic closing of events is not yet supported.  Additionally it appears that
ovirt may drop events off of its queue very quickly.  We are reading events every
minute to reduce the chance of a missed event since there is no real time event
mechanism in oVirt.

Prerequisites
--------------

==================  ==================================================================
Prerequisite        Restriction
==================  ==================================================================
Product             Zenoss 3.2.1 or higher
Processes           zenmodeler, zencommand
Installed ZenPacks  ZenPacks.zenoss.oVirt
Firewall Access     See below..
==================  ==================================================================


Limitations
------------
This version of the ZenPack only supports HTTP access to the oVirt server.
This version of the Zenpack does not automatically clear events.  The ovirt api seems
appears to be limited in regards to events.
This version of the Zenpack does not automatically detect device models in real time and
this can be worked around by manually scheduling zenmodeler to run via cron
on a regular basis.

The ovirt controller node is really a linux device.  It might be desirable to set
the appropriate modeller plugins and templates to add additional linux metrics
to this organizer.  Or you could use a cname for this device and model the real device.
under a different hostname and organizer.

This zenpack was developed against ``oVirt Engine Virtualization Engine Manager
Version: 3.0.0_0001-1.6.fc16``


Usage
------

Add an oVirt Server
++++++++++++++++++++++++++++++++

#. Navigate to the ``Infrastructure`` page
#. Click on the ``Add Device`` menu item and select ``Add oVirt Infrastructure...`` option.
#. Fill in the appropriate fields in the dialog box:
    * Url : Url of the ovirt instance.  eg http://ovirt.example.com:8080
    * Authentication Domain: Domain in which the user credentials are valid.
    * Username: User name
    * Password: Password for the user
    * Collector: Name of the remote collector which this should run.
#. Click on the ``Add`` button.
#. Wait for the device to be modeled.
#. Navigate to the new device.

Add an ovirt server via zendmd.
+++++++++++++++++++++++++++++++++
#. ovirt_facade = getFacade('oVirt')
#. ovirt_facade.add_ovirt('http://ovirt.example.com','username', 'domain', 'password')
#. commit()

Add an oVirt Server via zenbatchload
+++++++++++++++++++++++++++++++++
/Devices/oVirt loader='oVirt', loader_arg_keys=['url', 'username', 'domain', 'password']
ovirt.zenosslabs.com url='http://ovirt.zenosslabs.com', username='admin', domain='internal', password='zenoss'

#. add the above two lines to a txt file
#. Run ``zenbatchload txtfile``

Remodel an oVirt Server
++++++++++++++++++++++++++++++++
#. Navigate to the device.
#. Run the ``Model Device..`` command by selecting the gear menu at the bottom.


Firewall Access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The firewall access to and from the Zenoss collector server to the monitored
devices can depend on the type of device being monitored. The following table
provides a consolidated view of all required network access.

==================  ==================  =====================================
Source              Destination         Port & Protocol
==================  ==================  =====================================
Zenoss Collector    Monitored Device    8080/tcp (HTTP)  (ovirt api port)
==================  ==================  =====================================


Installation
-------------------------------------------------------------------------------

This ZenPack has no special installation considerations.  Depending on the
version of Zenoss you're installing the ZenPack into, you will need to verify
that you have the correct package (.egg) to install.

* Zenoss 4.1 and later: The ZenPack file must end with ``-py2.7.egg``.
* Zenoss 3.0 - 4.0: The ZenPack file must end with ``-py2.6.egg``.

To install the ZenPack you must copy the ``.egg`` file to your Zenoss master
server and run the following command as the ``zenoss`` user::

    zenpack --install <filename.egg>

After installing you must restart Zenoss by running the following command as
the ``zenoss`` user on your master Zenoss server::

    zenoss restart

If you have distributed collectors you must also update them after installing
the ZenPack.


Configuration
-------------------------------------------------------------------------------

Installing the ZenPack will add the following items to your Zenoss system.

* Device Classes

  * /oVirt

* Configuration Properties

   * zOVirtPassword
   * zOVirtUrl
   * zOVirtDomain
   * zOVirtUser

* Modeler Plugins

   * zenoss.oVirt

* Monitoring Templates

   * oVirtCluster
   * oVirtDataCenter
   * oVirtHost
   * oVirtHostNic
   * oVirtStorageDomain
   * oVirtSystem
   * oVirtVm
   * oVirtVmDisk
   * oVirtVmNic

* Event Classes

   * /oVirt


** Notes
   * If the zOVirtUrl changes it would be recommended to rename the ovirt device as well.
   * The above Configuration Properties will be automatically set when adding a
     new oVirt instance.


Removal
-------------------------------------------------------------------------------

.. warning::
    **Use caution when removing this ZenPack**

    Removing this ZenPack will **permanently** remove the /Network/Cisco device
    class and all devices and configuration contained within.

To remove this ZenPack you must run the following command as the ``zenoss``
user on your master Zenoss server::

    zenpack --remove ZenPacks.zenoss.oVirt

You must then restart the master Zenoss server by running the following command
as the ``zenoss`` user::

    zenoss restart


