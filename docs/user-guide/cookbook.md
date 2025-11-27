# ApiLinker Cookbook

This cookbook provides practical recipes for common integration tasks.

## Working with Pagination

### Problem
You need to fetch large datasets that span multiple pages.

### Solution
```python
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    endpoints={
        "get_users": {
            "path": "/users",
            "method": "GET",
            # Pagination configuration based on the API response format
            "pagination": {
                "data_path": "data",                # Path to items array in response
                "next_page_path": "meta.next_page", # Path to next page URL/token
                "page_param": "page"                # Query param name for page number
            }
        }
    }
)

# ApiLinker will automatically handle pagination
all_users = linker.fetch("get_users")
```

### Common Pagination Patterns

#### Page Number Pagination
```python
"pagination": {
    "data_path": "data",
    "page_param": "page"  # Will increment: page=1, page=2, etc.
}
```

#### Next URL Pagination
```python
"pagination": {
    "data_path": "data",
    "next_page_path": "links.next"  # Response contains full next URL
}
```

## Implementing Robust Error Handling

### Problem
You need reliable API integrations that can handle service outages and temporary network issues.

### Solution
Use APILinker's robust error handling and recovery system:

```yaml
# In your config.yaml
error_handling:
  # Configure circuit breakers to prevent cascading failures
  circuit_breakers:
    source_customers_api:
      failure_threshold: 5        # Open circuit after 5 consecutive failures
      reset_timeout_seconds: 60   # Wait 60 seconds before testing service again
      half_open_max_calls: 1      # Allow 1 test call in half-open state
  
  # Configure error handling strategies by error category
  recovery_strategies:
    network:                      # Network connectivity issues
      - exponential_backoff       # First try with increasing delays
      - circuit_breaker           # Then use circuit breaker if still failing
    # rate limiting: not built-in; use server guidance and retries
      - exponential_backoff       # Back off and retry
    server:                       # Server errors (5xx)
      - exponential_backoff
      - circuit_breaker
    timeout:                      # Request timeout errors
      - exponential_backoff
  
  # Configure Dead Letter Queue for failed operations
  dlq:
    directory: "./dlq"           # Store failed operations here
```

### Accessing Error Analytics

```python
from apilinker import ApiLinker

# Initialize with error handling config
linker = ApiLinker(config_path="config.yaml")

# Get error statistics
analytics = linker.get_error_analytics()
print(f"Recent error rate: {analytics['recent_error_rate']} errors/minute")
print(f"Most common errors: {analytics['top_errors']}")

# Check for failed operations in DLQ
items = linker.dlq.get_items(limit=10)
if items:
    print(f"Found {len(items)} failed operations in DLQ")
    
    # Process specific types of failed operations
    results = linker.process_dlq(operation_type="source_customers_api")
    print(f"Processed {results['successful']} items successfully")
```

### Handling Different Error Types

```python
from apilinker.core.error_handling import ErrorCategory, RecoveryStrategy

# Configure specific recovery strategies programmatically
linker.error_recovery_manager.set_strategy(
    ErrorCategory.RATE_LIMIT,
    [
        RecoveryStrategy.EXPONENTIAL_BACKOFF,
        RecoveryStrategy.SKIP  # Skip rate-limited operations
    ],
    operation_type="fetch_users"  # Only for this operation
)

# Execute with enhanced error handling
try:
    result = linker.sync("fetch_users", "create_users")
    print(f"Synced {result.count} users")
    
    # Check if any errors occurred
    if not result.success:
        print(f"Completed with {len(result.errors)} errors")
        for error in result.errors:
            print(f"- {error['message']}")
            
except Exception as e:
    print(f"Critical error: {str(e)}")
```

### Explanation
The ApiConnector's _handle_pagination method automatically:
1. Extracts data items from each response using the data_path
2. Determines the next page using next_page_path if available
3. Increments page parameters for subsequent requests
4. Combines results from all pages

## Handling API Rate Limits

### Problem
Your API requests are getting rate limited (HTTP 429).

