"""
Demonstration of observability integration with APILinker sync operations.

This example shows how to:
1. Enable observability in APILinker
2. Perform a sync operation with distributed tracing
3. Record metrics during the sync
4. Export telemetry data to console (or Prometheus if enabled)
"""

from apilinker import ApiLinker

def main():
    """Demonstrate observability during a sync operation."""

    # Configure APILinker with observability enabled
    config = {
        "source": {
            "type": "rest",
            "base_url": "https://jsonplaceholder.typicode.com"
        },
        "target": {
            "type": "rest",
            "base_url": "https://httpbin.org"
        },
        "mappings": [
            {
                "source": "/users",
                "target": "/post",
                "fields": [
                    {"source": "id", "target": "userId"},
                    {"source": "name", "target": "name"},
                    {"source": "email", "target": "email"}
                ]
            }
        ],
        "observability": {
            "enabled": True,
            "service_name": "apilinker-demo",
            "enable_tracing": True,
            "enable_metrics": True,
            "export_to_console": True,  # Set to False to disable console export
            "export_to_prometheus": False,  # Set to True and install OpenTelemetry to enable
            "prometheus_host": "0.0.0.0",
            "prometheus_port": 9090
        }
    }

    # Create APILinker instance with observability
    linker = ApiLinker(
        source_config=config["source"],
        target_config=config["target"],
        observability_config=config["observability"]
    )

    # Add mapping
    for mapping in config["mappings"]:
        linker.add_mapping(**mapping)

    print("=" * 70)
    print("APILinker Observability Demo")
    print("=" * 70)
    print("\nPerforming sync operation with observability enabled...")
    print("- Distributed tracing: ENABLED")
    print("- Metrics collection: ENABLED")
    print("- Console export: ENABLED")
    print("\n" + "=" * 70 + "\n")

    # Perform sync operation (this will be traced and metrics will be recorded)
    result = linker.sync()

    print("\n" + "=" * 70)
    print("Sync Result:")
    print("=" * 70)
    print(f"Success: {result.success}")
    print(f"Items transferred: {result.count}")
    print(f"Duration: {result.duration_ms}ms")
    print(f"Correlation ID: {result.correlation_id}")

    if result.errors:
        print(f"\nErrors: {len(result.errors)}")
        for error in result.errors:
            print(f"  - {error.get('message', 'Unknown error')}")

    print("\n" + "=" * 70)
    print("Telemetry Information:")
    print("=" * 70)
    print(f"Service Name: {linker.telemetry.config.service_name}")
    print(f"Tracing Enabled: {linker.telemetry.config.enable_tracing}")
    print(f"Metrics Enabled: {linker.telemetry.config.enable_metrics}")

    if linker.telemetry.tracer:
        print(f"OpenTelemetry Status: ACTIVE")
    else:
        print(f"OpenTelemetry Status: Not installed (graceful degradation)")

    print("\n" + "=" * 70)
    print("\nNOTE: To enable full OpenTelemetry functionality:")
    print("  1. Install: pip install opentelemetry-api opentelemetry-sdk")
    print("  2. Install: pip install opentelemetry-exporter-prometheus prometheus-client")
    print("  3. Set export_to_prometheus: True in config")
    print("  4. Access metrics at: http://localhost:9090/metrics")
    print("=" * 70)

if __name__ == "__main__":
    main()
