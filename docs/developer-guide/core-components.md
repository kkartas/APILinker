# Core Components

## ApiLinker Class

The `ApiLinker` class is the main orchestrator that coordinates all system components.

```python
class ApiLinker:
    """
    Main orchestrator class for API integration workflows.
    """
    def sync(self) -> SyncResult:
        """Execute synchronization workflow."""
```

It manages:
- Source and target connectors
- Field mapping and transformations
- Error recovery and retry logic
- Scheduling capabilities
- Security and monitoring integration

## ApiConnector Base Class

The `ApiConnector` is the foundation for all API connectors.

- **Consistent Interface**: Uniform methods for all API types.
- **Error Handling**: Built-in retry logic and circuit breakers.
- **Rate Limiting**: Respectful API usage with configurable limits.

## FieldMapper Class

The `FieldMapper` handles advanced data transformation.

- **Nested Mapping**: Support for dot notation (e.g., `user.profile.name`).
- **Transformers**: Built-in and custom transformation functions.
- **Conditional Logic**: Apply mappings based on data values.

## Scheduler Class

The `Scheduler` provides sophisticated automation.

- **Intervals**: Run jobs every X minutes/hours.
- **Cron**: Support for complex cron expressions.
- **Persistence**: Job state tracking and recovery.
