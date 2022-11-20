Changelog
=========

The third digit is only for regressions.


----

0.0.2 (2016-25-03)
------------------

Changes:
^^^^^^^^

Initial Release and implementation


0.0.3 (2016-25-03)
------------------

Changes:
^^^^^^^^
* Added all_devices attribute to ParticleCloud to return a collection of all of the devices
  Used like:  all_particle_devices = my_particle_cloud.all_devices


0.0.4 (2016-25-03)
------------------

Changes:
^^^^^^^^
* removed all_devices attribute because the user can use my_particle_cloud.devices

0.0.5 (2016-31-03)
------------------

Changes:
^^^^^^^^
* documentation update

0.0.6 (2016-31-03)
------------------

Changes:
^^^^^^^^
* documentation update

0.0.7 (2016-04-20)
------------------

Changes:
^^^^^^^^
* add device_ids list to ParticleCloud constructor to allow for optional filter of only the specified device ids.

0.0.8 (2016-05-19)
------------------

Changes:
^^^^^^^^
* added checks for error message construction.

0.0.9 (2016-08-18)
------------------

Changes:
^^^^^^^^
* add proxy support.

0.1.0 (2017-12-02)
------------------

Changes:
^^^^^^^^
* updated dependencies

0.1.1 (2022-11-02)
------------------

Changes:
^^^^^^^^
* Added some python examples
* added attribute_names, attribute, variable methods to make it easier to use those with named values instead of dot notation
* make available more of the attributes returned from ParticleIO

0.1.2 (2012-10-11)
------------------

Changes:
^^^^^^^^
* expose get_device_info as public

0.1.3 (2012-11-20)
------------------

Changes:
^^^^^^^^
* added ability to unsubscribe for events. See example_python_files/event_listeners.py for example
