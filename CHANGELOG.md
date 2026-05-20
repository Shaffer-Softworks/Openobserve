# Changelog

## 0.1.0 (2026-05-17)

- Initial HACS integration: logs and HA bus events to OpenObserve `/_json`
- Config flow with options for event groups, exclusions, and batching
- Diagnostic sensors and `openobserve.flush` service
- Optional Supervisor add-on: Fluent Bit tail of `home-assistant.log` to `/_multi`
