# Scheduling

ApiLinker supports scheduled syncs with flexible scheduling options.

## Interval-Based Scheduling

Run syncs at regular intervals:

```python
from apilinker import ApiLinker

linker = ApiLinker(config_path="config.yaml")
linker.add_schedule(interval_minutes=60)
linker.start_scheduled_sync()
```

## Cron Expressions

Use cron expressions for complex schedules:

```python
# Run every day at 2 AM
linker.add_schedule(cron="0 2 * * *")
```

## Configuration

Add scheduling to your YAML config:

```yaml
schedule:
  type: interval
  minutes: 60
```

Or for cron:

```yaml
schedule:
  type: cron
  expression: "0 2 * * *"
  timezone: "UTC"
```
