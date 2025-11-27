# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with ApiLinker and explains how to use the robust error handling and recovery system.

## Error Handling & Recovery System

APILinker includes a sophisticated error handling and recovery system to make your API integrations more resilient against common failures. The system includes:

1. **Circuit Breakers** - Prevent cascading failures during service outages
2. **Dead Letter Queues (DLQ)** - Store failed operations for later retry
3. **Configurable Recovery Strategies** - Apply different strategies for different error types
4. **Error Analytics** - Track error patterns and trends

### Using the Error Handling System

The error handling system is configured in your configuration file under the `error_handling` section:

```yaml
error_handling:
  # Configure circuit breakers
  circuit_breakers:
    source_customer_api:  # Name of the circuit breaker
      failure_threshold: 5  # Number of failures before opening circuit
      reset_timeout_seconds: 60  # Seconds to wait before trying again
      half_open_max_calls: 1  # Max calls allowed in half-open state
  
  # Configure recovery strategies by error category
  recovery_strategies:
    network:  # Error category
      - exponential_backoff
      - circuit_breaker
    rate_limit:
      - exponential_backoff
    server:
      - circuit_breaker
      - exponential_backoff
  
  # Configure Dead Letter Queue
  dlq:
    directory: "./dlq"  # Directory to store failed operations
```

## Diagnostic Decision Tree

Start here and follow the branches to diagnose your issue:

1. **Installation Issues**
   - [Package Not Found](#package-not-found)
   - [Version Conflicts](#version-conflicts)
   - [ImportError](#importerror)

2. **Configuration Issues**
   - [Invalid Configuration](#invalid-configuration)
   - [Environment Variables Not Working](#environment-variables)
   - [File Not Found](#file-not-found)

3. **API Connection Issues**
   - [Connection Failed](#connection-failed)
   - [Authentication Failed](#authentication-failed)
   - [SSL/Certificate Errors](#ssl-certificate-errors)
   - [Timeout Errors](#timeout-errors)
   - [Circuit Breaker Open](#circuit-breaker-open)

4. **Mapping Issues**
   - [Missing Fields](#missing-fields)
   - [Transformation Errors](#transformation-errors)
   - [Type Errors](#type-errors)

5. **Runtime Issues**
   - [Scheduling Problems](#scheduling-problems)
   - [Memory Usage](#memory-usage)
   - [Performance Problems](#performance-problems)
   - [DLQ Processing Errors](#dlq-processing-errors)

## Installation Issues

### Package Not Found

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement apilinker
```

**Solutions:**
1. Verify your Python version (3.8+ required):
   ```bash
   python --version
   ```

2. Update pip:
   ```bash
   pip install --upgrade pip
   ```

3. Check your internet connection and try again.

4. If using a corporate network, check proxy settings:
   ```bash
   pip install apilinker --proxy http://your-proxy:port
   ```

### Version Conflicts

**Symptoms:**
```
ERROR: Cannot install apilinker due to dependency conflicts
```

**Solutions:**
1. Create a clean virtual environment:
   ```bash
   python -m venv apilinker_env
   source apilinker_env/bin/activate  # On Windows: apilinker_env\Scripts\activate
   pip install apilinker
   ```

2. Install with the `--no-dependencies` flag and handle dependencies manually:
   ```bash
   pip install --no-dependencies apilinker
   pip install httpx pydantic pyyaml typer
   ```

### ImportError

**Symptoms:**
```python
ImportError: No module named apilinker
```

**Solutions:**
1. Verify installation:
   ```bash
   pip list | grep apilinker
   ```

2. Check your Python environment:
   ```bash
   # On Windows
   where python
   
   # On Linux/Mac
   which python
   ```

3. Try reinstalling:
   ```bash
   pip uninstall -y apilinker
   pip install apilinker
   ```

## Configuration Issues

### Invalid Configuration

**Symptoms:**
```
ConfigError: Invalid configuration at path 'source.auth'
```

**Solutions:**
1. Validate your YAML syntax using an online validator.

2. Check the specific error message for details about what's wrong.

3. Compare with the examples in the documentation.

4. Common issues:
   - Indentation errors
   - Missing required fields
   - Incorrect value types

### Environment Variables

**Symptoms:**
Environment variables are not being replaced in your configuration.

**Solutions:**
1. Verify the environment variable is set:
   ```bash
   # Windows
   echo %API_KEY%
   
   # Linux/Mac
   echo $API_KEY
   ```

2. Check the syntax in your configuration file:
   ```yaml
   # Correct
   auth:
     token: ${API_KEY}
   
   # Incorrect
   auth:
     token: $API_KEY
     token: "{API_KEY}"
   ```

3. Set the environment variable in your script:
   ```python
   import os
   os.environ["API_KEY"] = "your_api_key"
   linker = ApiLinker(config_path="config.yaml")
   ```

### File Not Found

**Symptoms:**
```
FileNotFoundError: No such file or directory: 'config.yaml'
```

**Solutions:**
1. Check the file path:
   ```python
   import os
   print(os.getcwd())  # Current working directory
   ```

2. Use absolute paths:
   ```python
   import os
   config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
   linker = ApiLinker(config_path=config_path)
   ```

## API Connection Issues

### Connection Failed

**Symptoms:**
```
ConnectionError: Failed to establish connection to api.example.com
```

**Solutions:**
1. Verify your internet connection.

2. Check if the API domain is correct and accessible:
   ```bash
   ping api.example.com
   ```

3. Try with a different network or disable firewall temporarily.

4. Add timeout and retry settings:
   ```python
   linker.add_source(
       # Other configuration...
       timeout=30,  # Seconds
       retry={
           "max_attempts": 3,
           "delay_seconds": 2
       }
   )
   ```

### Authentication Failed

**Symptoms:**
```
AuthenticationError: API responded with status code 401 Unauthorized
```

**Solutions:**
1. Verify your credentials are correct.

2. Check if your token or API key has expired.

3. Ensure you're using the correct authentication method.

4. Examine the API documentation for specific auth requirements.

5. Enable debug logging to see the actual request:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### SSL/Certificate Errors

**Symptoms:**
```
SSLError: SSL certificate verification failed
```

**Solutions:**
1. Update your CA certificates.

2. If necessary (and safe), disable SSL verification:
   ```python
   linker.add_source(
       # Other configuration...
       verify_ssl=False  # WARNING: Security risk in production
   )
   ```

3. Specify a custom CA bundle:
   ```python
   linker.add_source(
       # Other configuration...
       verify_ssl="/path/to/ca-bundle.crt"
   )
   ```

### Timeout Errors

**Symptoms:**
```
TimeoutError: Request timed out after 30 seconds
```

**Solutions:**
1. Increase timeout duration:
   ```python
   linker.add_source(
       # Other configuration...
       timeout=60  # Seconds
   )
   ```

2. Check if the API is experiencing high latency.

3. Consider adding pagination for large data sets.

## Mapping Issues

### Missing Fields

**Symptoms:**
```
KeyError: 'Field not found in source data: user_profile'
```

**Solutions:**
1. Print the actual response data to inspect the structure:
   ```python
   data = linker.fetch("get_users")
   print(data[0])  # Print first record
   ```

2. Use dot notation for nested fields:
   ```python
   linker.add_mapping(
       # Other configuration...
       fields=[
           {"source": "user.profile.name", "target": "name"}
       ]
   )
   ```

3. Add conditional mapping:
   ```python
   linker.add_mapping(
       # Other configuration...
       fields=[
           {
               "source": "profile.name", 
               "target": "name",
               "condition": {
                   "field": "profile",
                   "operator": "exists"
               }
           }
       ]
   )
   ```

### Transformation Errors

**Symptoms:**
```
TransformError: Error transforming value: invalid date format
```

**Solutions:**
1. Check the input data format.

2. Add validation in your transformer:
   ```python
   def date_transformer(value, **kwargs):
       if not value or not isinstance(value, str):
           return None
       
       try:
           # Transformation logic
           return transformed_value
       except ValueError:
           return kwargs.get("default", None)
   ```

3. Test the transformer directly:
   ```python
   result = linker.mapper.transform("2023-01-01", "date_transformer")
   print(result)
   ```

### Type Errors

**Symptoms:**
```
TypeError: Cannot process input of type: dict
```

**Solutions:**
1. Add type checking:
   ```python
   def my_transformer(value, **kwargs):
       if isinstance(value, dict):
           return json.dumps(value)
       elif isinstance(value, (int, float)):
           return str(value)
       return value
   ```

2. Use a pre-processor:
   ```python
   def pre_process(data):
       for item in data:
           if "amount" in item and item["amount"] is not None:
               item["amount"] = float(item["amount"])
       return data
   
   linker.add_source_processor("get_data", pre_process)
   ```

## API Connection Issues

### Connection Failed

**Symptoms:**
```
ConnectionError: Failed to establish connection to api.example.com
```

**Solutions:**
1. Check your internet connection
2. Verify the API is online using a tool like cURL or Postman
3. Check if the API domain resolves correctly:
   ```bash
   ping api.example.com
   ```
4. Check for firewall or proxy issues in your environment

### Authentication Failed

**Symptoms:**
```
APILinkerError: [AUTHENTICATION] Failed to fetch data: 401 Unauthorized
```

**Solutions:**
1. Verify your credentials are correct
2. Check if the token has expired
3. Ensure you're using the correct authentication method for the API
4. Check if your API key has the necessary permissions

### SSL/Certificate Errors

**Symptoms:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions:**
1. Update your CA certificates
2. If working in a development environment, you can disable verification (not recommended for production):
   ```python
   connector.client.verify = False
   ```
3. Provide the path to your custom certificate:
   ```python
   connector.client.verify = '/path/to/cert.pem'
   ```

### Timeout Errors

**Symptoms:**
```
APILinkerError: [TIMEOUT] Failed to fetch data: Request timed out
```

**Solutions:**
1. Increase the timeout in your configuration:
   ```yaml
   source:
     timeout: 60  # Seconds
   ```
2. Check if the API endpoint is slow or under heavy load
3. Consider adding exponential backoff retry strategy:
   ```yaml
   error_handling:
     recovery_strategies:
       timeout:
         - exponential_backoff
   ```

### Circuit Breaker Open

**Symptoms:**
```
APILinkerError: Circuit breaker 'source_customer_api' is open
```

**Solutions:**
1. Wait for the circuit breaker to reset (typically 60 seconds by default)
2. Check the health of the API service that's failing
3. Adjust your circuit breaker configuration if needed:
   ```yaml
   error_handling:
     circuit_breakers:
       source_customer_api:
         failure_threshold: 10  # More permissive
         reset_timeout_seconds: 30  # Quicker reset
   ```
4. Use error analytics to diagnose recurring problems:
   ```python
   error_stats = linker.get_error_analytics()
   print(error_stats)
   ```

## Runtime Issues

### Scheduling Problems

**Symptoms:**
Scheduled syncs not running at expected times.

**Solutions:**
1. Check your system time and timezone.

2. Verify the cron expression format.

3. Ensure your script is kept running:
   ```python
   # Add this at the end of your script
   try:
       # Keep the process alive
       while True:
           time.sleep(60)
   except KeyboardInterrupt:
       print("Stopping scheduled syncs")
       linker.stop_scheduled_sync()
   ```

4. Use a dedicated task scheduler like systemd, cron, or Windows Task Scheduler.

### Memory Usage

**Symptoms:**
High memory usage or `MemoryError` exceptions.

**Solutions:**
1. Process data in batches:
   ```python
   linker.add_mapping(
       # Other configuration...
       batch_size=100  # Process 100 records at a time
   )
   ```

2. Use pagination with limits:
   ```python
   linker.add_source(
       # Other configuration...
       endpoints={
           "get_data": {
               # Other configuration...
               "pagination": {
                   "limit": 200,  # Get 200 records per page
                   "page_param": "page"
               }
           }
       }
   )
   ```

3. Implement a custom stream processor for very large datasets.

### Performance Problems

**Symptoms:**
- Syncs take longer than expected
- High memory usage
- Slow response times

**Solutions:**
1. Use batch processing for large datasets
2. Add appropriate indexes to your database
3. Use pagination for large API responses
4. Profile your transformers to identify bottlenecks
5. Consider adding caching for frequently accessed data

## DLQ Processing Errors

**Symptoms:**
```
Failed to retry DLQ item: item_id
```

**Solutions:**
1. Check the DLQ item's payload and error details:
   ```python
   items = linker.dlq.get_items(limit=10)
   print(items[0])  # Examine the first item
   ```

2. Process specific types of failed operations:
   ```python
   results = linker.process_dlq(operation_type="source_customer_api")
   print(f"Processed {results['total_processed']} items, {results['successful']} succeeded")
   ```

3. Manually fix issues and retry:
   ```python
   # For specific item
   linker.dlq.retry_item("item_id", my_operation_function)
   ```

4. Check the error category distribution to identify patterns:
   ```python
   analytics = linker.get_error_analytics()
   print(analytics["error_counts_by_category"])
   ```

## Error Handling System Details

### Circuit Breaker Pattern

The circuit breaker pattern prevents cascading failures by temporarily stopping calls to failing services. It has three states:

- **CLOSED** - Normal operation, requests pass through
- **OPEN** - Service is failing, requests fail fast without calling the service
- **HALF-OPEN** - Testing if service has recovered with limited requests

Configuration options:
```yaml
circuit_breakers:
  name_of_breaker:
    failure_threshold: 5      # Failures before opening
    reset_timeout_seconds: 60 # Time before half-open
    half_open_max_calls: 1    # Test calls allowed
```

### Recovery Strategies

APILinker supports these recovery strategies:

- **RETRY** - Simple retry without delay
- **EXPONENTIAL_BACKOFF** - Retry with increasing delays
- **CIRCUIT_BREAKER** - Use circuit breaker pattern
- **FALLBACK** - Use default data instead
- **SKIP** - Skip the operation
- **FAIL_FAST** - Fail immediately

Configure by error category:
```yaml
recovery_strategies:
  network:                  # Error category
    - exponential_backoff   # First strategy
    - circuit_breaker       # Second strategy
```

Available error categories:
- NETWORK - Network connectivity issues
- AUTHENTICATION - Auth failures
- VALIDATION - Invalid data
- TIMEOUT - Request timeouts
- RATE_LIMIT - API returned 429 (rate limited): apply exponential backoff and retry
- SERVER - Server errors (5xx)
- CLIENT - Client errors (4xx)
- MAPPING - Data mapping errors
- PLUGIN - Plugin errors
- UNKNOWN - Uncategorized errors

### Dead Letter Queue (DLQ)

The DLQ stores failed operations for later analysis and retry. Each entry contains:
- Error details (category, message, status code)
- Original payload that caused the failure
- Timestamp and operation context
- Correlation ID for tracing

Access DLQ data:
```python
# Get failed operations
items = linker.dlq.get_items(error_category=ErrorCategory.RATE_LIMIT)

# Retry operations
linker.process_dlq(operation_type="source_customers", limit=10)
```

### Error Analytics

The error analytics system tracks:
- Error counts by category
- Error rates over time
- Top error types

Access analytics:
```python
analytics = linker.get_error_analytics()
print(f"Error rate: {analytics['recent_error_rate']} errors/minute")
print(f"Top errors: {analytics['top_errors']}")
```

**Symptoms:**
Syncs taking too long to complete.

**Solutions:**
1. Enable performance logging:
   ```python
   linker = ApiLinker(performance_logging=True)
   ```

2. Optimize transformers:
   - Avoid unnecessary operations
   - Cache repeated calculations
   - Use built-in functions where possible

3. Use concurrent requests when appropriate:
   ```python
   linker.add_source(
       # Other configuration...
       concurrency=5  # Up to 5 concurrent requests
   )
   ```

4. Implement partial syncs with filters:
   ```python
   linker.add_source(
       # Other configuration...
       endpoints={
           "get_data": {
               # Other configuration...
               "params": {
                   "updated_since": "{{last_sync}}"  # Only get recently changed data
               }
           }
       }
   )
   ```

## Debugging Techniques

### Enable Debug Logging

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Use Dry Run Mode

```python
# Test the sync without making changes
result = linker.sync(dry_run=True)
print(f"Would sync {result.count} records")
print(f"Preview: {result.preview[:3]}")  # First 3 records
```

### Inspect API Requests

```python
# Install HTTP debugging tool
# pip install httpx-debug

import httpx_debug
httpx_debug.install()  # Shows all HTTP requests and responses
```

### Interactive Debugging

```python
# Add this where you want to inspect
import pdb; pdb.set_trace()
# or
breakpoint()  # Python 3.7+
```

If you're still experiencing issues after trying these solutions, please [open an issue](https://github.com/kkartas/apilinker/issues) on GitHub with detailed information about your problem.
