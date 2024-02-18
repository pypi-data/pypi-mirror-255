=====
Heist
=====

Heist creates network tunnels for distributing and managing agents. While it has
been originally built to deploy and manage Salt Minions, it can be used to
distribute and manage other agents or plugins if extended to do so.

Using Heist is very easy, Start by downloading Heist. Just install via
`pip`:

.. code-block:: bash

        pip install heist


Heist Manager
=============

In order to run Heist you will need to specify a Heist manager. An example of a
heist manager is `salt.minion` but this will require a user to install the
`heist-salt <https://heist-salt.readthedocs.io/en/latest/>`_ project:

.. code-block:: bash

        pip install heist-salt


Making Your Roster
==================

A Roster is a file used by Heist to map login information to the
systems in your environment. This file can be very simple and just
needs to tell Heist where your systems are and how to log into them
via ssh. Open a file called `roster.cfg` and add the data needed to connect
to a remote system via ssh:

.. code-block:: yaml

    system_name:
      host: 192.168.4.4
      username: fred
      password: freds_password

.. note::

    This example is very simple, heist supports virtually all available authentication
    options for ssh.


The roster files typically all live inside of a roster directory. But to get
started we will execute a single roster file with Heist using the `salt.minion` Heist
manager:

.. code-block:: bash

    heist salt.minion -R roster.cfg

Assuming your roster is correct, heist will now connect to the remote
system and deploy the `salt.minion` binary.


Tear Down
=========

Heist is able to automatically clean up as well! Just soft kill
your heist application and it will reach out to all connections, tell them to
remove the deployed artifacts from the target systems and stop the service!
Like a proper heist these should be no evidence left behind!


Using Heist to Deploy Salt Minions
==================================
If you want to use Heist to deploy and manage Salt, you will need to install
`heist-salt <https://heist-salt.readthedocs.io/en/latest/>`_.


Additional Documentation
========================
If you want to read more about how to use Heist and its internals please
take a look at Heist's documentation here: https://heist.readthedocs.io/en/latest/
