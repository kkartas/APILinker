# Tutorial: Syncing Data Between Two APIs

🟢 **Difficulty: Beginner**

This tutorial guides you through the process of setting up ApiLinker to sync data between two REST APIs.

## What You'll Learn

- How to configure source and target APIs
- How to map fields between different data structures
- How to run a sync operation
- How to handle common scenarios like authentication and pagination

## Prerequisites

- Python 3.8 or newer installed
- ApiLinker installed (`pip install apilinker`)
- Basic understanding of REST APIs
- Access to test APIs (we'll use JSONPlaceholder, a free testing API)

## Step 1: Create a New Python Script

Create a new file named `api_sync.py` and open it in your preferred editor.

## Step 2: Import ApiLinker and Set Up Basic Structure

```python
from apilinker import ApiLinker
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_sync')

# Initialize ApiLinker
linker = ApiLinker()

# We'll add configurations in the next steps
```

## Step 3: Configure Source API

We'll use JSONPlaceholder as our source API to fetch user data:

```python
# Add source API configuration
linker.add_source(
    type="rest",
    base_url="https://jsonplaceholder.typicode.com",
    endpoints={
        "get_users": {
            "path": "/users",
            "method": "GET"
        }
    }
)

logger.info("Source API configured")
```

## Step 4: Configure Target API

For the target, we'll use JSONPlaceholder's posts endpoint (normally, this would be a different API):

```python
# Add target API configuration
linker.add_target(
    type="rest",
    base_url="https://jsonplaceholder.typicode.com",
    endpoints={
        "create_post": {
            "path": "/posts",
            "method": "POST"
        }
    }
)

logger.info("Target API configured")
```

## Step 5: Create Field Mappings

Now, let's define how fields from the source API map to the target API:

```python
# Define field mappings
linker.add_mapping(
    source="get_users",
    target="create_post",
    fields=[
        # Map user ID to the userId field in posts
        {"source": "id", "target": "userId"},
        
        # Use the user's name as the post title
        {"source": "name", "target": "title"},
        
        # Use the user's company catchphrase as the post body
        {"source": "company.catchPhrase", "target": "body"}
    ]
)

logger.info("Field mappings configured")
```

## Step 6: Define Transformers (Optional)

Let's add a simple transformer to format the post title:

```python
# Define a custom transformer function
def format_title(value, **kwargs):
    """Convert the title to a specific format."""
    if not value:
        return "Untitled"
    return f"User Profile: {value}"

# Register the transformer
linker.mapper.register_transformer("format_title", format_title)

# Update the mapping to use the transformer
linker.add_mapping(
    source="get_users",
    target="create_post",
    fields=[
        {"source": "id", "target": "userId"},
        # Apply the transformer to the title
        {"source": "name", "target": "title", "transform": "format_title"},
        {"source": "company.catchPhrase", "target": "body"}
    ],
    # Replace the previous mapping
    replace=True
)

logger.info("Transformers configured")
```

## Step 7: Run a Dry Run First

It's always a good idea to test with a dry run before performing actual API calls:

```python
# Perform a dry run (no actual API calls to the target)
logger.info("Starting dry run...")
dry_run_result = linker.sync(dry_run=True)

# Print preview of the first record
if dry_run_result.preview:
    logger.info(f"Dry run preview of first record: {dry_run_result.preview[0]}")
else:
    logger.info("No records to sync")

logger.info(f"Dry run would sync {dry_run_result.count} records")
```

## Step 8: Run the Actual Sync

If you're satisfied with the dry run results, perform the actual sync:

```python
# Perform the actual sync
logger.info("Starting sync...")
result = linker.sync()

logger.info(f"Sync completed. Synced {result.count} records")
if result.errors:
    logger.warning(f"Encountered {len(result.errors)} errors during sync")
    for error in result.errors[:5]:  # Show first 5 errors
        logger.warning(f"Error: {error}")
```

## Step 9: Complete Script

Here's the complete script:

```python
from apilinker import ApiLinker
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_sync')

# Initialize ApiLinker
linker = ApiLinker()

# Add source API configuration
linker.add_source(
    type="rest",
    base_url="https://jsonplaceholder.typicode.com",
    endpoints={
        "get_users": {
            "path": "/users",
            "method": "GET"
        }
    }
)
logger.info("Source API configured")

# Add target API configuration
linker.add_target(
    type="rest",
    base_url="https://jsonplaceholder.typicode.com",
    endpoints={
        "create_post": {
            "path": "/posts",
            "method": "POST"
        }
    }
)
logger.info("Target API configured")

# Define a custom transformer function
def format_title(value, **kwargs):
    """Convert the title to a specific format."""
    if not value:
        return "Untitled"
    return f"User Profile: {value}"

# Register the transformer
linker.mapper.register_transformer("format_title", format_title)

# Define field mappings
linker.add_mapping(
    source="get_users",
    target="create_post",
    fields=[
        {"source": "id", "target": "userId"},
        # Apply the transformer to the title
        {"source": "name", "target": "title", "transform": "format_title"},
        {"source": "company.catchPhrase", "target": "body"}
    ]
)
logger.info("Field mappings configured")

# Perform a dry run
logger.info("Starting dry run...")
dry_run_result = linker.sync(dry_run=True)

# Print preview of the first record
if dry_run_result.preview:
    logger.info(f"Dry run preview of first record: {dry_run_result.preview[0]}")
else:
    logger.info("No records to sync")

logger.info(f"Dry run would sync {dry_run_result.count} records")

# Ask for confirmation before actual sync
user_input = input("Proceed with actual sync? (yes/no): ")
if user_input.lower() not in ["yes", "y"]:
    logger.info("Sync cancelled by user")
    exit()

# Perform the actual sync
logger.info("Starting sync...")
result = linker.sync()

logger.info(f"Sync completed. Synced {result.count} records")
if result.errors:
    logger.warning(f"Encountered {len(result.errors)} errors during sync")
    for error in result.errors[:5]:  # Show first 5 errors
        logger.warning(f"Error: {error}")
```

## Step 10: Run the Script

Save the script and run it from your terminal:

```bash
python api_sync.py
```

## What's Next?

Now that you've successfully synced data between two APIs, you can:

1. **Explore Advanced Features**:
   - Try pagination for larger datasets
   - Add authentication for secured APIs
   - Set up scheduling for periodic syncs

2. **Try with Your Own APIs**:
   - Replace JSONPlaceholder with your actual APIs
   - Adapt field mappings to your specific data structures

3. **Check Out Other Tutorials**:
   - [Creating Custom Transformers](custom_transformers.md)
   - [Setting Up Scheduled Syncs](scheduled_syncs.md)
   - [Error Handling and Validation](error_handling.md)

## Troubleshooting

### Common Issues and Solutions

- **404 Not Found**: Double-check your API endpoint paths
- **Missing Fields**: Verify field names in your source data
- **Authentication Errors**: Ensure credentials are correct and properly formatted

For more help, check the [FAQ](../faq.md) or [open an issue](https://github.com/kkartas/apilinker/issues) on GitHub.
