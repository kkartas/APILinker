# ApiLinker Architecture

This document explains the architecture and data flow of ApiLinker.

## System Architecture

```
┌──────────────┐    ┌──────────────────────────────────────────────────┐    ┌──────────────┐
│              │    │                    ApiLinker                     │    │              │
│              │    │   ┌─────────────┐          ┌─────────────┐      │    │              │
│    Source    │    │   │    Source   │          │    Target   │      │    │    Target    │
│     API      ├────┼──►│  Connector  ├──────┬──►│  Connector  ├──────┼───►│     API      │
│              │    │   │(ApiConnector)│      │   │(ApiConnector)│      │    │              │
│              │    │   └─────────────┘      │   └─────────────┘      │    │              │
└──────────────┘    │          ▲             │          ▲             │    └──────────────┘
                    │          │             │          │             │
┌──────────────┐    │   ┌─────▼─────┐       │     ┌────▼─────┐       │
│              │    │   │    Auth   │       │     │   Auth   │       │
│ Config File  │    │   │  Manager  │       │     │ Manager  │       │
│  YAML/JSON   ├────┼──►└───────────┘       │     └──────────┘       │
│              │    │                       │                        │
└──────────────┘    │   ┌─────────────┐    │                        │
                    │   │ Field Mapper ├────┘                        │
┌──────────────┐    │   └─────────────┘                              │
│              │    │          ▲                                     │
│  Scheduler   ├────┼─────────┐                                      │
│              │    │   ┌─────▼─────┐                                │
└──────────────┘    │   │   Logger  │                                │
                    │   └───────────┘                                │
                    └──────────────────────────────────────────────────┘

```

### Actual Component Relationships

```
           ┌─────────────┐
           │  ApiLinker  │
           └──────┬──────┘
                  ▼
┌─────────────────────────────────┐
│                                 │
├─────────────┬───────────────────┤
│             │                   │
▼             ▼                   ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ ApiConn. │  │FieldMapper│  │Scheduler │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │            │             │
     ▼            ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│AuthManager│  │Transformers│ │Background│
└──────────┘  └──────────┘  │ Thread   │
                            └──────────┘
```
```

## Data Flow

The flow of data through ApiLinker follows these steps:

1. **Configuration**: The system is configured either programmatically or via YAML/JSON files.

2. **Source Connection**: ApiLinker connects to the source API using the configured connector and authentication.

3. **Data Retrieval**: Data is fetched from the source API, with automatic handling of pagination if configured.

4. **Data Transformation**: The mapper applies field mappings and transformations to convert the data structure from the source format to the target format.

5. **Target Connection**: ApiLinker connects to the target API using the configured connector and authentication.

6. **Data Transmission**: The transformed data is sent to the target API.

7. **Result Processing**: Results are collected and returned to the caller or handled by the error handler.

## Core Components

### 1. ApiLinker

The main class that orchestrates the entire process. It:
- Manages configuration
- Coordinates between components
- Handles synchronization processes
- Provides the public API

### 2. Connectors

Responsible for communication with APIs. They:
- Establish connections
- Send requests
- Handle responses
- Manage pagination
- Handle retries

### 3. Mapper

Manages field mappings and transformations. It:
- Maps fields from source to target format
- Applies transformations
- Handles nested data structures
- Implements conditional mapping

### 4. Transformers

Transform data values during the mapping process. They:
- Convert data formats
- Format values
- Validate data
- Apply business logic

### 5. Auth Plugins

Handle different authentication methods. They:
- Generate authentication tokens
- Format headers and parameters
- Refresh credentials when needed
- Validate auth responses

### 6. Plugin Manager

Discovers and manages plugins. It:
- Loads plugins from different sources
- Registers plugins
- Instantiates plugins
- Provides plugin discovery mechanisms

### 7. Scheduler

Manages periodic execution of synchronization jobs. It:
- Schedules sync operations
- Handles cron expressions and intervals
- Manages execution threads
- Tracks job status

## Visual Representation of the Mapping Process

```
Source Data                  Field Mapping                  Target Data
┌───────────────┐            ┌───────────────┐            ┌───────────────┐
│ {             │            │ fields: [     │            │ {             │
│  "id": 123,   │            │   {           │            │  "external_id": │
│  "name": "John",           │     source: "id",          │     "123",    │
│  "created":   ├───────────►│     target:   ├───────────►│  "fullName":  │
│    "2023-01-01",           │       "external_id"│       │     "JOHN DOE", │
│  "last_name": │            │   },          │            │  "created_at":│
│    "Doe",     │            │   {           │            │     1672531200│
│  "active":    │            │     source:   │            │ }             │
│    true       │            │       "name", │            └───────────────┘
│ }             │            │     target:   │
└───────────────┘            │       "fullName", │
                             │     transform:  │
                             │       "uppercase" │
                             │   },          │
                             │   {           │
                             │     source:   │
                             │       "created", │
                             │     target:   │
                             │       "created_at", │
                             │     transform:  │
                             │       "iso_to_timestamp" │
                             │   }           │
                             │ ]             │
                             └───────────────┘
