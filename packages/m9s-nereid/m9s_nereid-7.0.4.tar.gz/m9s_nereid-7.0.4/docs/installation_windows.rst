.. _installation_windows:

Some tips for installation on Windows
=====================================

.. _virtualenv:

virtualenv
----------

If you are on Windows and don't have the `easy_install` command, you must
install it first.  Check :ref:`windows-easy-install` section for more
information about how to do that.  Once you have it installed, run the same
commands as in :ref:`installation`.

If you are a Windows user, the following command is for you:

.. code-block:: sh

    $ venv\scripts\activate

Either way, you should now be using your virtualenv (notice how the prompt of
your shell has changed to show the active environment).

Now you can just enter the following command to get Nereid installed in your
virtualenv:

.. code-block:: sh

    $ pip install m9s-nereid

A few seconds, and you are good to go.


System-Wide Installation
------------------------

This is possible as well, though usually not recommended. Could be a way to go in
isolated containers. You have been warned! Just run `pip` with root privileges

On Windows systems, run it in a command-prompt window with administrator
privileges.

.. code-block:: sh

    $ pip install m9s-nereid


.. _windows-easy-install:

`pip` and `distribute` on Windows
-----------------------------------

On Windows, installation of `easy_install` is a bit tricky, but still
achievable.  Read the section on `pip and distribute on Windows`_ on the
Flask documentation for a better understanding.



.. _pip and distribute on Windows: https://flask.palletsprojects.com/installation/#pip-and-distribute-on-windows
.. _virtualenvs: https://virtualenv.pypa.io
.. _section on using virtualenv: https://flask.palletsprojects.com/installation/#virtual-environments
.. _Flask Documentation: https://flask.palletsprojects.com/
