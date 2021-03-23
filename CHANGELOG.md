# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [3.0.2]

### Fixed

- Use configured broker when replaying domain events

## [3.0.1]

### Fixed

- Don't connect to default broker when connection settings are set to `None`

## [3.0]

### Added

- Django 3.0 & 3.1 support
- Python 3.8 & 3.9 support
- Inline type information according to PEP 484 / 561

### Removed

- Django 1.11, 2.0 support
- Python 3.5 support

### Changed

- Print formatted JSON event data during interactive replays

### Fixed

- Use timeout during interactive replay to avoid errors when losing connections

## [2.0]

### Added

- Django 2.2 support
- Python 3.7 support

### Changed

- Library and module name has been renamed from `domain_events` to `domain_event_broker`
- Require pika version 1.0.0 or higher

## [1.1]

### Removed

- Python 2.7 support has been dropped

### Changed

- Consumer errors don't stop the application anymore

### Fixed

- Heartbeats are sent even for long-running event handlers

## [1.0.3]

### Added

- Django 2.1 support

### Changed

- Log stacktrace as error if consumers exceed the maximum retry count

## [1.0.2]

### Changed

- Rename package due to PyPI name clash

## [1.0.1]

### Added

- Django 2.0 support
- Python 3.7 support

### Changed

- Delayed messages don't queue up behind messages with longer delays.
- Wait queues and delay exchanges for retried messages are removed automatically.

### Fixed

- Reject messages with invalid payload

## [1.0] - 2017-11-01

First public release.
