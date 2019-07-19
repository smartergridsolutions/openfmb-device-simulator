OpenFMB Device Simulator
========================

OpenFMB Device Simulator is a simple simulator that publishes information using
NATS messaging about simulated devices and accepts control requests for those
devices. The intended purpose of this simulator is to enable testing with other
systems. A minimal system contains several components and this project provides
a couple of those to aid with development and testing:
::

         ┌───────────────────────────────┐
         │ System Under Development/Test │
         └───────────────────────────────┘
                 ⇑             ⇓
    ┌─────────────────────────────────────────┐
    │           NATS.io message bus           │
    └─────────────────────────────────────────┘
                 ⇑             ⇓
    ╔═════════════════════════════════════════╗
    ║            ⇑             ⇓              ║
    ║    ┌───────────────────────────────┐    ║
    ║    │    OpenFMB Device Simulator   │    ║
    ║    └───────────────────────────────┘    ║ OpenFMB Device
    ║            ⇑             ⇓              ║ Simulator Project
    ║    ┌───────────────────────────────┐    ║
    ║    │     Simple Web Interface      │    ║
    ║    └───────────────────────────────┘    ║
    ╚═════════════════════════════════════════╝

This OpenFMB Device Simulator enables you to quickly develop other systems that
subscribe to or publish messages without needing physical hardware.

How to Run
~~~~~~~~~~

In order to run OpenFMB Device Simulator, first install Python 3.7 or later
(earlier versions of Python are known to *not* work). You must also have NATS
running elsewhere which you can connect to.

Then follow the steps below:

#. Clone this repository and its submodules:

   .. code-block:: shell

       git clone --recursive https://gitlab.com/smatergridsolutions/openfmb-device-simulator.git

   If you already have cloned the repository and did not clone recursively, you
   can clone the submodules with

   .. code-block:: shell

      git submodule update --init --recursive

#. Install the dependencies with pip:

   .. code-block:: shell

      pip install -r requirements.txt

#. Run the simulator at a terminal window:

   .. code-block:: shell

      .\bin\run.cmd

What is Supported
~~~~~~~~~~~~~~~~~

The device simulator creates a single generator from the generation module that
periodically publishes `GenerationReadingProfile` information to NATS.

The project includes a simple web interface (using HTTP/2) to view information
about the simulator. This information is redundant but can help with diagnosing
issues.

.. image:: docs/web-front-end.png
   :height: 200px

The application is structured to support additional profiles and respond to
requests. However, that is not currently used.

Expected Environment
~~~~~~~~~~~~~~~~~~~~

This simulator expects NATS to run on the normal ports, 4222, 6222, and 8222.
The web server run on port 5000 and can be accessed from http://localhost:5000.

Contributing
~~~~~~~~~~~~

There are several ways in which you can participate in the project. In
particular, we are seeking help in:

* Extending the models that this simulator supports.
* Adding the ability to specify simulated devices at start-time and run-time.
* Creating a package that can be installed with pip (ask about why this is a
  bit of work) and creates the appropriate application entry point.
* Add support for additional messaging protocols.

If you are not sure, create an issue and we'll respond.

See the developing guide if you want to contribute code.