### Solution
```python
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    # Configure retry settings
    retry_count=3,         # Try 3 times before failing
    retry_delay=2,         # Wait 2 seconds between retries
    # Add longer timeout for slow APIs
    timeout=30,            # 30 second timeout
    endpoints={
        # Your endpoints here
    }
)

# For manual handling of 429s with backoff
def handle_rate_limits(func):
    def wrapper(*args, **kwargs):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "rate limit" in str(e).lower() and attempt < max_attempts - 1:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
    return wrapper

# Apply to your function
@handle_rate_limits
def fetch_data():
    return linker.fetch("get_data")
```

### Explanation
- The retry mechanism is built into ApiConnector for temporary failures
- For specific rate limit handling, implement a decorator or wrapper function in your app
- The connector will automatically use exponential backoff between retries

## Transforming Nested JSON Structures

### Problem
You need to extract and transform data from complex nested JSON structures.

### Solution
```python
linker.add_mapping(
    source="get_data",
    target="save_data",
    fields=[
        # Access nested properties with dot notation
        {"source": "user.profile.name", "target": "fullName"},
        
        # Access array items with indices
        {"source": "addresses[0].street", "target": "primary_address"},
        
        # Custom transformer for nested objects
        {
            "source": "metadata",  # This is an object
            "target": "meta_info", 
            "transform": "flatten_metadata"
        }
    ]
)

# Define transformer for nested object
def flatten_metadata(value, **kwargs):
    if not value or not isinstance(value, dict):
        return {}
    
    result = {}
    # Extract selected fields with prefixes
    for key in ["created", "updated", "status"]:
        if key in value:
            result[f"meta_{key}"] = value[key]
    
    # Flatten nested object
    if "details" in value and isinstance(value["details"], dict):
        for k, v in value["details"].items():
            result[f"detail_{k}"] = v
    
    return result

# Register the transformer
linker.mapper.register_transformer("flatten_metadata", flatten_metadata)
```

### Explanation
- Dot notation accesses nested properties
- Array indices access specific items in arrays
- Custom transformers handle complex transformations

## Syncing Only Changed Records

### Problem
You want to sync only records that have changed since the last sync.

### Solution
```python
# Method 1: Using template variables
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    endpoints={
        "get_users": {
            "path": "/users",
            "method": "GET",
            "params": {
                "updated_since": "{{last_sync}}",  # Template variable
                "sort": "updated_at"
            }
        }
    }
)

# Method 2: Using a filter function
def filter_changed_records(data, **kwargs):
    last_sync = kwargs.get("last_sync")
    if not last_sync:
        return data  # Return all if no last sync
    
    # Convert to datetime for comparison
    from datetime import datetime
    last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
    
    # Filter items updated since last sync
    return [
        item for item in data
        if "updated_at" in item and 
           datetime.fromisoformat(item["updated_at"].replace('Z', '+00:00')) > last_sync_dt
    ]

# Register the filter
linker.add_source_processor("get_users", filter_changed_records)

# Get last sync time from storage
last_sync_time = linker.get_last_sync_time() or "2023-01-01T00:00:00Z"

# Run the sync with context
result = linker.sync(context={"last_sync": last_sync_time})
```

### Explanation
- Template variables like `{{last_sync}}` are replaced with values at runtime
- Source processors can filter or modify data before mapping
- Context variables can be passed to processors

## Working with Files and Binary Data

### Problem
You need to handle file uploads or downloads.

