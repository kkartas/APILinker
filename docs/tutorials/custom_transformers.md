# Tutorial: Creating Custom Transformers

🟡 **Difficulty: Intermediate**

This tutorial guides you through the process of creating custom transformers to modify data as it's mapped between APIs.

## What You'll Learn

- How to create simple and complex data transformers
- How to register transformers with ApiLinker
- How to use transformers in field mappings
- How to handle transformer parameters and edge cases

## Prerequisites

- Python 3.8 or newer installed
- ApiLinker installed (`pip install apilinker`)
- Basic understanding of Python functions
- Completion of the [API-to-API Sync](api_to_api_sync.md) tutorial

## Step 1: Understanding Transformers

Transformers are functions that modify data during the mapping process. They can:

- Format values (e.g., convert dates, format phone numbers)
- Convert data types (e.g., string to number, array to string)
- Apply business logic (e.g., calculate totals, validate values)

A transformer function must:
1. Accept a value as its first argument
2. Accept arbitrary keyword arguments (**kwargs)
3. Return the transformed value

## Step 2: Create a Simple Transformer

Let's start with a basic transformer that formats a phone number:

```python
from apilinker import ApiLinker

# Initialize ApiLinker
linker = ApiLinker()

# Define a phone number formatter
def format_phone(value, **kwargs):
    """Format a phone number to (XXX) XXX-XXXX format."""
    if not value:  # Handle None/empty values
        return ""
    
    # Remove non-digit characters
    digits = ''.join(c for c in value if c.isdigit())
    
    # Format based on length
    if len(digits) == 10:  # US phone number
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    elif len(digits) > 10:  # International number
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
    else:
        return value  # Return original if not enough digits
    
# Register the transformer with ApiLinker
linker.mapper.register_transformer("format_phone", format_phone)

# Test the transformer
original_phone = "5551234567"
formatted_phone = linker.mapper.transform(original_phone, "format_phone")
print(f"Original: {original_phone}")
print(f"Formatted: {formatted_phone}")
```

## Step 3: Create a Transformer with Parameters

Transformers can accept additional parameters through **kwargs:

```python
# Define a transformer that accepts parameters
def truncate_text(value, **kwargs):
    """Truncate text to a specified length and add ellipsis if needed."""
    if not value or not isinstance(value, str):
        return value
    
    # Get max_length from kwargs with default value of 100
    max_length = kwargs.get("max_length", 100)
    
    # Get ellipsis text with default value of "..."
    ellipsis = kwargs.get("ellipsis", "...")
    
    # Truncate if longer than max_length
    if len(value) > max_length:
        return value[:max_length - len(ellipsis)] + ellipsis
    
    return value

# Register the transformer
linker.mapper.register_transformer("truncate_text", truncate_text)

# Test with different parameters
long_text = "This is a very long text that needs to be truncated to fit within specific limits for display purposes."
print(truncate_text(long_text, max_length=50))  # Default ellipsis
print(truncate_text(long_text, max_length=30, ellipsis=" [more]"))  # Custom ellipsis
```

## Step 4: Create a Class-Based Transformer

For more complex transformers, you can use the TransformerPlugin base class:

```python
from apilinker.core.plugins import TransformerPlugin

class SentimentAnalysisTransformer(TransformerPlugin):
    """A transformer plugin that analyzes text sentiment."""
    
    plugin_name = "sentiment_analysis"
    
    def validate_input(self, value):
        """Validate the input before transformation."""
        return isinstance(value, str)
    
    def transform(self, value, **kwargs):
        """
        Simple sentiment analysis implementation.
        
        Args:
            value: The text to analyze
            **kwargs: Additional parameters
                threshold: Sensitivity threshold (default: 0.1)
                
        Returns:
            dict: Sentiment analysis results
        """
        if not self.validate_input(value) or not value:
            return {"sentiment": "neutral", "score": 0.0}
        
        # Get threshold parameter with default value
        threshold = kwargs.get("threshold", 0.1)
        
        # Define sentiment word lists
        positive_words = ["good", "great", "excellent", "happy", "positive", "like", "love"]
        negative_words = ["bad", "poor", "terrible", "unhappy", "negative", "hate", "dislike"]
        
        # Convert to lowercase for case-insensitive matching
        text = value.lower()
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Calculate sentiment score
        total = positive_count + negative_count
        score = 0.0 if total == 0 else (positive_count - negative_count) / total
        
        # Determine sentiment based on score and threshold
        sentiment = "neutral"
        if score > threshold:
            sentiment = "positive"
        elif score < -threshold:
            sentiment = "negative"
            
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_count": positive_count,
            "negative_count": negative_count
        }

# Register the plugin class
linker.plugin_manager.register_plugin(SentimentAnalysisTransformer)

# Test the sentiment analysis transformer
text1 = "I really love this product, it's excellent and makes me happy!"
text2 = "This is terrible, I hate it and it makes me unhappy."
text3 = "This is a neutral statement without strong sentiment."

# Get the transformer
transformer = linker.plugin_manager.get_transformer("sentiment_analysis")

# Analyze texts
print(f"Text 1: {transformer(text1)}")
print(f"Text 2: {transformer(text2)}")
print(f"Text 3: {transformer(text3)}")
print(f"Text 3 (higher threshold): {transformer(text3, threshold=0.3)}")
```