```

## Plugin System Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                      Plugin Manager                           │
│                                                               │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │
│   │  Plugin Registry │    │  Plugin Loader  │    │  Plugin Validator│   │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘   │
│            │                     │                       │            │
└────────────┼─────────────────────┼───────────────────────┼────────────┘
             │                     │                       │
             ▼                     ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Base Plugin   │    │  Plugin Sources  │    │  Plugin Types   │
│    Interface    │    │                  │    │                 │
└─────────────────┘    │  ┌─────────────┐ │    │ ┌─────────────┐ │
        ▲              │  │ Built-in    │ │    │ │ Transformer │ │
        │              │  │ Plugins     │ │    │ │ Plugins     │ │
┌───────┴───────┐      │  └─────────────┘ │    │ └─────────────┘ │
│               │      │  ┌─────────────┐ │    │ ┌─────────────┐ │
│  Plugin Base  │      │  │ User        │ │    │ │ Connector   │ │
│     Class     │      │  │ Plugins     │ │    │ │ Plugins     │ │
└───────────────┘      │  └─────────────┘ │    │ └─────────────┘ │
        ▲              │  ┌─────────────┐ │    │ ┌─────────────┐ │
        │              │  │ Third-party │ │    │ │ Auth        │ │
┌───────┴───────┐      │  │ Plugins     │ │    │ │ Plugins     │ │
│   Specific    │      │  └─────────────┘ │    │ └─────────────┘ │
│  Plugin Types │      └──────────────────┘    └─────────────────┘
└───────────────┘
```

## Configuration Architecture

```
┌───────────────────────────┐
│     Config Sources        │
│                           │
│  ┌───────────────────┐    │
│  │  YAML/JSON Files  │    │
│  └───────────────────┘    │
│                           │
│  ┌───────────────────┐    │
│  │  API Parameters   │    │
│  └───────────────────┘    │
│                           │
│  ┌───────────────────┐    │
│  │  Environment Vars │    │
│  └───────────────────┘    │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐     ┌───────────────────────┐
│    Config Processor       │     │   Template Engine     │
│                           │     │                       │
│ - Parse config formats    │     │ - Process variables   │
│ - Validate structure      │◄────┤ - Handle expressions  │
│ - Apply defaults          │     │ - Environment lookups │
│ - Normalize values        │     │                       │
└───────────┬───────────────┘     └───────────────────────┘
            │
            ▼
┌───────────────────────────────────────────┐
│              Config Objects               │
│                                           │
│  ┌────────────────┐    ┌────────────────┐ │
│  │  Source Config │    │  Target Config │ │
│  └────────────────┘    └────────────────┘ │
│                                           │
│  ┌────────────────┐    ┌────────────────┐ │
│  │ Mapping Config │    │ Schedule Config│ │
│  └────────────────┘    └────────────────┘ │
└───────────────────────────────────────────┘
```

## Error Handling Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Operation   │     │    Error      │     │  Error Type   │
│   Execution   │────►│   Detection   │────►│ Classification │
└───────┬───────┘     └───────────────┘     └───────┬───────┘
        │                                           │
        │ Success                                   │ Error
        │                                           ▼
        │                                   ┌───────────────┐
        │                                   │  Custom Error │
        │                                   │   Handlers    │
        │                                   └───────┬───────┘
        │                                           │
        │                                           ▼
        │                                   ┌───────────────┐
        │                                   │   Retry       │ Yes
        │                                   │  Decision     │──────┐
        │                                   └───────┬───────┘      │
        │                                           │ No           │
        │                                           ▼              │
        │                                   ┌───────────────┐      │
        │                                   │   Error       │      │
        │                                   │   Reporting   │      │
        │                                   └───────────────┘      │
        ▼                                                          │
┌───────────────┐                                                  │
│   Result      │◄─────────────────────────────────────────────────┘
│   Processing  │
└───────────────┘
```

## Integration with External Systems

ApiLinker can integrate with various external systems:

```
                  ┌───────────────┐
                  │               │
                  │  Data Sources │
                  │               │
                  └───────┬───────┘
                          │
┌───────────────┐  ┌──────▼──────┐  ┌───────────────┐
│               │  │             │  │               │
│  Databases    │◄─┤  ApiLinker  ├─►│  CRM Systems  │
│               │  │             │  │               │
└───────────────┘  └──────┬──────┘  └───────────────┘
                          │
┌───────────────┐  ┌──────▼──────┐  ┌───────────────┐
│               │  │             │  │               │
│ File Systems  │◄─┤  Plugins &  ├─►│  Messaging    │
│               │  │ Extensions  │  │  Systems      │
└───────────────┘  └──────┬──────┘  └───────────────┘
                          │
                  ┌───────▼───────┐
                  │               │
                  │  Analytics &  │
                  │  Reporting    │
                  │               │
                  └───────────────┘
```
