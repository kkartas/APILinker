# Monitoring and Alerting

ApiLinker provides a robust monitoring system to track the health of your integrations and alert you when issues arise.

## Overview

The monitoring system allows you to:
- Perform health checks on connectors and components
- Define alert rules based on thresholds or status changes
- Send alerts to PagerDuty, Slack, and Email

## Basic Usage

Initialize the monitoring manager and register health checks:

```python
from apilinker.core.monitoring import MonitoringManager, HealthStatus

monitor = MonitoringManager()

# Register a simple health check
def check_database():
    # Your logic here
    return True

monitor.register_health_check("database", check_database)

# Run checks
results = monitor.run_health_checks()
print(results["database"].status)  # HealthStatus.HEALTHY
```

## Connector Health Checks

ApiConnectors have a built-in `check_health` method that can be registered:

```python
from apilinker import ApiConnector

connector = ApiConnector("rest", "https://api.example.com")
monitor.register_health_check("api_source", connector.check_health)
```

## Alert Rules

Define rules to trigger alerts when conditions are met.

### Status Rules

Trigger an alert when a component becomes unhealthy:

```python
from apilinker.core.monitoring import StatusAlertRule, AlertSeverity

rule = StatusAlertRule(
    name="api_down",
    component="api_source",
    target_status=HealthStatus.UNHEALTHY,
    severity=AlertSeverity.CRITICAL
)
monitor.add_rule(rule)
```

### Threshold Rules

Trigger an alert when a metric exceeds a threshold:

```python
from apilinker.core.monitoring import ThresholdAlertRule

# Assuming you populate context with metrics
rule = ThresholdAlertRule(
    name="high_latency",
    metric="api_source_latency",
    threshold=1000.0,  # ms
    operator=">"
)
monitor.add_rule(rule)
```

## Integrations

Configure where alerts should be sent.

### Slack

```python
from apilinker.core.monitoring import SlackIntegration

slack = SlackIntegration(webhook_url="https://hooks.slack.com/services/...")
monitor.add_integration(slack)
```

### PagerDuty

```python
from apilinker.core.monitoring import PagerDutyIntegration

pd = PagerDutyIntegration(routing_key="your_routing_key")
monitor.add_integration(pd)
```

### Email

```python
from apilinker.core.monitoring import EmailIntegration

email = EmailIntegration(
    smtp_host="smtp.example.com",
    smtp_port=587,
    sender="alerts@example.com",
    recipients=["admin@example.com"],
    username="user",
    password="password"
)
monitor.add_integration(email)
```