## Step 5: Using Transformers in Field Mappings

Now, let's use our transformers in field mappings:

```python
# Configure source and target APIs
linker.add_source(
    type="rest",
    base_url="https://api.example.com/v1",
    endpoints={
        "get_customers": {
            "path": "/customers",
            "method": "GET"
        }
    }
)

linker.add_target(
    type="rest",
    base_url="https://api.destination.com/v2",
    endpoints={
        "create_contact": {
            "path": "/contacts",
            "method": "POST"
        }
    }
)

# Define mapping with transformers
linker.add_mapping(
    source="get_customers",
    target="create_contact",
    fields=[
        {"source": "id", "target": "external_id"},
        
        # Use phone formatter
        {"source": "phone", "target": "phoneNumber", "transform": "format_phone"},
        
        # Truncate description
        {
            "source": "description", 
            "target": "bio", 
            "transform": "truncate_text", 
            "max_length": 200,  # Pass parameter to transformer
            "ellipsis": " (continued...)"
        },
        
        # Analyze feedback sentiment
        {
            "source": "feedback", 
            "target": "sentiment_data", 
            "transform": "sentiment_analysis",
            "threshold": 0.2  # Custom threshold
        }
    ]
)
```

## Step 6: Chain Multiple Transformers

You can also chain multiple transformers to apply them in sequence:

```python
# Define a string normalization transformer
def normalize_string(value, **kwargs):
    """Normalize string by removing extra whitespace and converting to lowercase."""
    if not value or not isinstance(value, str):
        return value
    return " ".join(value.split()).lower()

linker.mapper.register_transformer("normalize_string", normalize_string)

# Use chained transformers in a mapping
linker.add_mapping(
    source="get_products",
    target="create_item",
    fields=[
        # Chain transformers - first normalize, then truncate
        {
            "source": "description",
            "target": "short_desc",
            "transform": [
                "normalize_string",  # Applied first
                {
                    "name": "truncate_text",  # Applied second
                    "max_length": 100
                }
            ]
        }
    ]
)
```

## Step 7: Error Handling in Transformers

Good transformers should handle errors gracefully:

```python
def safe_date_converter(value, **kwargs):
    """Convert date strings to a consistent format with error handling."""
    if not value:
        return None
    
    input_format = kwargs.get("input_format", "%Y-%m-%d")
    output_format = kwargs.get("output_format", "%d/%m/%Y")
    
    try:
        from datetime import datetime
        date_obj = datetime.strptime(value, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        # Handle parsing errors
        fallback = kwargs.get("fallback")
        if fallback:
            return fallback
        return value  # Return original if can't convert
    except Exception as e:
        # Log other errors
        print(f"Error in date_converter: {e}")
        return value

linker.mapper.register_transformer("safe_date_converter", safe_date_converter)
```

## Step 8: Testing Your Transformers

Always test your transformers with various inputs including edge cases:

```python
def test_transformers():
    """Test transformers with various inputs."""
    # Test phone formatter
    test_phones = [
        "5551234567",              # Basic US number
        "+15551234567",            # US with country code
        "555-123-4567",            # With dashes
        "(555) 123-4567",          # Already formatted
        "123456",                  # Too short
        None,                      # None
        ""                         # Empty string
    ]
    print("\nTesting phone formatter:")
    for phone in test_phones:
        try:
            result = linker.mapper.transform(phone, "format_phone")
            print(f"  Input: {phone!r} → Output: {result!r}")
        except Exception as e:
            print(f"  Error with {phone!r}: {e}")
    
    # Test truncate_text
    test_texts = [
        "Short text",              # Shorter than limit
        "This is a longer text that should be truncated",  # Longer than default limit
        None,                      # None
        123                        # Non-string
    ]
    print("\nTesting text truncation:")
    for text in test_texts:
        try:
            result = linker.mapper.transform(text, "truncate_text", max_length=20)
            print(f"  Input: {text!r} → Output: {result!r}")
        except Exception as e:
            print(f"  Error with {text!r}: {e}")

# Run transformer tests
test_transformers()
```

## Step 9: Complete Example

Here's a complete script that demonstrates creating and using custom transformers:

```python
from apilinker import ApiLinker
from apilinker.core.plugins import TransformerPlugin

# Initialize ApiLinker
linker = ApiLinker()

# ------ Simple transformers ------

def format_phone(value, **kwargs):
    """Format a phone number to (XXX) XXX-XXXX format."""
    if not value:
        return ""
    
    # Remove non-digit characters
    digits = ''.join(c for c in value if c.isdigit())
    
    # Format based on length
    if len(digits) == 10:  # US phone number
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    elif len(digits) > 10:  # International number
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
    else:
        return value  # Return original if not enough digits

def truncate_text(value, **kwargs):
    """Truncate text to a specified length and add ellipsis if needed."""
    if not value or not isinstance(value, str):
        return value
    
    max_length = kwargs.get("max_length", 100)
    ellipsis = kwargs.get("ellipsis", "...")
    
    if len(value) > max_length:
        return value[:max_length - len(ellipsis)] + ellipsis
    
    return value

def safe_date_converter(value, **kwargs):
    """Convert date strings to a consistent format with error handling."""
    if not value:
        return None
    
    input_format = kwargs.get("input_format", "%Y-%m-%d")
    output_format = kwargs.get("output_format", "%d/%m/%Y")
    
    try:
        from datetime import datetime
        date_obj = datetime.strptime(value, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        fallback = kwargs.get("fallback")
        if fallback:
            return fallback
        return value  # Return original if can't convert
    except Exception as e:
        print(f"Error in date_converter: {e}")
        return value

# ------ Class-based transformer plugin ------

class SentimentAnalysisTransformer(TransformerPlugin):
    """A transformer plugin that analyzes text sentiment."""
    
    plugin_name = "sentiment_analysis"
    
    def validate_input(self, value):
        """Validate the input before transformation."""
        return isinstance(value, str)
    
    def transform(self, value, **kwargs):
        """Simple sentiment analysis implementation."""
        if not self.validate_input(value) or not value:
            return {"sentiment": "neutral", "score": 0.0}
        
        threshold = kwargs.get("threshold", 0.1)
        
        positive_words = ["good", "great", "excellent", "happy", "positive", "like", "love"]
        negative_words = ["bad", "poor", "terrible", "unhappy", "negative", "hate", "dislike"]
        
        text = value.lower()
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total = positive_count + negative_count
        score = 0.0 if total == 0 else (positive_count - negative_count) / total
        
        sentiment = "neutral"
        if score > threshold:
            sentiment = "positive"
        elif score < -threshold:
            sentiment = "negative"
            
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_count": positive_count,
            "negative_count": negative_count
        }

# ------ Register transformers ------

# Register function-based transformers
linker.mapper.register_transformer("format_phone", format_phone)
linker.mapper.register_transformer("truncate_text", truncate_text)
linker.mapper.register_transformer("safe_date_converter", safe_date_converter)

# Register class-based transformer plugin
linker.plugin_manager.register_plugin(SentimentAnalysisTransformer)

# ------ Test the transformers ------

def test_transformers():
    """Test transformers with various inputs."""
    # Test phone formatter
    test_phones = ["5551234567", "+15551234567", "555-123-4567", "(555) 123-4567", "123456", None, ""]
    print("\nTesting phone formatter:")
    for phone in test_phones:
        try:
            result = linker.mapper.transform(phone, "format_phone")
            print(f"  Input: {phone!r} → Output: {result!r}")
        except Exception as e:
            print(f"  Error with {phone!r}: {e}")
    
    # Test date converter
    test_dates = ["2023-01-15", "01/15/2023", "2023-13-01", None, ""]
    print("\nTesting date converter:")
    for date in test_dates:
        try:
            result = linker.mapper.transform(date, "safe_date_converter", 
                                           input_format="%Y-%m-%d", 
                                           fallback="INVALID DATE")
            print(f"  Input: {date!r} → Output: {result!r}")
        except Exception as e:
            print(f"  Error with {date!r}: {e}")
    
    # Test sentiment analysis
    test_texts = [
        "I really love this product, it's excellent and makes me happy!",
        "This is terrible, I hate it and it makes me unhappy.",
        "This is a neutral statement without strong sentiment.",
        None
    ]
    print("\nTesting sentiment analysis:")
    transformer = linker.plugin_manager.get_transformer("sentiment_analysis")
    for text in test_texts:
        try:
            result = transformer(text)
            print(f"  Input: {text!r}")
            print(f"  Output: {result}")
        except Exception as e:
            print(f"  Error with {text!r}: {e}")

# Run transformer tests
test_transformers()
```

## What's Next?

Now that you've learned how to create custom transformers, you can:

1. **Create More Advanced Transformers**:
   - Transform complex data structures
   - Integrate with external libraries (e.g., pandas for data analysis)
   - Access external services within transformers (with caching)

2. **Learn About Error Handling**:
   - Improve error handling in transformers
   - Set up validation to prevent errors

3. **Check Out Other Tutorials**:
   - [Setting Up Scheduled Syncs](scheduled_syncs.md)
   - [Error Handling and Validation](error_handling.md)

## Troubleshooting

### Common Issues and Solutions

- **Function Not Found**: Ensure transformer is registered before use
- **Type Errors**: Add proper type checking in your transformer
- **Parameter Issues**: Verify parameter names in mapping match your function

For more help, check the [FAQ](../faq.md) or [open an issue](https://github.com/kkartas/apilinker/issues) on GitHub.
