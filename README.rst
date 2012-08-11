=============================================================================
ZenPacks.zenoss.oVirt
=============================================================================


About
=============================================================================
This project is a Zenoss_ extension (ZenPack) that allows for monitoring of
oVirt/RHEV. An explanation of what oVirt is can be found on the `oVirt`_ and
`Red Hat Enterprise Virtualization`_ sites::

> The oVirt Project is an open virtualization project for anyone who cares
> about Linux-based KVM virtualization. Providing a feature-rich server
> virtualization management system with advanced capabilities for hosts and
> guests, including high availability, live migration, storage management,
> system scheduler, and more. This ZenPack models, collects events, and
> collects performance information from an oVirt server ( http://www.ovirt.org/
> ) for data centers, clusters, hosts and virtual machines.

.. _Zenoss: http://www.zenoss.com/
.. _oVirt: http://www.ovirt.org/
.. _Red Hat Enterprise Virtualization: http://www.redhat.com/products/virtualization/


Features
-----------------------------------------------------------------------------

Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've successfully added a ovirt system to Zenoss you will begin to see
the following metrics available.

* Host CPU, memory, network utilization
* VM CPU, memory, network, disk utilization and throughput
* Counts of hosts, VMs residing in the various containers


Events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

oVirt/Rhev has a single event stream containing both events and alerts. The API
does not appear to map an opening event to a closing event. For this reason
automatic closing of events is not yet supported.  Additionally it appears that
oVirt may drop events off of its queue very quickly. We are reading events
every minute to reduce the chance of a missed event since there is no real time
event mechanism in oVirt.

Prerequisites
-----------------------------------------------------------------------------

==================  =========================================================
Prerequisite        Restriction
==================  =========================================================
Product             Zenoss 3.2.1 or higher
Processes           zenmodeler, zencommand
Installed ZenPacks  ZenPacks.zenoss.oVirt
Firewall Access     See below..
==================  =========================================================


Firewall Access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The firewall access to and from the Zenoss collector server to the monitored
devices can depend on the type of device being monitored. The following table
provides a consolidated view of all required network access.

==================  ==================  =====================================
Source              Destination         Port & Protocol
==================  ==================  =====================================
Zenoss Collector    Monitored Device    8080/tcp (HTTP)  (oVirt API port)
==================  ==================  =====================================


Limitations
-----------------------------------------------------------------------------

This version of the ZenPack only supports HTTP access to the oVirt server. This
version of the ZenPack does not automatically clear events.  The oVirt API
seems appears to be limited in regards to events. This version of the ZenPack
does not automatically detect device models in real time and this can be worked
around by manually scheduling zenmodeler to run via cron on a regular basis.

The oVirt controller node is really a Linux device. It might be desirable to
set the appropriate modeler plugins and templates to add additional Linux
metrics to this organizer. Alternatively, you could use a CNAME for this device
and model the real device under a different hostname and organizer.

This ZenPack has been tested against the following oVirt releases.

* oVirt Engine Virtualization Engine Manager Version: 3.0.0_0001-1.6.fc16


Installation
-------------------------------------------------------------------------------

This ZenPack has no special installation considerations. Depending on the
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


.. note::

   If the zOVirtUrl changes it would be recommended to rename the ovirt device
   as well.

   The above Configuration Properties will be automatically set when adding a
   new oVirt instance.


Usage
-----------------------------------------------------------------------------

Add an oVirt Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to the `Infrastructure` page

2. Click on the `Add Device` menu item and select `Add oVirt
   Infrastructure...` option.

3. Fill in the appropriate fields in the dialog box:

   * `URL`: URL of the oVirt instance. (i.e. http://ovirt.example.com:8080)

   * `Authentication Domain`: Domain in which the user credentials are valid.

   * `Username`: User name.

   * `Password`: Password for the user.

   * `Collector`: Zenoss collector to which the device will be assigned.

4. Click on the `Add` button.

5. Wait for the device to be modeled.

6. Navigate to the new device.


Add an oVirt Server (zendmd)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Run the following snippet in `zendmd`.

   .. code:: python

      ovirt_facade = getFacade('oVirt')
      ovirt_facade.add_ovirt('http://ovirt.example.com','username', 'domain', 'password')
      commit()


Add an oVirt Server (zenbatchload)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Add an entry like the following to your zenbatchload input file.

   .. code::

      /Devices/oVirt loader='oVirt', loader_arg_keys=['url', 'username', 'domain', 'password']
      ovirt.zenosslabs.com url='http://ovirt.zenosslabs.com', username='admin', domain='internal', password='zenoss'

2. Run `zenbatchload`.

   .. code:: bash

      zenbatchload inputfile


Removal
-------------------------------------------------------------------------------

.. warning::

   **Use caution when removing this ZenPack**

   Removing this ZenPack will **permanently** remove the /oVirt device class
   and all devices and configuration contained within.

To remove this ZenPack you must run the following command as the ``zenoss``
user on your master Zenoss server::

    zenpack --remove ZenPacks.zenoss.oVirt

You must then restart the master Zenoss server by running the following command
as the ``zenoss`` user::

    zenoss restart


Change Log
-----------------------------------------------------------------------------

1.0.3 - 2012-08-06
------------------

* First fully-featured release.

* No longer dependent on Liberator ZenPack.


1.0.1 - 2012-03-21
------------------

* Initial demonstration release.
