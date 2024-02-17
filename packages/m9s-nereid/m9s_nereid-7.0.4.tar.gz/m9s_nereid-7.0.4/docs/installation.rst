.. _installation:

Installation
============

Nereid depends on a handful of Python libraries including Tryton.

So how do you get all that on your system quickly?  There are many ways you
could do that, but the most advanced method is `virtualenv`_. The `Flask
Documentation`_ has a detailed `section on using virtualenv`_ to install
Flask. You could refer to the same and then follow the instructions below.

.. _virtualenv:

virtualenv
----------

`virtualenvs`_ are isolated Python environments.

If you are on Mac OS X or Linux, chances are that one of the following two
commands will work for you in creating a virtualenv:

.. code-block:: sh

    $ sudo easy_install virtualenv

or even better

.. code-block:: sh

    $ sudo pip install virtualenv

One of these will probably install virtualenv on your system.

**The preferred way is to use
your package manager. On Debian or Ubuntu systems use**

.. code-block:: sh

    $ sudo apt-get install virtualenv

A very comfortable extension for managing multiple environments is virtualenvwrapper.

.. code-block:: sh

    $ sudo apt-get install virtualenvwrapper

.. note::
    While developing and running on Windows is not recommended there are some
    detailed instructions for Windows in :ref:`installation_windows`.

Once you have virtualenvwrapper installed, it is able to manage separate directories
for your project files and the virtualenv libraries thus keeping your project directory clean.

Just add the following line to your ~/.bashrc

.. code-block:: sh

    export PROJECT_HOME=<your_project_home>

and you are ready to fire up a shell and create your own environment. 

With virtualenvwrapper creating a new a project is as simple as 

.. code-block:: sh

    $ mkproject myproject

Now, whenever you want to work on a project, you only have to activate the
corresponding environment.  On OS X and Linux, do the following:

.. code-block:: sh

    $ workon myproject

Either way, you should now be using your virtualenv (notice how the prompt of
your shell has changed to show the active environment).

Now you can just enter the following command to get Nereid activated in your
virtualenv:


.. code-block:: sh

    $ pip install m9s-nereid

A few seconds, and you are good to go.


System-Wide Installation
------------------------

This is possible as well, though usually not recommended. Could be a way to go in
isolated containers. You have been warned! Just run `pip` with root privileges

.. code-block:: sh

    $ sudo pip install m9s-nereid


Living on the Edge
------------------

If you want to work with the latest version of Nereid, you can tell
it to operate on a git checkout.  Either way, virtualenv is strongly recommended.

Get the git checkout in a new virtualenv and run in development mode

.. code-block:: sh

    $ git clone https://gitlab.com/m9s/nereid
    $ pip install -e nereid

This will pull in the dependencies and activate the git head as the current
version inside the virtualenv.  Then all you have to do is run ``git pull
origin`` to update to the latest version.


.. _cloning_for_dev:

Cloning for Development
-----------------------

If you are cloning the repository for development or updating the
documentation, you also need to initialise the git submodules for the
theme used in the documentation.

.. code-block:: sh
    :emphasize-lines: 3,4 

    $ git clone https://gitlab.com/m9s/nereid
    $ cd nereid
    $ git submodule init
    $ git submodule update


.. _virtualenvs: https://virtualenv.pypa.io
.. _section on using virtualenv: https://flask.palletsprojects.com/installation/#virtual-environments
.. _Flask Documentation: https://flask.palletsprojects.com/
 
