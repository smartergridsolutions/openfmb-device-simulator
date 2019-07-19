Developing
==========

This guide will help you set yourself up to contribute code to this project.

Prerequisites
~~~~~~~~~~~~~

You need to have the following installed on your development machine:

* Python 3.6
* Python 3.7
* NATS 2.x

(Our tests run on both environment, so you need both installed).

Build and Run
~~~~~~~~~~~~~

It is normally good practice to setup a virtual environment and many IDEs can
help set that up for you, so that is not covered here.

Once you have Python on your path:

#. Install the requirements with pip:

   .. code-block:: shell

     pip install -r requirements.txt

#. Run NATS 2.x. The application expects to be able to communicate with NATS
   on localhost. If you don't already have NATS and you do have Docker, you
   can start NATS through docker-compose:

   .. code-block:: shell

     cd env
     docker-compose up

#. Run the application from the shell.

   .. code-block:: shell

     .\bin\run.cmd

#. Listen to messages from the simulator on NATS.

Running in a Debugger
~~~~~~~~~~~~~~~~~~~~~

These steps describe how to run the application from Visual Studio Code. You
need a running instance of NATS for the system to connect to. Other IDEs
support similar methods:

#. Create a new debug configuration to run Python module:

   .. code-block:: json

      {
            "name": "Python: OpenFMB Simulator Module",
            "type": "python",
            "request": "launch",
            "module": "openfmbsim.server"
      }

#. Run the debug configuration. That's it!

Testing
~~~~~~~

Tests (unit, linting, coverage) are normally run with tox.

The automated build enforces compliance with Python PEP 8, PEP 257, test
coverage and other best practices. Docstrings should be written in RST format.

#. If you don't have tox already installed in your environment:

  .. code-block:: shell

     pip install tox

#. Run tests at the command line from the root directory of this repository:

  .. code-block:: shell

     tox

Unit tests require pytest and pytest-asyncio. They can be run directly from
your IDE.
