# Contributing

This guide will help you set yourself up to contribute code to this project.

## Prerequisites

You need to have the following installed on your development machine:

* Python 3.7
* NATS 2.x

(Our tests run on both environment, so you need both installed).

## Build and Run

It is normally good practice to setup a virtual environment and many IDEs can
help set that up for you, so that is not covered here.

Once you have Python on your path:

1. Install the requirements with pip:

     ```sh
     pip install -r requirements.txt
     ```

1. Run NATS 2.x. The application expects to be able to communicate with NATS
   on localhost. If you don't already have NATS and you do have Docker, you
   can start NATS through docker:

     ```sh
     cd env/nats
     docker build -t nats .
     docker run -it nats
     ```

1. Run the application from the shell.

     ```sh
     python -m openfmbsim.server
     ```

1. Listen to messages from the simulator on NATS.

## Running in a Debugger

These steps describe how to run the application from Visual Studio Code. You
need a running instance of NATS for the system to connect to. Other IDEs
support similar methods:

1. Create a new debug configuration to run Python module:

     ```js
      {
            "name": "Python: OpenFMB Simulator Module",
            "type": "python",
            "request": "launch",
            "module": "openfmbsim.server"
      }
     ```

1. Run the debug configuration. That's it!

## Testing

Tests (unit, linting, coverage) are normally run with tox.

The automated build enforces compliance with Python PEP 8, PEP 257, test
coverage and other best practices. Docstrings should be written in RST format.

1. If you don't have tox already installed in your environment:

     ```sh
     pip install tox
     ```

1. Run tests at the command line from the root directory of this repository:

     ```sh
     tox
     ```

Unit tests require pytest and pytest-asyncio. They can be run directly from
your IDE.
