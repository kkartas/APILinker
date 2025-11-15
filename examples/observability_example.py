"""
Example: Using OpenTelemetry observability with APILinker

This example demonstrates how to enable distributed tracing and metrics
collection for production observability.
"""

from apilinker import ApiLinker
from apilinker.core.observability import ObservabilityConfig
import time

# Example 1: Enable observability with console export (for debugging)
print("\n" + "="*70)
print("Example 1: Console Observability")
print("="*70)

config = ObservabilityConfig(
    enabled=True,
    service_name="apilinker-example",
    enable_tracing=True,
    enable_metrics=True,
    export_to_console=True,  # Export to console for debugging
)

linker = ApiLinker(
    source_config={
        "type": "rest",
        "base_url": "https://jsonplaceholder.typicode.com",
        "endpoints": {
            "get_users": {
                "path": "/users",
                "method": "GET",
                "params": {"_limit": "3"}
            }
        }
    },
    target_config={
        "type": "rest",
        "base_url": "https://httpbin.org",
        "endpoints": {
            "echo": {
                "path": "/post",
                "method": "POST"
            }
        }
    },
    mapping_config={
        "source": "get_users",
        "target": "echo",
        "fields": [
            {"source": "name", "target": "user_name"},
            {"source": "email", "target": "user_email"}
        ]
    },
    observability_config=config.__dict__,
    log_level="WARNING"  # Quiet logs to see telemetry
)

print("\n📊 Performing sync with telemetry enabled...")
result = linker.sync()
print(f"✅ Synced {result.count} items")
print("📈 Telemetry data exported to console (check logs above)")

# Wait a moment for metrics to be exported
time.sleep(2)


# Example 2: Prometheus metrics export
print("\n" + "="*70)
print("Example 2: Prometheus Metrics Export")
print("="*70)

print("""
To enable Prometheus metrics export, first install the exporter:
    pip install opentelemetry-exporter-prometheus prometheus-client

Then configure APILinker:
""")

print("""
from apilinker.core.observability import ObservabilityConfig

config = ObservabilityConfig(
    enabled=True,
    service_name="my-apilinker-service",
    enable_tracing=True,
    enable_metrics=True,
    export_to_prometheus=True,
    prometheus_host="0.0.0.0",
    prometheus_port=9090
)

linker = ApiLinker(
    ...,
    observability_config=config.__dict__
)

# Metrics will be available at: http://localhost:9090/metrics
""")

print("""
Available metrics:
- apilinker.sync.count              : Total number of sync operations
- apilinker.sync.duration           : Duration of sync operations (ms)
- apilinker.api.calls               : Number of API calls
- apilinker.api.duration            : Duration of API calls (ms)
- apilinker.errors                  : Number of errors by type
- apilinker.transformations         : Number of transformations applied
- apilinker.items.processed         : Number of items processed
""")


# Example 3: Using YAML configuration
print("\n" + "="*70)
print("Example 3: YAML Configuration")
print("="*70)

print("""
# config.yaml
source:
  type: rest
  base_url: https://api.example.com
  endpoints:
    get_data:
      path: /data
      method: GET

target:
  type: rest
  base_url: https://api.target.com
  endpoints:
    post_data:
      path: /data
      method: POST

observability:
  enabled: true
  service_name: "my-service"
  enable_tracing: true
  enable_metrics: true
  export_to_prometheus: true
  prometheus_port: 9090

mapping:
  - source: get_data
    target: post_data
    fields:
      - source: id
        target: identifier
""")

print("""
# Load and use:
linker = ApiLinker(config_path="config.yaml")
linker.sync()
""")


# Example 4: Grafana Dashboard
print("\n" + "="*70)
print("Example 4: Monitoring with Grafana")
print("="*70)

print("""
1. Start Prometheus:
   docker run -p 9090:9090 -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

2. Configure Prometheus to scrape APILinker metrics:
   # prometheus.yml
   scrape_configs:
     - job_name: 'apilinker'
       static_configs:
         - targets: ['host.docker.internal:9090']

3. Start Grafana:
   docker run -p 3000:3000 grafana/grafana

4. Add Prometheus as a data source in Grafana

5. Create dashboard with panels:
   - Sync operations rate: rate(apilinker_sync_count[5m])
   - Avg sync duration: rate(apilinker_sync_duration_sum[5m]) / rate(apilinker_sync_duration_count[5m])
   - Error rate: rate(apilinker_errors[5m])
   - API call latency: histogram_quantile(0.95, apilinker_api_duration_bucket)
""")


# Example 5: Distributed Tracing
print("\n" + "="*70)
print("Example 5: Distributed Tracing")
print("="*70)

print("""
OpenTelemetry tracing provides:
- End-to-end visibility of sync operations
- Individual API call spans with timing
- Transformation operation spans
- Error stack traces in spans
- Correlation across multiple services

Trace structure:
sync_operation (root span)
├── api_call_source
│   └── fetch /users
├── transformation
│   └── lowercase email
├── transformation
│   └── uppercase name
└── api_call_target
    └── POST /users

Export traces to Jaeger, Zipkin, or other backends by adding exporters.
""")


print("\n" + "="*70)
print("✅ Observability Examples Complete")
print("="*70)
print("""
Next steps:
1. Install OpenTelemetry dependencies
2. Configure observability in your config file
3. Set up Prometheus and Grafana for monitoring
4. View metrics at http://localhost:9090/metrics
""")
