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
            "pagination": {
                "data_path": "data",                # Path to items array
                "next_page_path": "meta.next_page", # Path to next page URL/token
                "page_param": "page",               # Query param name for page number
                "limit_param": "limit",             # Query param for page size
                "limit": 100                        # Number of items per page
            }
        }
    }
)

# ApiLinker will automatically handle pagination
all_users = linker.fetch("get_users")
```

### Explanation
The pagination configuration tells ApiLinker how to:
1. Find the data items in each response
2. Find the link to the next page
3. Construct the pagination parameters

## Handling Rate Limits

### Problem
Your API requests are getting rate limited.

### Solution
```python
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    # Add rate limiting
    rate_limit={
        "requests_per_second": 5,  # Max 5 requests per second
        "burst": 10                # Allow bursts up to 10 requests
    },
    # Add retry configuration
    retry={
        "max_attempts": 3,         # Try 3 times before failing
        "delay_seconds": 2,        # Wait 2 seconds between retries
        "backoff_factor": 1.5,     # Exponential backoff
        "status_codes": [429, 500, 502, 503, 504]  # Retry these status codes
    },
    endpoints={
        # Your endpoints here
    }
)
```

### Explanation
- The rate limiter prevents sending too many requests too quickly
- The retry mechanism automatically handles temporary failures
- Exponential backoff increases wait time between retries

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

## Logging and Monitoring

### Problem
You need to track API operations and diagnose issues.

### Solution
```python
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("apilinker.log"),
        logging.StreamHandler()
    ]
)

# Create custom logger
logger = logging.getLogger("apilinker")

# Add custom logging for API operations
class APILogger:
    def __init__(self, log_file="api_operations.log"):
        self.log_file = log_file
        
    def log_operation(self, operation_type, details):
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "operation": operation_type,
            **details
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

# Create logger instance
api_logger = APILogger()

# Log requests and responses
def log_request(request_data, **kwargs):
    # Log the request (excluding sensitive data)
    safe_data = request_data.copy()
    if "auth" in safe_data:
        safe_data["auth"] = "[REDACTED]"
        
    api_logger.log_operation(
        "request",
        {
            "endpoint": kwargs.get("endpoint", "unknown"),
            "method": kwargs.get("method", "GET"),
            "data": safe_data
        }
    )
    return request_data  # Return unmodified data

def log_response(response_data, **kwargs):
    # Log summary of response
    summary = {
        "status": kwargs.get("status", 200),
        "size": len(str(response_data)),
        "record_count": len(response_data) if isinstance(response_data, list) else 1
    }
    
    api_logger.log_operation(
        "response",
        {
            "endpoint": kwargs.get("endpoint", "unknown"),
            "summary": summary
        }
    )
    return response_data  # Return unmodified data

# Register processors
linker.add_request_processor(log_request)
linker.add_response_processor(log_response)

# Create a performance monitor
class PerformanceMonitor:
    def __init__(self):
        self.operations = {}
        
    def start(self, operation_name):
        import time
        self.operations[operation_name] = {
            "start": time.time(),
            "status": "running"
        }
        
    def end(self, operation_name):
        import time
        if operation_name in self.operations:
            self.operations[operation_name]["end"] = time.time()
            self.operations[operation_name]["duration"] = (
                self.operations[operation_name]["end"] - 
                self.operations[operation_name]["start"]
            )
            self.operations[operation_name]["status"] = "completed"
            
            # Log if slow (>5 seconds)
            if self.operations[operation_name]["duration"] > 5:
                logger.warning(
                    f"Slow operation: {operation_name} took "
                    f"{self.operations[operation_name]['duration']:.2f} seconds"
                )
                
        return self.operations.get(operation_name)
    
    def report(self):
        return {k: v for k, v in self.operations.items() if v.get("status") == "completed"}

# Create monitor instance
monitor = PerformanceMonitor()

# Use in your code
def sync_with_monitoring():
    monitor.start("full_sync")
    
    try:
        # Source fetch
        monitor.start("fetch_source")
        source_data = linker.fetch("get_data")
        fetch_timing = monitor.end("fetch_source")
        
        # Process and map
        monitor.start("transform_data") 
        result = linker.sync()
        transform_timing = monitor.end("transform_data")
        
        # Overall completion
        sync_timing = monitor.end("full_sync")
        
        logger.info(f"Sync completed in {sync_timing['duration']:.2f} seconds")
        logger.info(f"  Fetch: {fetch_timing['duration']:.2f}s, Transform: {transform_timing['duration']:.2f}s")
        
        return result
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        monitor.end("full_sync")
        raise
```

### Explanation
- Structured logging helps with troubleshooting
- Request/response processors track API interactions
- Performance monitoring identifies bottlenecks
- Redacting sensitive information improves security
