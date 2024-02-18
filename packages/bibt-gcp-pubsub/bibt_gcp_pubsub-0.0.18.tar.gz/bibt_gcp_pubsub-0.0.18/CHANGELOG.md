# Changelog

[PyPI History](https://pypi.org/project/bibt-gcp-pubsub/#history)

## 0.0.18 (2024-02-07)

- Added `future.result()` to `send_pubsub` call to monitor for errors.
- Added `process_event()` to handle CloudEvent type triggers.
- Reduced default processing timeout from 1800 seconds to 600 seconds.

## 0.0.8 (2024-01-10)

- Automatic token refresh capability.

## 0.0.5 (2023-12-12)

- Initial library functionality; `Client.send_pubsub` and `process_trigger`.
