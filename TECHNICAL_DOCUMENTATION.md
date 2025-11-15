# ApiLinker Technical Documentation

**Version 0.4.1** | **For Python Developers** | **Internal Architecture Reference**

This document provides comprehensive technical documentation for Python developers working with or contributing to ApiLinker. It covers internal architecture, extension points, design patterns, and implementation details.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Plugin System Architecture](#plugin-system-architecture)
4. [Research Connectors Implementation](#research-connectors-implementation)
5. [Authentication & Security](#authentication--security)
6. [Error Handling & Recovery](#error-handling--recovery)
7. [Observability & Monitoring](#observability--monitoring)
8. [Data Flow & Processing](#data-flow--processing)
9. [Testing Architecture](#testing-architecture)
10. [Performance Considerations](#performance-considerations)
11. [Extension Points](#extension-points)
12. [Development Workflow](#development-workflow)
13. [Code Organization](#code-organization)

---

## System Architecture

### High-Level Design

ApiLinker follows a **modular, plugin-based architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                            │
│                    (apilinker.cli)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                   Main Orchestrator                         │
│                  (ApiLinker class)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┬───────────────────────┐
    │                 │                 │                       │
┌───▼────┐    ┌──────▼──────┐   ┌─────▼─────┐        ┌──────▼──────┐
│ Source │    │   Field     │   │ Target    │        │  Scheduler  │
│Connecto│    │   Mapper    │   │Connector  │        │             │
│   rs   │    │             │   │    s      │        │             │
└────────┘    └─────────────┘   └───────────┘        └─────────────┘
    │                 │                 │                       │
┌───▼────┐    ┌──────▼──────┐   ┌─────▼─────┐        ┌──────▼──────┐
│Plugin  │    │Transform    │   │Plugin     │        │   Error     │
│System  │    │Pipeline     │   │System     │        │  Handling   │
└────────┘    └─────────────┘   └───────────┘        └─────────────┘
```

### Core Design Patterns

1. **Strategy Pattern**: Different connectors, authenticators, and transformers
2. **Factory Pattern**: Plugin instantiation and connector creation
3. **Observer Pattern**: Event handling and monitoring
4. **Circuit Breaker Pattern**: Error handling and recovery
5. **Template Method Pattern**: Base classes with customizable steps

### Package Structure

```
apilinker/
├── __init__.py                 # Main exports and version
├── api_linker.py              # Main orchestrator class
├── cli.py                     # Command-line interface
├── core/                      # Core system components
│   ├── __init__.py
│   ├── connector.py           # Base connector classes
│   ├── mapper.py              # Field mapping and transformations
│   ├── scheduler.py           # Scheduling and automation
│   ├── auth.py                # Authentication system
│   ├── error_handling.py      # Error handling and recovery
│   ├── logger.py              # Logging system
│   ├── plugins.py             # Plugin base classes
│   ├── security.py            # Security features
│   └── security_integration.py # Security integration layer
├── connectors/                # Connector implementations
│   ├── scientific/            # Research/scientific APIs
│   │   ├── __init__.py
│   │   ├── ncbi.py           # NCBI (PubMed, GenBank)
│   │   ├── arxiv.py          # arXiv preprints
│   │   ├── crossref.py       # CrossRef citations
│   │   ├── semantic_scholar.py # Semantic Scholar
│   │   ├── pubchem.py        # PubChem compounds
│   │   └── orcid.py          # ORCID researcher profiles
│   └── general/               # General purpose APIs
│       ├── __init__.py
│       ├── github.py         # GitHub repositories
│       └── nasa.py           # NASA earth/space data
├── plugins/                   # Built-in plugins
│   ├── __init__.py
│   └── builtin.py            # Default transformers and handlers
└── examples/                  # Usage examples
    ├── custom_plugin.py
    ├── custom_transform.py
    ├── github_to_gitlab.py
    └── comprehensive_research_examples.py
```

---

## Core Components

### 1. ApiLinker Class (`api_linker.py`)

**Main orchestrator** that coordinates all system components.

```python
class ApiLinker:
    """
    Main orchestrator class for API integration workflows.

    Architecture:
    - Manages source and target connectors
    - Coordinates field mapping and transformations
    - Handles error recovery and retry logic
    - Provides scheduling capabilities
    - Integrates security and monitoring
    """

    def __init__(self, config_path=None, log_level="INFO", log_file=None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging(log_level, log_file)
        self.mapper = FieldMapper()
        self.scheduler = None
        self.security = SecurityManager()
        self._source_connectors = {}
        self._target_connectors = {}
        self._error_handler = ErrorHandler()

    def sync(self) -> SyncResult:
        """
        Execute synchronization workflow.

        Internal Flow:
        1. Validate configuration
        2. Initialize connectors
        3. Fetch data from sources
        4. Apply field mappings and transformations
        5. Send data to targets
        6. Handle errors and recovery
        7. Generate metrics and reporting
        """
```

**Key Internal Methods:**

```python
def _execute_sync_workflow(self) -> SyncResult:
    """Internal sync execution with full error handling."""

def _prepare_connectors(self):
    """Initialize and validate all connectors."""

def _process_data_pipeline(self, raw_data) -> List[Dict]:
    """Execute data transformation pipeline."""

def _handle_sync_errors(self, error: Exception) -> bool:
    """Centralized error handling with recovery strategies."""
```

### 2. ApiConnector Base Class (`core/connector.py`)

**Foundation for all API connectors** with extensible architecture.

```python
class ApiConnector:
    """
    Base class for all API connectors.

    Design Philosophy:
    - Consistent interface across all API types
    - Built-in error handling and retry logic
    - Configurable authentication methods
    - Rate limiting and respectful API usage
    - Extensible through inheritance
    """

    def __init__(self, base_url: str, auth: Dict = None,
                 headers: Dict = None, timeout: int = 30,
                 retry_count: int = 3, retry_delay: float = 1.0):

        # Core HTTP client setup
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers=headers or {}
        )

        # Authentication setup
        self.auth_handler = self._setup_authentication(auth)

        # Error handling and retry configuration
        self.retry_config = RetryConfig(
            max_attempts=retry_count,
            base_delay=retry_delay,
            backoff_strategy="exponential"
        )

        # Rate limiting
        self.rate_limiter = RateLimiter()

        # Monitoring and metrics
        self.metrics = ConnectorMetrics()
```

**Key Internal Architecture:**

```python
def _prepare_request(self, endpoint: EndpointConfig, **kwargs) -> httpx.Request:
    """
    Internal request preparation with full pipeline:
    1. URL construction and parameter injection
    2. Authentication header application
    3. Rate limiting checks
    4. Request validation
    """

def _execute_request(self, request: httpx.Request) -> httpx.Response:
    """
    Execute request with comprehensive error handling:
    1. Pre-request hooks
    2. HTTP execution with retries
    3. Response validation
    4. Post-request hooks
    5. Metrics collection
    """

def _handle_response(self, response: httpx.Response) -> Dict:
    """
    Response processing pipeline:
    1. Status code validation
    2. Content type detection
    3. Data parsing (JSON/XML/CSV)
    4. Error extraction
    5. Data normalization
    """
```

### 3. FieldMapper Class (`core/mapper.py`)

**Advanced data transformation engine** with plugin architecture.

```python
class FieldMapper:
    """
    Sophisticated field mapping and transformation system.

    Capabilities:
    - Nested field mapping with dot notation
    - Built-in transformation functions
    - Custom transformer plugins
    - Conditional mappings
    - Data validation and sanitization
    - Performance optimization for large datasets
    """

    def __init__(self):
        self.mappings = []
        self.transformers = self._load_builtin_transformers()
        self.validators = {}
        self.cache = LRUCache(maxsize=1000)

    def add_mapping(self, source_field: str, target_field: str,
                   transformer: str = None, condition: str = None,
                   default_value: Any = None):
        """
        Add field mapping with advanced options.

        Parameters:
        - source_field: Source field path (supports dot notation)
        - target_field: Target field path (supports dot notation)
        - transformer: Transformation function name
        - condition: Conditional mapping expression
        - default_value: Fallback value if source is missing
        """
```

**Internal Transformation Pipeline:**

```python
def _execute_transformation_pipeline(self, data: Dict) -> Dict:
    """
    Execute full transformation pipeline:

    1. Data Validation
       - Schema validation
       - Type checking
       - Required field validation

    2. Field Extraction
       - Nested field access
       - Array/list handling
       - Null value handling

    3. Transformation Application
       - Built-in transformers
       - Custom plugin transformers
       - Chained transformations

    4. Target Field Assignment
       - Nested structure creation
       - Conflict resolution
       - Data type coercion

    5. Validation & Cleanup
       - Target schema validation
       - Data sanitization
       - Performance metrics
    """
```

**Built-in Transformers:**

```python
BUILTIN_TRANSFORMERS = {
    # String transformations
    "lowercase": lambda x: str(x).lower(),
    "uppercase": lambda x: str(x).upper(),
    "trim": lambda x: str(x).strip(),
    "slugify": lambda x: re.sub(r'[^\w\s-]', '', str(x)).strip().lower(),

    # Date/time transformations
    "iso_to_timestamp": lambda x: datetime.fromisoformat(x).timestamp(),
    "timestamp_to_iso": lambda x: datetime.fromtimestamp(x).isoformat(),
    "format_date": lambda x, fmt: datetime.strptime(x, fmt).isoformat(),

    # Numeric transformations
    "to_int": lambda x: int(float(x)),
    "to_float": lambda x: float(x),
    "round": lambda x, decimals=2: round(float(x), decimals),

    # Array/list transformations
    "join": lambda x, sep=",": sep.join(map(str, x)),
    "split": lambda x, sep=",": str(x).split(sep),
    "first": lambda x: x[0] if isinstance(x, (list, tuple)) and len(x) > 0 else None,
    "last": lambda x: x[-1] if isinstance(x, (list, tuple)) and len(x) > 0 else None,

    # JSON transformations
    "json_parse": lambda x: json.loads(x),
    "json_stringify": lambda x: json.dumps(x),

    # Validation transformations
    "email_validate": lambda x: x if re.match(r'^[^@]+@[^@]+\.[^@]+$', x) else None,
    "url_validate": lambda x: x if validators.url(x) else None,
}
```

### 4. Scheduler Class (`core/scheduler.py`)

**Advanced scheduling system** with multiple trigger types.

```python
class Scheduler:
    """
    Sophisticated scheduling system supporting:
    - Interval-based scheduling
    - Cron expressions
    - Event-driven triggers
    - Dependency management
    - Failure handling and recovery
    """

    def __init__(self, timezone: str = "UTC"):
        self.jobs = {}
        self.event_handlers = {}
        self.dependency_graph = DependencyGraph()
        self.timezone = pytz.timezone(timezone)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.is_running = False

    def schedule_interval(self, func: Callable, interval: int,
                         args: tuple = None, kwargs: dict = None,
                         max_retries: int = 3, retry_delay: int = 60) -> str:
        """Schedule function execution at regular intervals."""

    def schedule_cron(self, func: Callable, cron_expression: str,
                     timezone: str = None, **options) -> str:
        """Schedule function using cron expression."""
```

**Internal Job Management:**

```python
class ScheduledJob:
    """
    Internal job representation with comprehensive metadata.
    """

    def __init__(self, job_id: str, func: Callable, trigger: BaseTrigger):
        self.job_id = job_id
        self.func = func
        self.trigger = trigger
        self.created_at = datetime.now()
        self.last_run = None
        self.next_run = trigger.get_next_run_time()
        self.run_count = 0
        self.failure_count = 0
        self.max_retries = 3
        self.state = JobState.SCHEDULED
        self.metadata = {}

    def execute(self) -> JobResult:
        """
        Execute job with comprehensive error handling:
        1. Pre-execution validation
        2. Function execution with timeout
        3. Result capture and validation
        4. Error handling and retry logic
        5. Metrics collection
        6. Next run calculation
        """
```

---

## Plugin System Architecture

### Plugin Base Classes (`core/plugins.py`)

**Extensible plugin architecture** for custom functionality.

```python
class PluginBase:
    """
    Base class for all ApiLinker plugins.

    Plugin Types:
    - ConnectorPlugin: Custom API connectors
    - TransformerPlugin: Data transformation functions
    - AuthPlugin: Authentication methods
    - SchedulerPlugin: Custom scheduling triggers
    - MonitoringPlugin: Metrics and monitoring
    """

    plugin_type: str = "base"
    plugin_name: str = "unknown"
    version: str = "0.4.0"
    author: str = "Unknown"

    @classmethod
    def get_plugin_info(cls) -> Dict[str, Any]:
        """Return plugin metadata for discovery system."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration."""

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
```

**Plugin Discovery and Loading:**

```python
class PluginManager:
    """
    Centralized plugin management system.
    """

    def __init__(self):
        self.loaded_plugins = {}
        self.plugin_registry = {}
        self.plugin_paths = []

    def discover_plugins(self, paths: List[str] = None) -> List[PluginInfo]:
        """
        Discover available plugins:
        1. Scan specified directories
        2. Import plugin modules
        3. Validate plugin classes
        4. Register in plugin registry
        5. Return plugin information
        """

    def load_plugin(self, plugin_name: str, config: Dict = None) -> PluginBase:
        """
        Load and initialize plugin:
        1. Validate plugin exists
        2. Check dependencies
        3. Initialize plugin instance
        4. Register event handlers
        5. Add to loaded plugins
        """

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Safely unload plugin:
        1. Execute cleanup methods
        2. Remove event handlers
        3. Clear references
        4. Update registry
        """
```

### Custom Plugin Development

**Example: Custom Connector Plugin**

```python
from apilinker.core.plugins import ConnectorPlugin
from apilinker.core.connector import ApiConnector

class CustomAPIConnector(ConnectorPlugin, ApiConnector):
    """
    Example custom connector implementation.
    """

    plugin_type = "connector"
    plugin_name = "custom_api"
    version = "1.0.0"
    author = "Developer Name"

    def __init__(self, api_key: str, **kwargs):
        # Initialize base connector
        super().__init__(
            base_url="https://api.custom.com/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            **kwargs
        )

        # Define custom endpoints
        self.endpoints = {
            "list_items": EndpointConfig(
                path="/items",
                method="GET",
                params={"limit": 100}
            ),
            "create_item": EndpointConfig(
                path="/items",
                method="POST"
            )
        }

    def fetch_data(self, endpoint_name: str, **kwargs) -> Dict:
        """Custom data fetching logic."""
        endpoint = self.endpoints[endpoint_name]
        response = self._execute_request(endpoint, **kwargs)
        return self._process_custom_response(response)

    def send_data(self, endpoint_name: str, data: List[Dict], **kwargs) -> bool:
        """Custom data sending logic."""
        endpoint = self.endpoints[endpoint_name]
        for item in data:
            response = self._execute_request(endpoint, json=item, **kwargs)
            if not response.is_success:
                raise ConnectorError(f"Failed to send item: {response.status_code}")
        return True
```

**Example: Custom Transformer Plugin**

```python
from apilinker.core.plugins import TransformerPlugin

class AdvancedTextTransformer(TransformerPlugin):
    """
    Advanced text processing transformer.
    """

    plugin_type = "transformer"
    plugin_name = "advanced_text"
    version = "1.0.0"

    def get_transformers(self) -> Dict[str, Callable]:
        """Return available transformation functions."""
        return {
            "extract_emails": self.extract_emails,
            "sentiment_analysis": self.sentiment_analysis,
            "language_detect": self.detect_language,
            "text_summarize": self.summarize_text,
        }

    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)

    def sentiment_analysis(self, text: str) -> Dict[str, float]:
        """Perform sentiment analysis (requires additional libraries)."""
        # Implementation would use libraries like TextBlob, VADER, etc.
        pass
```

---

## Research Connectors Implementation

### Scientific Connector Architecture

**Specialized connectors** for research APIs with domain-specific optimizations.

```python
class ResearchConnectorBase(ApiConnector):
    """
    Base class for scientific/research API connectors.

    Additional Features:
    - Ethical API usage guidelines
    - Rate limiting for academic APIs
    - Citation metadata extraction
    - Research-specific data parsing
    - Integration with academic authentication systems
    """

    def __init__(self, email: str = None, **kwargs):
        self.researcher_email = email  # Required for many academic APIs
        self.rate_limits = self._get_academic_rate_limits()
        self.citation_parser = CitationParser()
        super().__init__(**kwargs)

    def _get_academic_rate_limits(self) -> Dict[str, int]:
        """Get appropriate rate limits for academic APIs."""
        return {
            "requests_per_second": 1,    # Conservative for academic APIs
            "requests_per_minute": 10,
            "requests_per_hour": 100,
            "burst_requests": 3
        }

    def _prepare_academic_headers(self) -> Dict[str, str]:
        """Prepare headers following academic API best practices."""
        headers = {
            "User-Agent": f"ApiLinker/0.4.0 (mailto:{self.researcher_email})",
            "Accept": "application/json",
        }
        return headers
```

### NCBI Connector Deep Dive (`connectors/scientific/ncbi.py`)

**Comprehensive NCBI E-utilities integration.**

```python
class NCBIConnector(ResearchConnectorBase):
    """
    NCBI E-utilities connector with full API coverage.

    Supported Databases:
    - PubMed (biomedical literature)
    - GenBank (genetic sequences)
    - ClinVar (genetic variants)
    - dbSNP (genetic variations)
    - GEO (gene expression data)
    - SRA (sequence read archive)
    """

    def __init__(self, email: str, api_key: str = None, tool_name: str = "ApiLinker"):
        self.email = email  # Required by NCBI
        self.api_key = api_key  # Optional for higher rate limits
        self.tool_name = tool_name

        # NCBI E-utilities base URL
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

        # Prepare authentication parameters
        auth_params = {
            "email": email,
            "tool": tool_name
        }
        if api_key:
            auth_params["api_key"] = api_key

        super().__init__(
            base_url=base_url,
            email=email,
            headers=self._prepare_academic_headers()
        )

        # Define NCBI endpoints
        self.endpoints = {
            "search": EndpointConfig(
                path="/esearch.fcgi",
                method="GET",
                params={**auth_params, "retmode": "json"}
            ),
            "fetch": EndpointConfig(
                path="/efetch.fcgi",
                method="GET",
                params={**auth_params, "retmode": "xml"}
            ),
            "summary": EndpointConfig(
                path="/esummary.fcgi",
                method="GET",
                params={**auth_params, "retmode": "json"}
            ),
            "link": EndpointConfig(
                path="/elink.fcgi",
                method="GET",
                params={**auth_params, "retmode": "json"}
            )
        }
```

**Advanced NCBI Methods:**

```python
def search_pubmed(self, query: str, max_results: int = 100,
                 date_range: tuple = None, sort_order: str = "relevance") -> Dict:
    """
    Search PubMed with advanced filtering.

    Internal Process:
    1. Query validation and sanitization
    2. Parameter preparation with filters
    3. API request with retry logic
    4. Response parsing and validation
    5. Result post-processing
    """

    # Prepare search parameters
    search_params = {
        "db": "pubmed",
        "term": self._sanitize_query(query),
        "retmax": min(max_results, 10000),  # NCBI limit
        "sort": sort_order
    }

    # Add date filtering if specified
    if date_range:
        start_date, end_date = date_range
        search_params["datetype"] = "pdat"
        search_params["mindate"] = start_date
        search_params["maxdate"] = end_date

    # Execute search and apply backoff on 429 responses
    response = self._execute_with_backoff("search", **search_params)

    # Parse and validate response
    return self._parse_pubmed_search_response(response)

def get_article_summaries(self, pubmed_ids: List[str]) -> Dict:
    """
    Retrieve article summaries with metadata extraction.

    Features:
    - Batch processing for efficiency
    - Citation metadata extraction
    - Author disambiguation
    - Journal impact factor lookup
    - Reference linking
    """

    # Process in batches to respect API limits
    batch_size = 200  # NCBI recommendation
    all_summaries = {}

    for i in range(0, len(pubmed_ids), batch_size):
        batch_ids = pubmed_ids[i:i + batch_size]

        # Execute summary request
        response = self.fetch_data("summary",
                                 db="pubmed",
                                 id=",".join(batch_ids))

        # Parse summaries with metadata extraction
        batch_summaries = self._parse_article_summaries(response)
        all_summaries.update(batch_summaries)

        # Rate limiting between batches
        time.sleep(self.rate_limits["batch_delay"])

    return all_summaries

def _parse_article_summaries(self, response: Dict) -> Dict:
    """
    Advanced article summary parsing with metadata extraction.
    """
    summaries = {}

    for uid, article_data in response.get("result", {}).items():
        if uid == "uids":
            continue

        # Extract comprehensive metadata
        summary = {
            "pmid": uid,
            "title": article_data.get("title", ""),
            "authors": self._parse_authors(article_data.get("authors", [])),
            "journal": {
                "name": article_data.get("source", ""),
                "iso_abbreviation": article_data.get("source_abbrev", ""),
                "issn": article_data.get("issn", ""),
                "volume": article_data.get("volume", ""),
                "issue": article_data.get("issue", ""),
                "pages": article_data.get("pages", "")
            },
            "publication_date": self._parse_publication_date(article_data),
            "doi": article_data.get("elocationid", "").replace("doi: ", ""),
            "abstract": article_data.get("abstract", ""),
            "keywords": self._extract_keywords(article_data),
            "mesh_terms": self._extract_mesh_terms(article_data),
            "citation_count": article_data.get("cited_by_count", 0),
            "full_text_available": self._check_full_text_availability(article_data)
        }

        summaries[uid] = summary

    return summaries
```

### arXiv Connector Deep Dive (`connectors/scientific/arxiv.py`)

**arXiv API connector with XML parsing and category filtering.**

```python
class ArXivConnector(ResearchConnectorBase):
    """
    arXiv API connector with comprehensive search capabilities.

    Features:
    - Subject category filtering
    - Advanced search syntax
    - Bulk download capabilities
    - Citation extraction
    - Author disambiguation
    - Version tracking
    """

    def __init__(self):
        super().__init__(
            base_url="http://export.arxiv.org/api",
            headers={"User-Agent": "ApiLinker/0.4.0"}
        )

        # arXiv subject categories
        self.categories = self._load_arxiv_categories()

        # XML parser for arXiv responses
        self.xml_parser = ArXivXMLParser()

        # Define endpoints
        self.endpoints = {
            "query": EndpointConfig(
                path="/query",
                method="GET",
                params={"sortBy": "relevance", "sortOrder": "descending"}
            )
        }

    def search_papers(self, query: str, max_results: int = 100,
                     categories: List[str] = None,
                     date_range: tuple = None) -> List[Dict]:
        """
        Advanced arXiv paper search with filtering.

        Search Syntax Support:
        - Boolean operators (AND, OR, NOT)
        - Field-specific searches (ti:, au:, abs:, cat:)
        - Wildcard searches
        - Phrase searches with quotes
        """

        # Build search query
        search_query = self._build_arxiv_query(query, categories, date_range)

        # Execute search with pagination
        papers = []
        start_index = 0
        batch_size = min(max_results, 1000)  # arXiv limit per request

        while len(papers) < max_results and start_index < 50000:  # arXiv total limit
            batch_size = min(batch_size, max_results - len(papers))

            # Execute API request
            response = self.fetch_data("query",
                                     search_query=search_query,
                                     start=start_index,
                                     max_results=batch_size)

            # Parse XML response
            batch_papers = self.xml_parser.parse_search_results(response)

            if not batch_papers:
                break  # No more results

            papers.extend(batch_papers)
            start_index += batch_size

            # Rate limiting
            time.sleep(1)  # Be respectful to arXiv servers

        return papers[:max_results]

class ArXivXMLParser:
    """
    Specialized XML parser for arXiv API responses.
    """

    def __init__(self):
        self.namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

    def parse_search_results(self, xml_content: str) -> List[Dict]:
        """
        Parse arXiv XML response into structured data.
        """
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ConnectorError(f"Failed to parse arXiv XML response: {e}")

        papers = []
        entries = root.findall('atom:entry', self.namespaces)

        for entry in entries:
            paper = self._parse_entry(entry)
            papers.append(paper)

        return papers

    def _parse_entry(self, entry) -> Dict:
        """
        Parse individual arXiv entry with comprehensive metadata.
        """
        # Extract basic information
        paper = {
            "id": self._extract_arxiv_id(entry),
            "title": self._clean_text(entry.find('atom:title', self.namespaces).text),
            "summary": self._clean_text(entry.find('atom:summary', self.namespaces).text),
            "authors": self._parse_authors(entry),
            "published_date": self._parse_date(entry.find('atom:published', self.namespaces).text),
            "updated_date": self._parse_date(entry.find('atom:updated', self.namespaces).text),
            "categories": self._parse_categories(entry),
            "doi": self._extract_doi(entry),
            "journal_reference": self._extract_journal_ref(entry),
            "pdf_url": self._extract_pdf_url(entry),
            "abstract_url": self._extract_abstract_url(entry),
            "version": self._extract_version(entry),
            "comment": self._extract_comment(entry)
        }

        return paper
```

---

## Authentication & Security

### Authentication System (`core/auth.py`)

**Multi-method authentication with secure credential management.**

```python
class AuthenticationManager:
    """
    Centralized authentication system supporting multiple methods.

    Supported Methods:
    - API Key (header/query parameter)
    - Bearer Token (JWT/OAuth)
    - Basic Authentication
    - OAuth 2.0 flows
    - Custom authentication schemes
    """

    def __init__(self, credential_store: CredentialStore = None):
        self.credential_store = credential_store or SecureCredentialStore()
        self.auth_handlers = self._load_auth_handlers()
        self.token_cache = TokenCache()

    def authenticate_request(self, request: httpx.Request,
                           auth_config: Dict) -> httpx.Request:
        """
        Apply authentication to HTTP request.

        Process:
        1. Determine authentication method
        2. Retrieve credentials securely
        3. Apply authentication headers/parameters
        4. Handle token refresh if needed
        5. Cache tokens for reuse
        """

        auth_type = auth_config.get("type", "none")
        handler = self.auth_handlers.get(auth_type)

        if not handler:
            raise AuthenticationError(f"Unsupported auth type: {auth_type}")

        return handler.apply_auth(request, auth_config)

class SecureCredentialStore:
    """
    Secure credential storage with encryption.
    """

    def __init__(self, encryption_key: bytes = None):
        self.encryption_key = encryption_key or self._generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.credentials = {}

    def store_credential(self, key: str, value: str,
                        metadata: Dict = None) -> None:
        """
        Store credential with encryption.
        """
        encrypted_value = self.cipher.encrypt(value.encode())
        self.credentials[key] = {
            "value": encrypted_value,
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "last_accessed": None
        }

    def retrieve_credential(self, key: str) -> str:
        """
        Retrieve and decrypt credential.
        """
        if key not in self.credentials:
            raise CredentialError(f"Credential not found: {key}")

        encrypted_value = self.credentials[key]["value"]
        self.credentials[key]["last_accessed"] = datetime.now()

        return self.cipher.decrypt(encrypted_value).decode()

class OAuth2Handler(AuthHandler):
    """
    OAuth 2.0 authentication handler with flow support.
    """

    def __init__(self):
        self.token_endpoint = None
        self.authorization_endpoint = None
        self.client_credentials = {}

    def apply_auth(self, request: httpx.Request, config: Dict) -> httpx.Request:
        """
        Apply OAuth 2.0 authentication.
        """
        # Check for cached valid token
        token = self._get_cached_token(config["client_id"])

        if not token or self._is_token_expired(token):
            # Refresh token or get new one
            token = self._refresh_or_get_token(config)

        # Apply bearer token
        request.headers["Authorization"] = f"Bearer {token['access_token']}"
        return request

    def _refresh_or_get_token(self, config: Dict) -> Dict:
        """
        OAuth token refresh/acquisition logic.
        """
        grant_type = config.get("grant_type", "client_credentials")

        if grant_type == "client_credentials":
            return self._client_credentials_flow(config)
        elif grant_type == "refresh_token":
            return self._refresh_token_flow(config)
        else:
            raise AuthenticationError(f"Unsupported grant type: {grant_type}")
```

### Security Features (`core/security.py`)

**Comprehensive security implementation.**

```python
class SecurityManager:
    """
    Centralized security management system.

    Features:
    - Data anonymization
    - Access control and permissions
    - Audit logging
    - Threat detection
    - Compliance monitoring
    """

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.encryption_manager = EncryptionManager(config.encryption)
        self.access_control = AccessControlManager(config.access_control)
        self.audit_logger = AuditLogger(config.audit)
        self.threat_detector = ThreatDetector(config.threat_detection)

    def secure_request(self, request: httpx.Request,
                      security_context: SecurityContext) -> httpx.Request:
        """
        Apply security measures to outgoing request.
        """
        # Access control check
        if not self.access_control.check_permission(security_context, "api_request"):
            raise SecurityError("Access denied for API request")

        # Custom request encryption is not supported; rely on HTTPS

        # Data anonymization
        if self.config.anonymize_data:
            request = self._anonymize_request_data(request)

        # Audit logging
        self.audit_logger.log_request(request, security_context)

        return request

    def secure_response(self, response: httpx.Response,
                       security_context: SecurityContext) -> httpx.Response:
        """
        Apply security measures to incoming response.
        """
        # Threat detection
        threats = self.threat_detector.analyze_response(response)
        if threats:
            self.audit_logger.log_security_event("threats_detected", threats)
            if self.config.block_threats:
                raise SecurityError(f"Response blocked due to threats: {threats}")

        # Custom response decryption is not supported

        # Audit logging
        self.audit_logger.log_response(response, security_context)

        return response

class EncryptionManager:
    """
    Request/response encryption manager.
    """

    def __init__(self, config: EncryptionConfig):
        self.config = config
        self.cipher = self._initialize_cipher(config.algorithm)

    def encrypt_request(self, request: httpx.Request) -> httpx.Request:
        """
        Encrypt sensitive request data.
        """
        if request.content:
            # Encrypt request body
            encrypted_content = self.cipher.encrypt(request.content)
            request._content = encrypted_content
            request.headers["Content-Encoding"] = "encrypted"
            request.headers["Encryption-Algorithm"] = self.config.algorithm

        # Encrypt sensitive headers
        for header_name in self.config.sensitive_headers:
            if header_name in request.headers:
                encrypted_value = self.cipher.encrypt(
                    request.headers[header_name].encode()
                ).decode()
                request.headers[header_name] = encrypted_value

        return request
```

---

## Error Handling & Recovery

### Error Handling System (`core/error_handling.py`)

**Sophisticated error handling with recovery strategies.**

```python
class ErrorHandler:
    """
    Comprehensive error handling and recovery system.

    Features:
    - Circuit breaker pattern
    - Dead letter queue for failed operations
    - Intelligent retry strategies
    - Error categorization and routing
    - Recovery workflow automation
    - Error analytics and reporting
    """

    def __init__(self, config: ErrorHandlingConfig):
        self.config = config
        self.circuit_breakers = {}
        self.dead_letter_queue = DeadLetterQueue(config.dlq)
        self.retry_strategies = self._load_retry_strategies()
        self.error_categories = ErrorCategorizer()
        self.recovery_workflows = RecoveryWorkflowManager()
        self.metrics = ErrorMetrics()

    def handle_error(self, error: Exception, context: ErrorContext) -> ErrorResult:
        """
        Centralized error handling with intelligent routing.

        Process:
        1. Error categorization and severity assessment
        2. Circuit breaker evaluation
        3. Retry strategy selection
        4. Dead letter queue processing
        5. Recovery workflow execution
        6. Metrics collection and alerting
        """

        # Categorize error
        error_category = self.error_categories.categorize(error)
        severity = self.error_categories.assess_severity(error, context)

        # Update metrics
        self.metrics.record_error(error_category, severity, context)

        # Check circuit breaker
        circuit_breaker = self._get_circuit_breaker(context.service_name)
        if circuit_breaker.is_open():
            return ErrorResult(
                action=ErrorAction.FAIL_FAST,
                reason="Circuit breaker is open",
                next_retry=None
            )

        # Determine retry strategy
        retry_strategy = self._select_retry_strategy(error_category, context)

        if retry_strategy.should_retry(error, context):
            # Record failure and schedule retry
            circuit_breaker.record_failure()
            next_retry = retry_strategy.calculate_next_retry(context.attempt_count)

            return ErrorResult(
                action=ErrorAction.RETRY,
                reason=f"Retrying with {retry_strategy.name} strategy",
                next_retry=next_retry
            )
        else:
            # Send to dead letter queue
            self.dead_letter_queue.add_failed_operation(
                operation=context.operation,
                error=error,
                context=context
            )

            # Trigger recovery workflow if available
            recovery_workflow = self.recovery_workflows.get_workflow(error_category)
            if recovery_workflow:
                recovery_workflow.execute(error, context)

            return ErrorResult(
                action=ErrorAction.FAIL,
                reason="Max retries exceeded, sent to DLQ",
                next_retry=None
            )

class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.
    """

    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise

    def _record_failure(self):
        """Record failure and update circuit breaker state."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0  # Reset success count

        if (self.state == CircuitBreakerState.HALF_OPEN or
            self.failure_count >= self.failure_threshold):
            self.state = CircuitBreakerState.OPEN

    def _record_success(self):
        """Record success and potentially close circuit."""
        self.success_count += 1
        self.failure_count = 0  # Reset failure count

        if (self.state == CircuitBreakerState.HALF_OPEN and
            self.success_count >= self.success_threshold):
            self.state = CircuitBreakerState.CLOSED

class DeadLetterQueue:
    """
    Dead letter queue for failed operations with retry capabilities.
    """

    def __init__(self, config: DLQConfig):
        self.config = config
        self.storage = self._initialize_storage(config.storage_type)
        self.processor = DLQProcessor(config.processing)
        self.metrics = DLQMetrics()

    def add_failed_operation(self, operation: Dict, error: Exception,
                           context: ErrorContext) -> str:
        """
        Add failed operation to dead letter queue.
        """
        dlq_entry = DLQEntry(
            id=str(uuid.uuid4()),
            operation=operation,
            error_details={
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc()
            },
            context=context.to_dict(),
            created_at=datetime.now(),
            retry_count=0,
            next_retry_at=self._calculate_next_retry(),
            status=DLQStatus.PENDING
        )

        self.storage.store(dlq_entry)
        self.metrics.record_dlq_addition(dlq_entry)

        return dlq_entry.id

    def process_queue(self) -> ProcessingResult:
        """
        Process dead letter queue entries.
        """
        entries = self.storage.get_ready_entries()
        results = ProcessingResult()

        for entry in entries:
            try:
                # Attempt to reprocess the failed operation
                result = self.processor.reprocess(entry)

                if result.success:
                    # Move to success state
                    entry.status = DLQStatus.PROCESSED
                    entry.processed_at = datetime.now()
                    results.successful.append(entry)
                else:
                    # Update retry information
                    entry.retry_count += 1
                    entry.last_retry_at = datetime.now()

                    if entry.retry_count >= self.config.max_retries:
                        entry.status = DLQStatus.FAILED
                        results.failed.append(entry)
                    else:
                        entry.next_retry_at = self._calculate_next_retry(entry.retry_count)
                        results.requeued.append(entry)

                self.storage.update(entry)

            except Exception as e:
                logger.error(f"Error processing DLQ entry {entry.id}: {e}")
                results.errors.append((entry, e))

        self.metrics.record_processing_result(results)
        return results
```

---

## Observability & Monitoring

### Observability System (`core/observability.py`)

**Production-grade observability with OpenTelemetry integration.**

#### Architecture

```python
class TelemetryManager:
    """
    OpenTelemetry-based observability system.

    Features:
    - Distributed tracing with correlation IDs
    - Prometheus metrics export
    - Graceful degradation without OpenTelemetry
    - Context managers for automatic instrumentation
    - Custom metric recording
    - Console export for debugging
    """

    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.tracer = None
        self.meter = None

        if config.enabled and OPENTELEMETRY_AVAILABLE:
            self._initialize_opentelemetry()

    def _initialize_opentelemetry(self):
        """Initialize OpenTelemetry SDK with TracerProvider and MeterProvider."""
        # Set up TracerProvider
        resource = Resource(attributes={"service.name": self.config.service_name})
        provider = TracerProvider(resource=resource)

        # Configure exporters
        if self.config.export_to_console:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)

        # Set up MeterProvider for Prometheus
        if self.config.export_to_prometheus:
            metric_reader = PrometheusMetricReader()
            meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)

            # Start Prometheus HTTP server
            start_http_server(port=self.config.prometheus_port)

        self.meter = metrics.get_meter(__name__)
        self._create_metrics()
```

#### Distributed Tracing

**Trace Context Managers:**

```python
@contextmanager
def trace_sync(self, source_endpoint: str, target_endpoint: str, correlation_id: str):
    """
    Trace a complete sync operation.

    Creates a span with:
    - correlation_id
    - source_endpoint
    - target_endpoint
    - success/failure status
    - error details (if applicable)
    """
    if not self.tracer:
        yield
        return

    with self.tracer.start_as_current_span(
        "sync_operation",
        attributes={
            "correlation_id": correlation_id,
            "source_endpoint": source_endpoint,
            "target_endpoint": target_endpoint,
        },
    ) as span:
        try:
            yield span
            span.set_attribute("success", True)
        except Exception as e:
            span.set_attribute("success", False)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise
```

**Instrumentation Points:**

1. **Sync Operations** (`ApiLinker.sync()`)
   - Trace entire sync pipeline
   - Record duration, success/failure, item count
   - Capture correlation ID for distributed tracing

2. **API Calls** (Future enhancement)
   - Trace individual fetch/send operations
   - Record HTTP method, endpoint, status code
   - Track API latency and errors

3. **Transformations** (Future enhancement)
   - Trace field mapping operations
   - Record transformation type and duration
   - Capture validation errors

#### Prometheus Metrics

**Counter Metrics:**

```python
# Total sync operations
self.sync_counter = self.meter.create_counter(
    name="apilinker.sync.count",
    description="Total number of sync operations",
    unit="1",
)

# Total API calls
self.api_call_counter = self.meter.create_counter(
    name="apilinker.api_call.count",
    description="Total number of API calls",
    unit="1",
)

# Total errors
self.error_counter = self.meter.create_counter(
    name="apilinker.error.count",
    description="Total number of errors",
    unit="1",
)
```

**Histogram Metrics:**

```python
# Sync operation duration
self.sync_duration_histogram = self.meter.create_histogram(
    name="apilinker.sync.duration",
    description="Duration of sync operations",
    unit="ms",
)

# API call duration
self.api_call_duration_histogram = self.meter.create_histogram(
    name="apilinker.api_call.duration",
    description="Duration of API calls",
    unit="ms",
)
```

**Metric Labels:**

- `source_endpoint`: Source API endpoint
- `target_endpoint`: Target API endpoint
- `success`: Operation outcome (true/false)
- `operation_type`: Type of operation (fetch/send/transform)
- `error_category`: Error category (NETWORK, VALIDATION, etc.)

#### Configuration

```python
@dataclass
class ObservabilityConfig:
    """Configuration for observability features."""
    enabled: bool = True
    service_name: str = "apilinker"
    enable_tracing: bool = True
    enable_metrics: bool = True
    export_to_console: bool = False
    export_to_prometheus: bool = False
    prometheus_host: str = "0.0.0.0"
    prometheus_port: int = 9090
```

**YAML Configuration:**

```yaml
observability:
  enabled: true
  service_name: "apilinker-production"
  enable_tracing: true
  enable_metrics: true
  export_to_console: false
  export_to_prometheus: true
  prometheus_host: "0.0.0.0"
  prometheus_port: 9090
```

#### Graceful Degradation

**Handling Missing OpenTelemetry:**

```python
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger.warning(
        "OpenTelemetry not available. Install with: "
        "pip install opentelemetry-api opentelemetry-sdk"
    )
```

**No-Op Pattern:**

When OpenTelemetry is not installed:
- All trace context managers become no-ops
- Metric recording becomes no-ops
- Application continues normally
- No performance impact

#### Integration with ApiLinker

**Initialization:**

```python
class ApiLinker:
    def __init__(self, ..., observability_config: Optional[Dict[str, Any]] = None):
        # Initialize observability
        self.telemetry = self._initialize_observability(observability_config)

    def _initialize_observability(self, config: Optional[Dict[str, Any]]) -> TelemetryManager:
        """Initialize observability system."""
        if not config:
            config = {}

        obs_config = ObservabilityConfig(
            enabled=config.get("enabled", True),
            service_name=config.get("service_name", "apilinker"),
            enable_tracing=config.get("enable_tracing", True),
            enable_metrics=config.get("enable_metrics", True),
            export_to_console=config.get("export_to_console", False),
            export_to_prometheus=config.get("export_to_prometheus", False),
            prometheus_host=config.get("prometheus_host", "0.0.0.0"),
            prometheus_port=config.get("prometheus_port", 9090),
        )

        return TelemetryManager(obs_config)
```

**Sync Instrumentation:**

```python
def sync(self, source_endpoint: str, target_endpoint: str, ...) -> SyncResult:
    """Execute sync with distributed tracing."""
    correlation_id = str(uuid.uuid4())
    start_time = time.time()

    # Wrap entire sync in trace span
    with self.telemetry.trace_sync(source_endpoint, target_endpoint, correlation_id):
        try:
            # ... sync logic ...

            # Record success metrics
            self.telemetry.record_sync_completion(
                source_endpoint, target_endpoint, True, sync_result.count
            )

            return sync_result

        except Exception as e:
            # Record error metrics
            self.telemetry.record_sync_completion(
                source_endpoint, target_endpoint, False, 0
            )
            self.telemetry.record_error(
                error.error_category.value, "sync", error.message
            )
            raise
```

#### Monitoring Best Practices

**1. Metrics to Monitor:**

- **Success Rate:** `rate(apilinker_sync_count{success="true"}[5m])`
- **Latency P95:** `histogram_quantile(0.95, apilinker_sync_duration_bucket)`
- **Error Rate:** `rate(apilinker_error_count[5m])`
- **Throughput:** `rate(apilinker_sync_count[5m])`

**2. Alerting Rules:**

```yaml
groups:
  - name: apilinker_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(apilinker_error_count[5m]) > 0.1
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, apilinker_sync_duration_bucket) > 5000
        annotations:
          summary: "High sync latency detected (>5s)"

      - alert: LowSuccessRate
        expr: rate(apilinker_sync_count{success="true"}[5m]) < 0.9
        annotations:
          summary: "Low sync success rate (<90%)"
```

**3. Grafana Dashboards:**

- **Overview Panel:** Success rate, total syncs, error count
- **Latency Panel:** P50, P95, P99 sync duration
- **Error Analysis:** Errors by category and endpoint
- **Throughput:** Syncs per second by endpoint

#### Performance Impact

**Benchmarks:**

- **Disabled:** 0% overhead (feature flag check only)
- **No OpenTelemetry:** <0.1% overhead (no-op calls)
- **Console Export:** ~0.5% overhead (synchronous logging)
- **Prometheus Export:** <1% overhead (in-memory aggregation)

**Memory Usage:**

- **Base:** ~1KB (configuration)
- **OpenTelemetry SDK:** ~5-10MB
- **Prometheus Exporter:** ~2-5MB (metric buffers)

**Network Impact:**

- Prometheus uses HTTP pull model (no outbound traffic)
- Metrics endpoint responds in <10ms
- No impact on sync operation latency

#### Testing

**Test Coverage:**

- Configuration validation
- TelemetryManager initialization (with/without OpenTelemetry)
- Trace context managers
- Metric recording
- Graceful degradation
- Integration with ApiLinker.sync()

**Test File:** `tests/test_observability.py` (22 tests, 14 passed, 8 skipped)

**Example Test:**

```python
def test_trace_sync_disabled():
    """Test trace_sync when observability is disabled."""
    config = ObservabilityConfig(enabled=False)
    manager = TelemetryManager(config)

    with manager.trace_sync("source", "target", "correlation-123") as span:
        assert span is None  # No-op
```

#### Future Enhancements

1. **Jaeger Export:** Distributed tracing export to Jaeger
2. **Custom Metrics:** User-defined metrics via plugin system
3. **Sampling:** Configurable trace sampling for high-volume systems
4. **Log Correlation:** Automatic trace context injection into logs
5. **Connector Instrumentation:** Trace individual API calls
6. **Mapper Tracing:** Trace data transformation operations
7. **Span Events:** Record detailed events within traces
8. **Baggage Propagation:** Pass context across service boundaries

---

## Data Flow & Processing

### Data Processing Pipeline

**Comprehensive data flow through the system.**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Source API    │────│  Raw Data Fetch  │────│ Data Validation │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┘
│   Target API    │────│  Data Delivery   │────│ Field Mapping   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┘
│  Error Handler  │────│ Transformation  │────│  Data Transform │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Internal Data Structures

**Key data structures used throughout the system.**

```python
@dataclass
class SyncResult:
    """
    Result object for synchronization operations.
    """
    success: bool
    records_processed: int
    records_failed: int
    duration_ms: float
    errors: List[Exception]
    metrics: Dict[str, Any]
    warnings: List[str]

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        total = self.records_processed + self.records_failed
        return (self.records_processed / total * 100) if total > 0 else 0

@dataclass
class EndpointConfig:
    """
    Configuration for API endpoints.
    """
    path: str
    method: str = "GET"
    params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    pagination: PaginationConfig = None
    rate_limit: RateLimitConfig = None
    timeout: int = 30

    def build_url(self, base_url: str, **kwargs) -> str:
        """Build complete URL with parameter substitution."""
        url = urljoin(base_url, self.path)

        # Parameter substitution
        for key, value in kwargs.items():
            url = url.replace(f"{{{key}}}", str(value))

        return url

@dataclass
class ErrorContext:
    """
    Context information for error handling.
    """
    operation: str
    service_name: str
    endpoint: str
    attempt_count: int
    start_time: datetime
    user_context: Dict[str, Any]
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

class DataProcessor:
    """
    Central data processing engine.
    """

    def __init__(self, mapper: FieldMapper, validators: List[Validator] = None):
        self.mapper = mapper
        self.validators = validators or []
        self.processors = self._load_data_processors()

    def process_data_batch(self, raw_data: List[Dict],
                          processing_config: ProcessingConfig) -> ProcessingResult:
        """
        Process batch of data through full pipeline.

        Pipeline Stages:
        1. Input Validation
        2. Data Preprocessing
        3. Field Mapping
        4. Data Transformation
        5. Output Validation
        6. Post-processing
        """

        result = ProcessingResult()

        for record in raw_data:
            try:
                # Stage 1: Input Validation
                validation_result = self._validate_input(record)
                if not validation_result.valid:
                    result.add_validation_error(record, validation_result.errors)
                    continue

                # Stage 2: Data Preprocessing
                preprocessed = self._preprocess_record(record, processing_config)

                # Stage 3: Field Mapping
                mapped = self.mapper.map_fields(preprocessed)

                # Stage 4: Data Transformation
                transformed = self._apply_transformations(mapped, processing_config)

                # Stage 5: Output Validation
                output_validation = self._validate_output(transformed)
                if not output_validation.valid:
                    result.add_validation_error(transformed, output_validation.errors)
                    continue

                # Stage 6: Post-processing
                final_record = self._postprocess_record(transformed, processing_config)

                result.add_success(final_record)

            except Exception as e:
                result.add_error(record, e)

        return result
```

---

## Testing Architecture

### Test Organization

**Comprehensive testing strategy with multiple layers.**

```
tests/
├── unit/                      # Unit tests for individual components
│   ├── test_connectors.py     # Connector unit tests
│   ├── test_mapper.py         # Field mapping tests
│   ├── test_auth.py           # Authentication tests
│   ├── test_plugins.py        # Plugin system tests
│   └── test_error_handling.py # Error handling tests
├── integration/               # Integration tests
│   ├── test_api_workflows.py  # End-to-end workflows
│   ├── test_connector_integration.py # Real API integration
│   └── test_security_integration.py  # Security feature tests
├── performance/               # Performance and load tests
│   ├── test_throughput.py     # Data throughput tests
│   ├── test_memory_usage.py   # Memory usage profiling
│   └── test_concurrent_access.py # Concurrency tests
└── fixtures/                  # Test data and fixtures
    ├── mock_responses/        # Mock API responses
    ├── test_configs/          # Test configurations
    └── sample_data/           # Sample datasets
```

### Testing Utilities

**Advanced testing utilities and fixtures.**

```python
class MockAPIServer:
    """
    Sophisticated mock API server for testing.
    """

    def __init__(self, port: int = 8000):
        self.port = port
        self.app = FastAPI()
        self.responses = {}
        self.request_history = []
        self.delay_config = {}
        self.error_config = {}

    def setup_endpoint(self, path: str, method: str,
                      response_data: Dict, status_code: int = 200,
                      delay: float = 0, error_rate: float = 0):
        """
        Configure mock endpoint with sophisticated behavior.
        """
        async def endpoint_handler(request: Request):
            # Record request for verification
            self.request_history.append({
                "path": path,
                "method": method,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
                "timestamp": datetime.now()
            })

            # Simulate delay if configured
            if delay > 0:
                await asyncio.sleep(delay)

            # Simulate errors if configured
            if error_rate > 0 and random.random() < error_rate:
                raise HTTPException(status_code=500, detail="Simulated server error")

            return response_data

        # Register endpoint
        if method.upper() == "GET":
            self.app.get(path)(endpoint_handler)
        elif method.upper() == "POST":
            self.app.post(path)(endpoint_handler)
        # ... other HTTP methods

@pytest.fixture
def mock_ncbi_server():
    """
    Mock NCBI server with realistic responses.
    """
    server = MockAPIServer()

    # Setup PubMed search endpoint
    server.setup_endpoint(
        "/esearch.fcgi",
        "GET",
        {
            "esearchresult": {
                "count": "1000",
                "retmax": "20",
                "retstart": "0",
                "idlist": ["12345678", "87654321", "11111111"]
            }
        }
    )

    # Setup article summary endpoint
    server.setup_endpoint(
        "/esummary.fcgi",
        "GET",
        load_fixture("ncbi_summary_response.json")
    )

    return server

class APITestCase:
    """
    Base test case class with common testing utilities.
    """

    def setup_method(self):
        """Setup for each test method."""
        self.mock_server = MockAPIServer()
        self.test_config = self.load_test_config()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup after each test method."""
        self.mock_server.cleanup()
        shutil.rmtree(self.temp_dir)

    def assert_api_call_made(self, endpoint: str, method: str = "GET",
                           params: Dict = None):
        """Assert that a specific API call was made."""
        matching_calls = [
            call for call in self.mock_server.request_history
            if call["path"] == endpoint and call["method"] == method
        ]

        assert len(matching_calls) > 0, f"No API call made to {method} {endpoint}"

        if params:
            for call in matching_calls:
                if all(call["query_params"].get(k) == v for k, v in params.items()):
                    return  # Found matching call

            assert False, f"No API call found with parameters {params}"

    def load_fixture(self, filename: str) -> Dict:
        """Load test fixture data."""
        fixture_path = Path(__file__).parent / "fixtures" / filename
        with open(fixture_path) as f:
            return json.load(f)
```

### Performance Testing

**Performance benchmarking and profiling.**

```python
class PerformanceTestSuite:
    """
    Comprehensive performance testing suite.
    """

    def test_throughput_benchmark(self):
        """
        Benchmark data throughput across different scenarios.
        """
        scenarios = [
            {"name": "small_records", "record_count": 100, "record_size": "1KB"},
            {"name": "medium_records", "record_count": 1000, "record_size": "10KB"},
            {"name": "large_records", "record_count": 10000, "record_size": "100KB"},
        ]

        results = {}

        for scenario in scenarios:
            # Generate test data
            test_data = self.generate_test_data(
                count=scenario["record_count"],
                size=scenario["record_size"]
            )

            # Run benchmark
            start_time = time.time()
            linker = ApiLinker()
            result = linker.process_data_batch(test_data)
            duration = time.time() - start_time

            # Calculate metrics
            throughput = len(test_data) / duration  # records per second
            data_rate = sum(len(json.dumps(record)) for record in test_data) / duration  # bytes per second

            results[scenario["name"]] = {
                "throughput_rps": throughput,
                "data_rate_bps": data_rate,
                "duration_seconds": duration,
                "memory_peak_mb": self.measure_peak_memory()
            }

        # Assert performance requirements
        assert results["small_records"]["throughput_rps"] > 100
        assert results["medium_records"]["throughput_rps"] > 50
        assert results["large_records"]["throughput_rps"] > 10

    def test_memory_usage_profiling(self):
        """
        Profile memory usage during various operations.
        """
        import tracemalloc

        tracemalloc.start()

        # Test scenarios
        scenarios = [
            self.test_large_dataset_processing,
            self.test_concurrent_connections,
            self.test_long_running_sync
        ]

        memory_profiles = {}

        for scenario in scenarios:
            # Reset memory tracking
            tracemalloc.clear_traces()

            # Run scenario
            scenario()

            # Get memory snapshot
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            memory_profiles[scenario.__name__] = {
                "peak_memory_mb": sum(stat.size for stat in top_stats) / 1024 / 1024,
                "allocation_count": len(top_stats),
                "top_allocations": [
                    {"file": stat.traceback.format()[0], "size_mb": stat.size / 1024 / 1024}
                    for stat in top_stats[:10]
                ]
            }

        tracemalloc.stop()

        # Verify no memory leaks
        for profile_name, profile_data in memory_profiles.items():
            assert profile_data["peak_memory_mb"] < 500, f"Memory usage too high in {profile_name}"
```

---

## Performance Considerations

### Optimization Strategies

**Performance optimization techniques implemented throughout the system.**

```python
class PerformanceOptimizer:
    """
    Performance optimization manager.
    """

    def __init__(self):
        self.connection_pool = ConnectionPoolManager()
        self.cache_manager = CacheManager()
        self.batch_processor = BatchProcessor()
        self.compression_manager = CompressionManager()

    def optimize_api_requests(self, connector: ApiConnector):
        """
        Optimize API request performance.
        """
        # Connection pooling
        connector.client = self.connection_pool.get_optimized_client(
            base_url=connector.base_url,
            max_connections=20,
            max_keepalive=100
        )

        # Request batching where supported
        if hasattr(connector, 'supports_batch_requests'):
            connector.batch_processor = self.batch_processor

        # Response compression
        connector.client.headers.update({
            "Accept-Encoding": "gzip, deflate, br"
        })

    def optimize_data_processing(self, mapper: FieldMapper):
        """
        Optimize data processing performance.
        """
        # Enable caching for expensive transformations
        mapper.enable_transformation_cache(
            max_size=10000,
            ttl_seconds=3600
        )

        # Compile regex patterns for reuse
        mapper.compile_transformation_patterns()

        # Enable parallel processing for large datasets
        mapper.enable_parallel_processing(
            chunk_size=1000,
            max_workers=min(4, os.cpu_count())
        )

class CacheManager:
    """
    Intelligent caching system for performance optimization.
    """

    def __init__(self):
        self.memory_cache = TTLCache(maxsize=10000, ttl=3600)
        self.disk_cache = DiskCache("cache", size_limit=1024*1024*100)  # 100MB
        self.distributed_cache = None  # Redis, Memcached, etc.

    def get_cached_response(self, cache_key: str,
                           cache_levels: List[str] = None) -> Optional[Any]:
        """
        Multi-level cache retrieval.
        """
        cache_levels = cache_levels or ["memory", "disk"]

        # Try memory cache first
        if "memory" in cache_levels:
            result = self.memory_cache.get(cache_key)
            if result is not None:
                return result

        # Try disk cache
        if "disk" in cache_levels:
            result = self.disk_cache.get(cache_key)
            if result is not None:
                # Promote to memory cache
                self.memory_cache[cache_key] = result
                return result

        # Try distributed cache
        if "distributed" in cache_levels and self.distributed_cache:
            result = self.distributed_cache.get(cache_key)
            if result is not None:
                # Promote to local caches
                self.memory_cache[cache_key] = result
                self.disk_cache[cache_key] = result
                return result

        return None

    def cache_response(self, cache_key: str, data: Any,
                      cache_levels: List[str] = None,
                      ttl: int = 3600):
        """
        Multi-level cache storage.
        """
        cache_levels = cache_levels or ["memory", "disk"]

        if "memory" in cache_levels:
            self.memory_cache[cache_key] = data

        if "disk" in cache_levels:
            self.disk_cache[cache_key] = data

        if "distributed" in cache_levels and self.distributed_cache:
            self.distributed_cache.set(cache_key, data, ttl=ttl)

class BatchProcessor:
    """
    Batch processing optimization for API operations.
    """

    def __init__(self, default_batch_size: int = 100):
        self.default_batch_size = default_batch_size
        self.batch_strategies = {}

    def process_in_batches(self, items: List[Any],
                          processor_func: Callable,
                          batch_size: int = None,
                          parallel: bool = True) -> List[Any]:
        """
        Process items in optimized batches.
        """
        batch_size = batch_size or self.default_batch_size
        results = []

        # Split into batches
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

        if parallel and len(batches) > 1:
            # Parallel batch processing
            with ThreadPoolExecutor(max_workers=min(4, len(batches))) as executor:
                futures = [executor.submit(processor_func, batch) for batch in batches]

                for future in as_completed(futures):
                    batch_result = future.result()
                    results.extend(batch_result)
        else:
            # Sequential batch processing
            for batch in batches:
                batch_result = processor_func(batch)
                results.extend(batch_result)

        return results
```

### Memory Management

**Memory optimization and leak prevention.**

```python
class MemoryManager:
    """
    Memory management and optimization system.
    """

    def __init__(self):
        self.memory_tracker = MemoryTracker()
        self.gc_optimizer = GCOptimizer()
        self.object_pool = ObjectPool()

    def monitor_memory_usage(self, func: Callable) -> Callable:
        """
        Decorator to monitor memory usage of functions.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Record memory before execution
            mem_before = self.memory_tracker.get_current_usage()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Record memory after execution
                mem_after = self.memory_tracker.get_current_usage()
                mem_delta = mem_after - mem_before

                # Log significant memory changes
                if mem_delta > 10 * 1024 * 1024:  # 10MB threshold
                    logger.warning(f"High memory usage in {func.__name__}: {mem_delta / 1024 / 1024:.1f}MB")

                # Trigger garbage collection if needed
                if mem_after > self.memory_tracker.high_water_mark:
                    self.gc_optimizer.optimize_gc()

        return wrapper

    def create_memory_efficient_processor(self, large_dataset: List[Dict]) -> Iterator[Dict]:
        """
        Create memory-efficient processor for large datasets.
        """
        # Use generator to process items lazily
        for item in large_dataset:
            # Process item
            processed_item = self._process_item(item)

            # Yield result immediately
            yield processed_item

            # Clear references to help GC
            del item, processed_item

            # Periodic garbage collection
            if self.memory_tracker.should_gc():
                gc.collect()

class ObjectPool:
    """
    Object pooling for frequently created/destroyed objects.
    """

    def __init__(self):
        self.pools = defaultdict(list)
        self.factory_functions = {}
        self.max_pool_size = 100

    def register_pooled_type(self, obj_type: Type, factory_func: Callable):
        """
        Register object type for pooling.
        """
        self.factory_functions[obj_type] = factory_func

    def get_object(self, obj_type: Type, *args, **kwargs):
        """
        Get object from pool or create new one.
        """
        pool = self.pools[obj_type]

        if pool:
            # Reuse existing object
            obj = pool.pop()
            if hasattr(obj, 'reset'):
                obj.reset(*args, **kwargs)
            return obj
        else:
            # Create new object
            factory = self.factory_functions.get(obj_type)
            if factory:
                return factory(*args, **kwargs)
            else:
                return obj_type(*args, **kwargs)

    def return_object(self, obj):
        """
        Return object to pool for reuse.
        """
        obj_type = type(obj)
        pool = self.pools[obj_type]

        if len(pool) < self.max_pool_size:
            # Clean object before returning to pool
            if hasattr(obj, 'cleanup'):
                obj.cleanup()
            pool.append(obj)
```

---

## Extension Points

### Creating Custom Components

**Guide for extending ApiLinker with custom components.**

#### Custom Connector Development

```python
from apilinker.core.connector import ApiConnector
from apilinker.core.plugins import ConnectorPlugin

class CustomConnector(ConnectorPlugin, ApiConnector):
    """
    Template for custom connector development.
    """

    # Plugin metadata
    plugin_name = "custom_connector"
    plugin_type = "connector"
    version = "1.0.0"
    author = "Your Name"

    def __init__(self, api_key: str, base_url: str, **kwargs):
        """
        Initialize custom connector.

        Best Practices:
        - Validate required parameters
        - Set up appropriate headers and authentication
        - Define endpoint configurations
        - Handle HTTP 429 with exponential backoff
        - Set up error handling
        """

        # Validate required parameters
        if not api_key:
            raise ValueError("API key is required")

        # Call parent constructor
        super().__init__(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": f"ApiLinker/0.4.0 CustomConnector/1.0.0"
            },
            **kwargs
        )

        # Define endpoints specific to your API
        self.endpoints = {
            "list_items": EndpointConfig(
                path="/api/v1/items",
                method="GET",
                params={"per_page": 100}
            ),
            "get_item": EndpointConfig(
                path="/api/v1/items/{item_id}",
                method="GET"
            ),
            "create_item": EndpointConfig(
                path="/api/v1/items",
                method="POST"
            ),
            "update_item": EndpointConfig(
                path="/api/v1/items/{item_id}",
                method="PUT"
            ),
            "delete_item": EndpointConfig(
                path="/api/v1/items/{item_id}",
                method="DELETE"
            )
        }

        # Example: implement application-level backoff for 429 responses instead of client-side rate limiter

    def fetch_data(self, endpoint_name: str, **kwargs) -> Dict:
        """
        Fetch data from the API.

        Implementation Guidelines:
        - Use the endpoint configurations
        - Handle pagination appropriately
        - Implement proper error handling
        - Return normalized data structure
        """

        if endpoint_name not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")

        endpoint = self.endpoints[endpoint_name]

        # Handle pagination for list endpoints
        if endpoint_name == "list_items":
            return self._fetch_paginated_data(endpoint, **kwargs)
        else:
            return self._fetch_single_item(endpoint, **kwargs)

    def send_data(self, endpoint_name: str, data: List[Dict], **kwargs) -> bool:
        """
        Send data to the API.

        Implementation Guidelines:
        - Handle batch operations efficiently
        - Implement proper error handling
        - Return success/failure status
        - Support different data formats
        """

        if endpoint_name not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")

        endpoint = self.endpoints[endpoint_name]

        # Handle batch creation
        if endpoint_name == "create_item":
            return self._create_items_batch(endpoint, data, **kwargs)
        else:
            return self._send_single_item(endpoint, data[0], **kwargs)

    def _fetch_paginated_data(self, endpoint: EndpointConfig, **kwargs) -> Dict:
        """
        Handle paginated data fetching.
        """
        all_items = []
        page = 1
        per_page = kwargs.get("per_page", 100)
        max_results = kwargs.get("max_results", 1000)

        while len(all_items) < max_results:
            # Prepare request parameters
            params = {
                **endpoint.params,
                "page": page,
                "per_page": min(per_page, max_results - len(all_items))
            }

            # Execute request
            response = self._execute_request(endpoint, params=params)
            response_data = response.json()

            # Extract items (adjust based on API response structure)
            items = response_data.get("items", [])
            if not items:
                break  # No more items

            all_items.extend(items)

            # Check if we have more pages
            if len(items) < per_page:
                break  # Last page

            page += 1

            # Rate limiting
            time.sleep(1 / self.rate_limiter.requests_per_second)

        return {
            "items": all_items[:max_results],
            "total_count": len(all_items),
            "page_count": page
        }

    def _create_items_batch(self, endpoint: EndpointConfig,
                           data: List[Dict], **kwargs) -> bool:
        """
        Create multiple items efficiently.
        """
        success_count = 0

        for item in data:
            try:
                response = self._execute_request(endpoint, json=item)
                if response.status_code in [200, 201]:
                    success_count += 1
                else:
                    logger.warning(f"Failed to create item: {response.status_code}")
            except Exception as e:
                logger.error(f"Error creating item: {e}")

            # Rate limiting
            time.sleep(1 / self.rate_limiter.requests_per_second)

        return success_count == len(data)
```

#### Custom Transformer Development

```python
from apilinker.core.plugins import TransformerPlugin

class AdvancedTransformerPlugin(TransformerPlugin):
    """
    Advanced transformer plugin with multiple transformation functions.
    """

    plugin_name = "advanced_transformers"
    plugin_type = "transformer"
    version = "1.0.0"

    def get_transformers(self) -> Dict[str, Callable]:
        """
        Return dictionary of available transformers.
        """
        return {
            # Text processing
            "clean_html": self.clean_html,
            "extract_entities": self.extract_entities,
            "normalize_whitespace": self.normalize_whitespace,

            # Data validation
            "validate_email": self.validate_email,
            "validate_phone": self.validate_phone,
            "validate_url": self.validate_url,

            # Advanced transformations
            "geocode_address": self.geocode_address,
            "currency_convert": self.currency_convert,
            "language_detect": self.detect_language,

            # Custom business logic
            "calculate_score": self.calculate_business_score,
            "enrich_user_data": self.enrich_user_data
        }

    def clean_html(self, html_content: str) -> str:
        """
        Clean HTML content and extract plain text.
        """
        from bs4 import BeautifulSoup

        if not html_content:
            return ""

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text and clean up whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def extract_entities(self, text: str, entity_types: List[str] = None) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        """
        import re

        entity_types = entity_types or ["email", "phone", "url", "date"]
        entities = {}

        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            "url": r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        }

        for entity_type in entity_types:
            if entity_type in patterns:
                entities[entity_type] = re.findall(patterns[entity_type], text)

        return entities

    def geocode_address(self, address: str, api_key: str = None) -> Dict[str, float]:
        """
        Geocode address to latitude/longitude coordinates.
        """
        # This would integrate with a geocoding service
        # For demonstration, returning mock coordinates

        if not address:
            return {"latitude": None, "longitude": None, "confidence": 0}

        # Mock geocoding logic
        # In reality, you'd call a service like Google Maps, OpenStreetMap, etc.

        return {
            "latitude": 40.7128,  # Mock coordinates for NYC
            "longitude": -74.0060,
            "confidence": 0.95,
            "formatted_address": address.title()
        }

    def calculate_business_score(self, data: Dict) -> float:
        """
        Calculate custom business score based on multiple factors.
        """
        score = 0.0

        # Example scoring logic
        if data.get("annual_revenue"):
            score += min(data["annual_revenue"] / 1000000, 10) * 0.3  # Revenue factor

        if data.get("employee_count"):
            score += min(data["employee_count"] / 100, 10) * 0.2  # Size factor

        if data.get("years_in_business"):
            score += min(data["years_in_business"] / 10, 10) * 0.2  # Experience factor

        if data.get("customer_satisfaction"):
            score += data["customer_satisfaction"] * 0.3  # Satisfaction factor

        return min(score, 10.0)  # Cap at 10
```

---

## Development Workflow

### Development Environment Setup

**Complete setup guide for contributors.**

```bash
# 1. Clone repository
git clone https://github.com/kkartas/apilinker.git
cd apilinker

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install development dependencies
pip install -e ".[dev]"

# 4. Setup pre-commit hooks
pre-commit install

# 5. Run initial tests
pytest

# 6. Start development server (if applicable)
uvicorn apilinker.dev_server:app --reload
```

### Code Quality Standards

**Comprehensive code quality guidelines.**

```python
# pyproject.toml configuration for development tools

[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["apilinker"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "performance: marks tests as performance tests"
]

[tool.coverage.run]
source = ["apilinker"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__init__.py",
    "*/conftest.py"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:"
]
```

### Git Workflow

**Standardized Git workflow for contributors.**

```bash
# Feature development workflow

# 1. Create feature branch
git checkout -b feature/new-connector-implementation

# 2. Make changes with descriptive commits
git add .
git commit -m "Add: NCBI connector with PubMed search capability

- Implement NCBIConnector class with email validation
- Add search_pubmed method with pagination support
- Include comprehensive error handling
- Add unit tests with mock responses
- Update documentation with usage examples

Closes #123"

# 3. Keep branch updated
git fetch origin
git rebase origin/main

# 4. Run quality checks
make lint          # Run linters
make test          # Run tests
make type-check    # Run type checking
make security-check # Run security scans

# 5. Push and create PR
git push -u origin feature/new-connector-implementation

# 6. Create pull request with template
# - Clear description of changes
# - Test results and coverage
# - Breaking changes (if any)
# - Documentation updates
```

### Code Review Guidelines

**Comprehensive code review checklist.**

```markdown
## Code Review Checklist

### Functionality
- [ ] Code accomplishes its intended purpose
- [ ] Edge cases are handled appropriately
- [ ] Error handling is comprehensive
- [ ] API contracts are maintained

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Functions and classes have appropriate docstrings
- [ ] Variable and function names are descriptive
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Appropriate design patterns are used

### Testing
- [ ] New code has appropriate test coverage
- [ ] Tests are meaningful and test edge cases
- [ ] Mock objects are used appropriately
- [ ] Integration tests are included where needed

### Performance
- [ ] No obvious performance issues
- [ ] Database queries are optimized
- [ ] Caching is used where appropriate
- [ ] Memory usage is reasonable

### Security
- [ ] Input validation is implemented
- [ ] No sensitive data in logs
- [ ] Authentication/authorization is correct
- [ ] Dependencies are secure and up-to-date

### Documentation
- [ ] Code changes are documented
- [ ] API documentation is updated
- [ ] Breaking changes are noted
- [ ] Examples are provided where helpful
```

---

## Conclusion

This technical documentation provides a comprehensive overview of ApiLinker's internal architecture and implementation details. It serves as a reference for:

- **Contributors**: Understanding the codebase structure and design decisions
- **Extensibility**: Guidelines for creating custom connectors, transformers, and plugins
- **Integration**: Deep technical knowledge for integrating ApiLinker into larger systems
- **Maintenance**: Understanding system components for debugging and optimization

The modular, plugin-based architecture ensures that ApiLinker can be extended and customized for specific use cases while maintaining a clean, maintainable codebase.

For additional technical support or questions about extending ApiLinker, refer to the development documentation in the `docs/` directory or create an issue in the GitHub repository.

---

**ApiLinker v0.4.0** | **Technical Documentation** | **Last Updated: 2025-01-28**