### Solution
```python
# File download
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    endpoints={
        "get_document": {
            "path": "/documents/{doc_id}",
            "method": "GET",
            "response_type": "binary"  # Treat response as binary
        }
    }
)

# Custom transformer to save files
def save_file(binary_data, **kwargs):
    if not binary_data:
        return None
        
    filename = kwargs.get("filename", "document.pdf")
    file_path = f"downloads/{filename}"
    
    # Create directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write binary data to file
    with open(file_path, "wb") as f:
        f.write(binary_data)
    
    return {
        "path": file_path,
        "size": len(binary_data),
        "status": "downloaded"
    }

# Register transformer
linker.mapper.register_transformer("save_file", save_file)

# Use it in a mapping
linker.add_mapping(
    source="get_document",
    target="log_download",
    fields=[
        {
            "source": "_response",  # Special field with raw response
            "target": "file_info",
            "transform": "save_file",
            "filename": "report.pdf"
        }
    ]
)

# File upload
linker.add_target(
    type="rest",
    base_url="https://api.destination.com",
    endpoints={
        "upload_file": {
            "path": "/upload",
            "method": "POST",
            "headers": {
                "Content-Type": "application/octet-stream"
            }
        }
    }
)

# Read file transformer
def read_file(file_path, **kwargs):
    if not file_path or not isinstance(file_path, str):
        return None
    
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Register transformer
linker.mapper.register_transformer("read_file", read_file)
```

### Explanation
- Set `response_type: "binary"` for file downloads
- Use `Content-Type: "application/octet-stream"` for file uploads
- Use custom transformers to handle file operations

## Conditional Mapping

### Problem
You need to apply different mappings based on data conditions.

### Solution
```python
linker.add_mapping(
    source="get_products",
    target="create_item",
    fields=[
        # Basic fields always included
        {"source": "id", "target": "product_id"},
        {"source": "name", "target": "title"},
        
        # Only include if value exists
        {
            "source": "description",
            "target": "description",
            "condition": {
                "field": "description",
                "operator": "exists"
            }
        },
        
        # Apply different mapping based on status
        {
            "source": "status",
            "target": "status",
            "transform": "map_active_status",
            "condition": {
                "field": "status",
                "operator": "equals",
                "value": "active"
            }
        },
        
        # Apply different mapping for inactive items
        {
            "target": "status",
            "value": "discontinued",
            "condition": {
                "field": "status",
                "operator": "equals",
                "value": "inactive"
            }
        },
        
        # Complex condition using multiple fields
        {
            "source": "price",
            "target": "discount_price",
            "transform": "calculate_discount",
            "condition": {
                "field": "on_sale",
                "operator": "equals",
                "value": True
            },
            "discount_percent": 15
        }
    ]
)

# Status mapper transformer
def map_active_status(value, **kwargs):
    status_map = {
        "active": "in_stock",
        "pending": "coming_soon"
    }
    return status_map.get(value, value)

# Calculate discount transformer
def calculate_discount(value, **kwargs):
    if not isinstance(value, (int, float)) or value <= 0:
        return value
    
    discount = kwargs.get("discount_percent", 10)
    return round(value * (1 - discount / 100), 2)

# Register transformers
linker.mapper.register_transformer("map_active_status", map_active_status)
linker.mapper.register_transformer("calculate_discount", calculate_discount)
```

### Explanation
- The `condition` property controls when a field mapping is applied
- Supported operators: `exists`, `not_exists`, `equals`, `not_equals`, `in`, `not_in`
- You can use fixed values with `value` property
- Custom transformers can use additional parameters

## Using Environment Variables for Credentials

### Problem
You need to securely manage API credentials without hardcoding them.

### Solution
```python
# Method 1: Environment variables in configuration
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    auth={
        "type": "bearer",
        "token": "${API_TOKEN}"  # Will be replaced with API_TOKEN env var
    }
)

# Method 2: Load from .env file
from dotenv import load_dotenv
load_dotenv()  # Loads variables from .env file

# Method 3: Set variables in script (for testing)
import os
os.environ["API_TOKEN"] = "your_token"  # Only for testing!

# Method 4: Use a credential manager
def get_credential(name):
    # Implement your secure credential retrieval logic here
    # Examples: AWS Secrets Manager, HashiCorp Vault, etc.
    return "secure_credential"

# Use retrieved credentials
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    auth={
        "type": "bearer",
        "token": get_credential("api_token")
    }
)
```

