# Getting Started with ApiLinker

This guide is designed for Python beginners who want to learn how to connect APIs using ApiLinker.

## Prerequisites

- Python 3.8 or newer installed
- Basic understanding of Python (variables, functions)
- A text editor or IDE (like VS Code, PyCharm, or even Notepad)
- Internet connection

## Installation

First, let's install ApiLinker:

```bash
pip install apilinker
```

## Basic Concepts

Before diving in, here are the key concepts in ApiLinker:

1. **Source** - The API where you get data from
2. **Target** - The API where you send data to
3. **Endpoint** - A specific operation in an API (like "get users" or "create post")
4. **Mapping** - Rules for how data moves from source to target
5. **Transformer** - A function that changes data format during transfer

## Your First ApiLinker Script

Let's build a simple script that gets data from the free JSONPlaceholder API:

```python
# Step 1: Import the library
from apilinker import ApiLinker

# Step 2: Create an ApiLinker instance
linker = ApiLinker()

# Step 3: Configure a source API
linker.add_source(
    type="rest",
    base_url="https://jsonplaceholder.typicode.com",
    endpoints={
        "get_posts": {
            "path": "/posts",
            "method": "GET",
            "params": {"_limit": 5}  # Only get 5 posts
        }
    }
)

# Step 4: Fetch data from the source API
posts = linker.fetch("get_posts")

# Step 5: Print the results
print("Posts retrieved:")
for post in posts:
    print(f"- {post['title']}")
```

Save this as `first_example.py` and run it:

```bash
python first_example.py
```

You should see a list of post titles printed to your console!

## Connecting Two APIs

Now let's connect two APIs to move data from one to another:

```python
from apilinker import ApiLinker

# Create ApiLinker instance
linker = ApiLinker()

# Configure source API (JSONPlaceholder)
linker.add_source(
    type="rest",
    base_url="https://jsonplaceholder.typicode.com",
    endpoints={
        "get_posts": {
            "path": "/posts",
            "method": "GET",
            "params": {"_limit": 3}  # Get 3 posts
        }
    }
)

# Configure target API (also JSONPlaceholder in this demo)
linker.add_target(
    type="rest",
    base_url="https://jsonplaceholder.typicode.com",
    endpoints={
        "create_comment": {
            "path": "/comments",
            "method": "POST"
        }
    }
)

# Create a mapping between source and target
linker.add_mapping(
    source="get_posts",
    target="create_comment",
    fields=[
        # Map the post id to the comment's postId
        {"source": "id", "target": "postId"},
        
        # Create a fixed name
        {"target": "name", "value": "API Connector Test"},
        
        # Map the post title to the comment's email (just for demo purposes)
        {"source": "title", "target": "email"},
        
        # Map the post body to the comment's body
        {"source": "body", "target": "body"}
    ]
)

# Run the sync
result = linker.sync(dry_run=True)  # Use dry_run=True to prevent actual API calls

print(f"Synced {result.count} posts to comments")
print("Preview of the first transformed item:")
print(result.preview[0] if result.preview else "No preview available")
```

Save this as `connecting_apis.py` and run it:

```bash
python connecting_apis.py
```

## Understanding Results

When you run the code above, you'll see:

1. How many records were synced
2. A preview of what the data looks like after transformation

## Next Steps

Now that you've created your first ApiLinker script, you can:

1. **Connect to real APIs** - Replace the example APIs with ones you want to use
2. **Add authentication** - Learn about auth options in the documentation
3. **Create transformers** - Write functions to format data between systems
4. **Set up scheduling** - Make your sync run on a regular schedule

## Common Questions for Beginners

### How do I find API endpoints?

Check the API documentation for the service you're using. They should list available endpoints, required parameters, and authentication methods.

### What if my API requires authentication?

Add it to your source or target configuration:

```python
linker.add_source(
    type="rest",
    base_url="https://api.example.com",
    auth={
        "type": "api_key",
        "header": "X-API-Key",
        "key": "your_api_key_here"  # Better to use environment variables!
    },
    endpoints={
        # Your endpoints here
    }
)
```

### How do I debug issues?

Enable debugging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

linker = ApiLinker(debug=True)
# Rest of your code...
```

### How do I handle pagination?

ApiLinker can handle pagination automatically:

```python
linker.add_source(
    # Other configuration...
    endpoints={
        "get_items": {
            "path": "/items",
            "method": "GET",
            "pagination": {
                "data_path": "data",
                "next_page_path": "meta.next_page",
                "page_param": "page"
            }
        }
    }
)
```

## Getting Help

If you get stuck, here are resources to help:

- **Documentation**: Visit https://apilinker.readthedocs.io
- **Example Code**: Look at the examples in the GitHub repository
- **Issues**: If you find a bug, report it on GitHub Issues

Remember, everyone starts somewhere! API integration gets easier with practice.
