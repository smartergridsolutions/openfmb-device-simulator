# OpenFMB Device Simulator

[![View build status on Travis CI](https://travis-ci.org/smartergridsolutions/openfmb-device-simulator.svg?branch=master)](https://travis-ci.org/smartergridsolutions/openfmb-device-simulator)
[![View code quality on Codacy](https://api.codacy.com/project/badge/Grade/3182844be1e6487d88af74d8f22e3007)](https://www.codacy.com/app/garretfick/openfmb-device-simulator?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=smartergridsolutions/openfmb-device-simulator&amp;utm_campaign=Badge_Grade)
[![Join the chat on Gitter](https://badges.gitter.im/smartergridsolutions/openfmb-device-simulator.svg)](https://gitter.im/smartergridsolutions/openfmb-device-simulator?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


OpenFMB Device Simulator is a simple simulator that publishes information using
NATS messaging about simulated devices and accepts control requests for those
devices. The intended purpose of this simulator is to enable testing with other
systems. A minimal system contains several components and this project provides
a couple of those to aid with development and testing:

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

This OpenFMB Device Simulator enables you to quickly develop other systems that
subscribe to or publish messages without needing physical hardware.

## How to Run

See the OpenFMB Device Simulator [instructions](https://smartergridsolutions.github.io/openfmb-device-simulator/)
for details on how to run the simulator.

## Contributing

There are several ways in which you can participate in the project. In
particular, we are seeking help in:

* Extending the models that this simulator supports.
* Adding the ability to specify simulated devices at start-time and run-time.
* Creating a package that can be installed with pip (ask about why this is a
  bit of work) and creates the appropriate application entry point.
* Add support for additional messaging protocols.

If you are not sure, create an issue and we'll respond.

See the developing guide if you want to contribute code.
