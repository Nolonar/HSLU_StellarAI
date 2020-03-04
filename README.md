# Stellar

Stellar is the main software behind the fantastic Hyperion autonomous mobile robot.

## Components

Stellar consists of four main components:
* **Perception**: The robot needs information about its environment. Perception collects these data from sensors and turns them into contrete signals.
* **Cognition**: Behaviour to achieve the overall-goal; turns the information around the robots surrounding and movements into decisions about its movement.
* **Action**: Turns planned movements into concrete actions for the robots hardware.
* **Observatory**: Gathers debug- and diagnostic data in order to introspect Stellar's behavior.

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
