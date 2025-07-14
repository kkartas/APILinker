# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with ApiLinker.

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

4. **Mapping Issues**
   - [Missing Fields](#missing-fields)
   - [Transformation Errors](#transformation-errors)
   - [Type Errors](#type-errors)

5. **Runtime Issues**
   - [Scheduling Problems](#scheduling-problems)
   - [Memory Usage](#memory-usage)
   - [Performance Problems](#performance-problems)

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
