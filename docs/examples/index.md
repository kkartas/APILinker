# ApiLinker Examples

This section provides practical examples of ApiLinker usage for common integration scenarios.

## Basic Examples

### Simple Data Fetch

Fetch data from a REST API:

```python
from apilinker import ApiLinker

# Initialize ApiLinker
linker = ApiLinker()

# Configure source API
linker.add_source(
    type="rest",
    base_url="https://jsonplaceholder.typicode.com",  # Free testing API
    endpoints={
        "get_posts": {
            "path": "/posts",
            "method": "GET",
            "params": {"_limit": 5}
        }
    }
)

# Fetch data
posts = linker.fetch("get_posts")

# Process data
for post in posts:
    print(f"Post #{post['id']}: {post['title']}")
```

### Basic Sync

Sync data between two endpoints:

```python
from apilinker import ApiLinker

# Initialize ApiLinker
linker = ApiLinker()

# Configure source API
linker.add_source(
    type="rest",
    base_url="https://source-api.example.com",
    auth={
        "type": "bearer",
        "token": "${SOURCE_API_TOKEN}"
    },
    endpoints={
        "get_products": {
            "path": "/products",
            "method": "GET",
            "params": {"updated_since": "2023-01-01"}
        }
    }
)

# Configure target API
linker.add_target(
    type="rest",
    base_url="https://target-api.example.com",
    auth={
        "type": "api_key",
        "header": "X-API-Key",
        "key": "${TARGET_API_KEY}"
    },
    endpoints={
        "create_product": {
            "path": "/products",
            "method": "POST"
        }
    }
)

# Define mapping
linker.add_mapping(
    source="get_products",
    target="create_product",
    fields=[
        {"source": "id", "target": "external_id"},
        {"source": "name", "target": "title"},
        {"source": "description", "target": "description"},
        {"source": "price", "target": "price"},
        {"source": "category", "target": "category", "transform": "lowercase"}
    ]
)

# Run the sync
result = linker.sync()
print(f"Synced {result.count} products")
```

## Intermediate Examples

### Scheduled Sync with Error Handling

Set up a scheduled sync with robust error handling:

```python
from apilinker import ApiLinker
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='sync.log'
)
logger = logging.getLogger('api_sync')

# Initialize ApiLinker
linker = ApiLinker()

# Configure APIs and mapping
# ... (configuration as in previous examples)

# Define error handler
def handle_sync_error(error, context):
    logger.error(f"Sync failed: {error}")
    logger.info(f"Context: {context}")
    
    # Send notification (example)
    send_notification(f"API Sync failed: {error}")
    
    # Return True to retry, False to abort
    return True

# Add schedule with error handling
linker.add_schedule(
    interval_minutes=60,
    error_handler=handle_sync_error,
    max_retries=3,
    retry_delay_seconds=300
)

# Start scheduled sync
try:
    logger.info("Starting scheduled sync")
    linker.start_scheduled_sync()
    
    # Keep the script running
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    logger.info("Scheduled sync stopped by user")
```

### Pagination Handling

Handle paginated API responses:

```python
from apilinker import ApiLinker

# Initialize ApiLinker
linker = ApiLinker()

# Configure source API with pagination
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    endpoints={
        "get_orders": {
            "path": "/orders",
            "method": "GET",
            "pagination": {
                "data_path": "data",
                "next_page_path": "meta.next_page",
                "page_param": "page",
                "limit_param": "limit",
                "limit": 100
            }
        }
    }
)

# Fetch all pages automatically
all_orders = linker.fetch("get_orders")
print(f"Retrieved {len(all_orders)} orders across multiple pages")

# Configure target and mapping
# ...

# Sync with automatic pagination
result = linker.sync()
print(f"Synced {result.count} orders")
```

## Advanced Examples

### Custom Data Transformations

Apply complex transformations to your data:

```python
from apilinker import ApiLinker
import datetime

# Initialize ApiLinker
linker = ApiLinker()

# Configure APIs
# ...

# Define custom transformers
def format_date(value, **kwargs):
    """Convert date string to desired format."""
    if not value:
        return None
        
    format_in = kwargs.get("format_in", "%Y-%m-%d")
    format_out = kwargs.get("format_out", "%d/%m/%Y")
    
    try:
        date_obj = datetime.datetime.strptime(value, format_in)
        return date_obj.strftime(format_out)
    except ValueError:
        return value

def combine_fields(value, **kwargs):
    """Combine multiple fields into one."""
    # The current field value is ignored
    # Instead we use the full source record
    source_record = kwargs.get("_source_record", {})
    
    fields = kwargs.get("fields", [])
    separator = kwargs.get("separator", " ")
    
    values = []
    for field in fields:
        field_value = source_record.get(field)
        if field_value:
            values.append(str(field_value))
            
    return separator.join(values)

# Register transformers
linker.mapper.register_transformer("format_date", format_date)
linker.mapper.register_transformer("combine_fields", combine_fields)

# Use transformers in mapping
linker.add_mapping(
    source="get_users",
    target="create_contacts",
    fields=[
        # Format date from YYYY-MM-DD to DD/MM/YYYY
        {
            "source": "birth_date",
            "target": "dateOfBirth",
            "transform": "format_date",
            "format_in": "%Y-%m-%d",
            "format_out": "%d/%m/%Y"
        },
        # Combine first and last name into full name
        {
            "target": "fullName",
            "transform": "combine_fields",
            "fields": ["first_name", "last_name"],
            "separator": " "
        }
    ]
)
```

### Conditional Mapping

Apply mappings based on conditions:

```python
from apilinker import ApiLinker

# Initialize ApiLinker
linker = ApiLinker()

# Configure APIs
# ...

# Add mapping with conditions
linker.add_mapping(
    source="get_orders",
    target="create_order",
    fields=[
        {"source": "id", "target": "external_id"},
        {"source": "customer.name", "target": "customer_name"},
        
        # Only map the shipping address if it exists
        {
            "source": "shipping_address",
            "target": "shipping_details",
            "condition": {
                "field": "shipping_address",
                "operator": "exists"
            }
        },
        
        # Apply different mapping based on status
        {
            "source": "status",
            "target": "status",
            "transform": "map_status",
            "condition": {
                "field": "status",
                "operator": "in",
                "value": ["pending", "processing"]
            }
        },
        
        # Apply a default for completed orders
        {
            "target": "status",
            "value": "fulfilled",
            "condition": {
                "field": "status",
                "operator": "equals",
                "value": "completed"
            }
        }
    ]
)

# Register status mapper
def map_status(value, **kwargs):
    status_map = {
        "pending": "new",
        "processing": "in_progress"
    }
    return status_map.get(value, value)

linker.mapper.register_transformer("map_status", map_status)
```

## Real-world Use Cases

For more detailed real-world examples, see:

- [CRM to Marketing Platform](crm_to_marketing.md)
- [E-commerce Inventory Sync](ecommerce_inventory.md)
- [Weather Data Collection](weather_data.md)
- [GitHub to GitLab Migration](github_to_gitlab.md)

Each example includes full code, configuration files, and explanations.
