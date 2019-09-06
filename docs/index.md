# OpenFMB Device Simulator

The OpenFMB Device Simulator helps with developing components that depend on
OpenFMB messages. The simulator periodically publishes messages to OpenFMB
defined topics using NATS messaging. The primary uses cases are:

* you don't have hardware that supports OpenFMB messages;
* you want to test in an isolated environment;
* you want to test against a reliable message source.

The simulator is organized based on a *virtual device* that periodically
publishes data according to it's internal state. We currently support a
virtualized single-phase battery, but plan to add more and encourage
contributions. The simulator environment includes a simple web interface for
adding devices into the system.

A typical use case is shown below:

```
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
```

## Install and Run OpenFMB Device Simulator

The simplest way to get started with OpenFMB Device Simulator is using
[Docker](https://www.docker.com/) containers.

### Requirements

You can setup a complete system with two commands in a terminal window
provided that you satisfy the following requirements on your local machine:

* `git`
* `docker`
* `docker compose`
* A web browser that supports HTTP/2 server-send events. See
  [Event Source on MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#EventSource)
  for information on browser support.

This includes both the simulator and an instance of NATS that it publishes to.

### Clone the Repository

Run the following in a terminal to clone the repository and its submodules:

```sh
git clone --recursive https://gitlab.com/smatergridsolutions/openfmb-device-simulator.git
```

If you already have cloned the repository and did not clone recursively, you can
clone the submodules with:

```sh
git submodule update --init --recursive
```

### Build and Start

#### Build and Start Only the Simulator

Execute the following in a terminal if you already have NATS running and want
to connect to the running instance:

```sh
# Build the simulator in a container
docker build -t openfmb-device-simulator .
# Run the container (substitute the IP address of the server you want to connect to)
docker run -it -p 5000:5000 openfmb-device-simulator "--servers" "nats://127.0.0.1:4222" "--verbose"
```

💡 *TIP* Execute the following in a terminal to see the full set of supported
command line arguments:

```sh
docker run -it openfmb-device-simulator "--help"
```

#### Build and Start the Simulator and NATS

Execute the following in a terminal if you do not have an instance of NATS
running.

```sh
# Build the simulator and NATS into two containers
docker-compose build
# Run the built containers
docker-compose up
```

### Interact

Once the simulator is running following the steps above, it will automatically
being to publish messages to NATS using the default generator reading profile.

You can use a 3rd party tool such at
[nats-top](https://github.com/nats-io/nats-top) to observe message delivery
statistics.

### Control

The simulator includes a simple web interface for creating and deleting
simulated models at runtime. You can also interact with the simulator via the
included web interface by opening `localhost:5000` on your local machine.

![](web-front-end.png)

💡 *TIP* The included web server is not intended to replace OpenFMB messaging.
Rather, it enables capabilities to add or remove devices that are not messages
defined by the OpenFMB standard. However, it also includes basic visualization
for the defined devices.

## Creating or Deleting Devices

The simulator creates a default simulated generator on startup. Devices
can be added or deleted after startup using the web interface.

Follow the steps below to create a new device:

1. Open the web interface
1. Choose the type of device you want to create
1. Select to create the device

A default device of the selected type is created. Messages will shortly appear
on the front end and NATS messaging service.

Follow the steps below to delete an existing device:

1. Select the device to delete and click delete

## Supported Messages

The simulator can model devices with the following profiles:

* BreakerReadingProfile
* BreakerStatusProfile
* GenerationReadingProfile
* MeterReadingProfile
* RecloserControlProfile
* RecloserReadingProfile
* RecloserStatusProfile
* SolarReadingProfile
