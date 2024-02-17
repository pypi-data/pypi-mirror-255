
Nereid Test Module
==================

This module is an optional tryton module which helps in testing nereid
features. This module is not required for the regular functioning of
nereid but if you are developing on nereid, you could use this module to
write tests.

History
-------

Version 7.0.0
`````````````
Updated for version 7.0.
Depends now directly on the newly phased out module nereid_base.
Also released on Pypi.org for easy and independent availablity.

Version 3.4.0.1
```````````````

The module ws brought back into nereid codebase because the changes on
both module happen at the same time and tracking the changes in different
places is not worth the effort.

TODO: Try and disable the module from being displayed in the modules list
of Tryton for regular implementations.

Version 2.8.0.2
```````````````

This module was originally a part of nereid itself and then moved out as
nereid is to be a part of tryton. This module can be added to the
test_requires list of your module if you use it in testing.

Installing
----------

See INSTALL

Note
----

This module is developed and tested over a patched Tryton server and
core modules. Maybe some of these patches are required for the module to work.

Support
-------

For more information or if you encounter any problems with this module,
please contact the programmers at

#### MBSolutions

   * Issues:   https://gitlab.com/m9s/nereid_test/issues
   * Website:  http://www.m9s.biz/
   * Email:    info@m9s.biz

If you encounter any problems with Tryton, please don't hesitate to ask
questions on the Tryton bug tracker, forum or IRC channel:

   * http://bugs.tryton.org/
   * http://www.tryton.org/forum
   * irc://irc.freenode.net/tryton

License
-------

See LICENSE

Copyright
---------

See COPYRIGHT

