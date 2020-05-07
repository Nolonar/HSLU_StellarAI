# Stellar

Stellar is the main software behind the fantastic Hyperion autonomous mobile robot.

## Components

Stellar consists of four main components:

### Perception

The robot needs information about its environment. Perception collects these data from sensors and turns them into concrete signals.

Aims to solve following problems:
* Receive information about the robots environment
* Aligns sensor signals in a chronological manner
* Abstracts underlying hardware.

### Cognition

Consists of the main logic; behaviour to achieve the overall-goals.

Aims to solve following problems:
* Mapping of the environment
* Localizing the robot in the environment
* Plan an optimal path through the parcours
* Track robot on the planned path

### Action

Translates current state into concrete signals for the underlying hardware.

Aims to solve following problems:
* Send signals to the engine as well as steering
* Abstracts underlying hardware


### Observatory

Gathers debug- and diagnostic data in order to introspect Stellar's behavior.

Aims to solve following problems:
* Allowing introspection into the inner-workings of stellar
* Forward information to the debug UI.


### Communication

Provides the infrastructure for modules to communicate with each other.


# Getting started

## Dependencies
- Python 3
- Pipenv

Install all (development-) dependencies
```sh
$ pipenv install --dev
```

## Run tests

This project is using the pytest framework. To run the tests:
```sh
$ pipenv run pytest tests/
```
