# Changelog

## 0.2.2 (2026-05-20)

- Use async bus listeners so event handlers run on the HA event loop (HA runs sync listeners in a thread pool)
- Thread-safe `enqueue_log` / `enqueue_event` via `call_soon_threadsafe` when called off-loop

## 0.2.1 (2026-05-20)

- Fix thread-safety warning: schedule batch flushes via `loop.call_soon_threadsafe` instead of calling `async_create_task` from worker threads
- Debounce batch-triggered flushes to avoid spawning hundreds of concurrent tasks under load

## 0.2.0 (2026-05-20)

- Split Supervisor add-on to [home-assistant-openobserve-addon](https://github.com/Shaffer-Softworks/home-assistant-openobserve-addon)
- This repo is HACS integration only

## 0.1.0 (2026-05-17)

- Initial HACS integration: logs and HA bus events to OpenObserve `/_json`
- Config flow with options for event groups, exclusions, and batching
- Diagnostic sensors and `openobserve.flush` service
- Optional Supervisor add-on: Fluent Bit tail of `home-assistant.log` to `/_multi`