### Explanation
- Environment variables are the simplest secure method
- .env files are convenient for development
- Never hardcode credentials in source code
- Consider using a dedicated secrets manager for production

## Error Handling and Validation

### Problem
You need to handle errors gracefully and validate data.

### Solution
```python
# Custom error handler
def handle_sync_error(error, context):
    import logging
    logging.error(f"Sync error: {error}")
    
    # Send notification
    send_notification(f"Sync failed: {error}")
    
    # Determine whether to retry based on error type
    if "rate limit" in str(error).lower():
        # Wait longer for rate limits
        import time
        time.sleep(60)
        return True  # Retry
        
    if "connection" in str(error).lower():
        # Retry connection errors up to 3 times
        attempt = context.get("attempt", 1)
        if attempt <= 3:
            context["attempt"] = attempt + 1
            return True  # Retry
            
    return False  # Don't retry other errors

# Register error handler
linker.add_error_handler(handle_sync_error)

# Data validation
def validate_customer_data(data, **kwargs):
    if not isinstance(data, list):
        raise ValueError("Expected a list of customers")
        
    valid_items = []
    for item in data:
        # Skip invalid items
        if not isinstance(item, dict):
            continue
            
        # Require email field
        if "email" not in item or not item["email"]:
            continue
            
        # Format validation
        if "phone" in item and item["phone"]:
            # Clean phone number
            item["phone"] = ''.join(c for c in item["phone"] if c.isdigit())
            
        # Normalize fields
        if "name" in item and item["name"]:
            item["name"] = item["name"].strip().title()
            
        valid_items.append(item)
        
    return valid_items

# Register validator
linker.add_source_processor("get_customers", validate_customer_data)
```

### Explanation
- Error handlers determine whether to retry after errors
- Error context is preserved between retries
- Source processors can validate and normalize data
- Validators can filter out invalid records

## Logging and Debugging

### Problem
You need to track API operations and diagnose issues.

### Solution
```python
import logging
import time

# Configure logging for ApiLinker
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("apilinker.log"),
        logging.StreamHandler()
    ]
)

# Initialize ApiLinker with log level
linker = ApiLinker(log_level="DEBUG", log_file="apilinker.log")

# Add custom timing measurement
class SimpleTimer:
    def __init__(self):
        self.start_times = {}
        self.results = {}
    
    def start(self, operation_name):
        self.start_times[operation_name] = time.time()
        
    def end(self, operation_name):
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            self.results[operation_name] = duration
            logging.info(f"{operation_name} completed in {duration:.2f} seconds")
            return duration
        return None

# Use the timer in your code
timer = SimpleTimer()

# Create a wrapper for timing operations
def timed_operation(func):
    def wrapper(*args, **kwargs):
        operation_name = func.__name__
        timer.start(operation_name)
        try:
            result = func(*args, **kwargs)
            timer.end(operation_name)
            return result
        except Exception as e:
            logging.error(f"Error in {operation_name}: {e}")
            timer.end(operation_name)
            raise
    return wrapper

# Use the decorator for operations you want to time
@timed_operation
def fetch_and_process():
    # Fetch data
    logging.info("Fetching data from source")
    source_data = linker.fetch("get_data")
    
    # Log response summary (without sensitive data)
    logging.info(f"Fetched {len(source_data) if isinstance(source_data, list) else 1} records")
    
    # Process data
    logging.info("Processing data")
    result = linker.sync()
    
    # Log processing results
    logging.info(f"Processed {result.count} records")
    if result.errors:
        logging.warning(f"Encountered {len(result.errors)} errors")
        
    return result

# Execute with debug logging
try:
    result = fetch_and_process()
    print(f"Sync completed successfully: {result.count} records")
    print(f"Operation times: {timer.results}")
except Exception as e:
    print(f"Sync failed: {e}")
```

### Explanation
- ApiLinker has built-in logging that can be configured with different levels
- You can create simple timing utilities to measure performance
- Use the Python logging module for structured logs
- Use decorators to consistently measure and log operations
