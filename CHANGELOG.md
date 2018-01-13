# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Django 2.0 support
- Python 3.7 support

### Changed

- Delayed messages don't queue up behind messages with longer delays.
- Wait queues and delay exchanges for retried messages are removed automatically.

## [1.0] - 2017-11-01

First public release.
