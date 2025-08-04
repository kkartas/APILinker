# Research Configuration Guide

This guide shows researchers how to configure ApiLinker for different types of research workflows, from simple literature searches to complex automated research pipelines.

## Table of Contents

- [Basic Research Configuration](#basic-research-configuration)
- [YAML Configuration for Research](#yaml-configuration-for-research)
- [Python Configuration for Research](#python-configuration-for-research)
- [Automated Research Workflows](#automated-research-workflows)
- [Multi-Database Integration](#multi-database-integration)
- [Custom Research Transformers](#custom-research-transformers)
- [Security and Ethics](#security-and-ethics)

## Basic Research Configuration

### Simple Literature Search Configuration

For basic literature searches across multiple databases:

```yaml
# research_config.yaml
research_metadata:
  project: "AI in Drug Discovery Literature Review"
  investigator: "Dr. Research Scientist"
  institution: "University Research Lab"
  date: "2024-01-15"

sources:
  pubmed:
    type: "ncbi"
    email: "researcher@university.edu"  # Required for NCBI
    endpoints:
      search_literature:
        database: "pubmed"
        max_results: 100
        sort: "date"

  arxiv:
    type: "arxiv"
    endpoints:
      search_preprints:
        max_results: 100
        sort_by: "submittedDate"

targets:
  research_database:
    type: "rest"
    base_url: "https://your-research-db.com/api"
    auth:
      type: "api_key"
      key: "${RESEARCH_DB_KEY}"
    endpoints:
      save_papers:
        path: "/papers"
        method: "POST"

mappings:
  literature_sync:
    source: "search_literature"
    target: "save_papers"
    fields:
      - source: "esearchresult.idlist"
        target: "paper_ids"
      - source: "esearchresult.count"
        target: "total_found"
      - source: "esearchresult.querytranslation"
        target: "processed_query"

transformers:
  research_metadata_enricher:
    function: "add_research_context"
    parameters:
      project_id: "drug_discovery_2024"
      search_date: "{{ current_date }}"
      investigator: "Dr. Research Scientist"

schedule:
  daily_literature_update:
    interval: "daily"
    time: "09:00"
    workflow: "literature_sync"
    params:
      query: "artificial intelligence drug discovery"
      date_range: "last_1_days"
```

### Using the Configuration

```python
from apilinker import ApiLinker

# Load research configuration
linker = ApiLinker(config_path="research_config.yaml")

# Run literature search
results = linker.sync_data(
    source_endpoint="search_literature",
    target_endpoint="save_papers",
    params={"query": "CRISPR gene editing", "max_results": 50}
)

print(f"Transferred {results.transferred_records} papers")
```

## YAML Configuration for Research

### Comprehensive Research Project Configuration

```yaml
# comprehensive_research_config.yaml
research_project:
  title: "Cross-Domain Analysis: AI Applications in Biology"
  principal_investigator: "Dr. Jane Smith"
  institution: "Stanford University"
  grant_number: "NSF-12345"
  start_date: "2024-01-01"
  expected_duration: "24 months"

data_sources:
  ncbi_pubmed:
    type: "ncbi"
    email: "j.smith@stanford.edu"
    api_key: "${NCBI_API_KEY}"  # Optional but recommended
    rate_limit: 3  # Requests per second
    endpoints:
      biomedical_search:
        database: "pubmed"
        max_results: 500
        filters:
          - "English[Language]"
          - "Journal Article[Publication Type]"
          - "2020:2024[Publication Date]"
      
      genetic_sequences:
        database: "nuccore"
        max_results: 100
        sequence_type: "nucleotide"

  arxiv_cs:
    type: "arxiv"
    rate_limit: 1  # Respectful rate limiting
    endpoints:
      cs_papers:
        categories: ["cs.AI", "cs.LG", "cs.CV", "cs.CL"]
        max_results: 300
        date_range: "2020-2024"
      
      interdisciplinary_papers:
        search_fields: ["title", "abstract", "categories"]
        max_results: 200

  institutional_repository:
    type: "rest"
    base_url: "https://repository.stanford.edu/api"
    auth:
      type: "oauth2"
      client_id: "${REPO_CLIENT_ID}"
      client_secret: "${REPO_CLIENT_SECRET}"
    endpoints:
      stanford_research:
        path: "/search"
        method: "GET"

data_targets:
  research_database:
    type: "rest" 
    base_url: "https://research-db.stanford.edu/api"
    auth:
      type: "bearer_token"
      token: "${RESEARCH_DB_TOKEN}"
    endpoints:
      store_papers:
        path: "/papers"
        method: "POST"
        batch_size: 50
      
      store_analysis:
        path: "/analysis"
        method: "POST"

  collaboration_platform:
    type: "rest"
    base_url: "https://api.slack.com/api"
    auth:
      type: "bearer_token"
      token: "${SLACK_BOT_TOKEN}"
    endpoints:
      notify_team:
        path: "/chat.postMessage"
        method: "POST"

research_workflows:
  daily_literature_monitoring:
    description: "Monitor new publications in AI and biology"
    sources: ["ncbi_pubmed", "arxiv_cs"]
    targets: ["research_database", "collaboration_platform"]
    
    search_queries:
      ai_biology_intersection:
        pubmed_query: "artificial intelligence AND (biology OR bioinformatics OR genomics)"
        arxiv_query: "machine learning biology"
        minimum_relevance: 0.7
      
      emerging_techniques:
        pubmed_query: "deep learning AND (protein OR gene OR drug discovery)"
        arxiv_query: "transformer bioinformatics"
        minimum_relevance: 0.8

    data_processing:
      deduplication:
        method: "title_similarity"
        threshold: 0.9
      
      relevance_filtering:
        use_ai: true
        model: "research_relevance_classifier"
        confidence_threshold: 0.75
      
      citation_enrichment:
        enabled: true
        sources: ["crossref", "semantic_scholar"]

  weekly_trend_analysis:
    description: "Analyze research trends and generate reports"
    frequency: "weekly"
    day: "monday" 
    time: "08:00"
    
    analysis_types:
      - keyword_trends
      - author_collaboration_networks
      - institutional_partnerships
      - citation_impact_analysis
    
    report_generation:
      formats: ["pdf", "html", "json"]
      recipients: ["j.smith@stanford.edu", "research-team@stanford.edu"]
      include_visualizations: true

data_transformations:
  standardize_author_names:
    function: "normalize_author_format"
    parameters:
      format: "last_name, first_initial"
      handle_consortiums: true
  
  extract_research_themes:
    function: "topic_modeling"
    parameters:
      model_type: "LDA"
      num_topics: 20
      min_word_frequency: 5
  
  calculate_impact_metrics:
    function: "bibliometric_analysis"
    parameters:
      metrics: ["citation_count", "h_index", "impact_factor"]
      time_window: "5_years"

quality_assurance:
  data_validation:
    required_fields: ["title", "authors", "publication_date", "source"]
    field_validation:
      publication_date:
        format: "YYYY-MM-DD"
        range: ["2000-01-01", "2024-12-31"]
      authors:
        min_count: 1
        max_count: 50
  
  ethical_compliance:
    rate_limiting: true
    api_terms_compliance: true
    data_anonymization: false  # Research data, keep identifiable
    citation_requirements: true

error_handling:
  retry_strategy:
    max_retries: 3
    backoff_multiplier: 2
    max_wait_time: 60
  
  dead_letter_queue:
    enabled: true
    max_retention: "7_days"
  
  notification_channels:
    email: "j.smith@stanford.edu"
    slack: "#research-alerts"

monitoring:
  performance_metrics:
    track_response_times: true
    track_error_rates: true
    track_data_quality: true
  
  research_metrics:
    papers_processed_daily: true
    research_coverage_by_field: true
    collaboration_network_growth: true

archival:
  backup_frequency: "daily"
  retention_period: "indefinite"  # Research data
  backup_location: "stanford_research_archive"
  versioning: true
  metadata_preservation: true
```

## Python Configuration for Research

### Programmatic Research Configuration

```python
from apilinker import ApiLinker, NCBIConnector, ArXivConnector
from datetime import datetime, timedelta

class ResearchConfiguration:
    """
    Comprehensive research configuration class.
    """
    
    def __init__(self, project_config):
        self.config = project_config
        self.linker = ApiLinker()
        self._setup_connectors()
        self._setup_transformers()
    
    def _setup_connectors(self):
        """Set up scientific connectors."""
        # NCBI connector for biomedical research
        self.ncbi = NCBIConnector(
            email=self.config['investigator_email'],
            api_key=self.config.get('ncbi_api_key'),
            tool_name=f"ApiLinker_{self.config['project_name']}"
        )
        
        # arXiv connector for preprints
        self.arxiv = ArXivConnector()
        
        # Add to ApiLinker
        self.linker.add_source(
            name="ncbi_source",
            connector=self.ncbi
        )
        
        self.linker.add_source(
            name="arxiv_source", 
            connector=self.arxiv
        )
    
    def _setup_transformers(self):
        """Set up research-specific data transformers."""
        
        def add_research_metadata(data):
            """Add research project metadata to all records."""
            if isinstance(data, dict):
                data['research_project'] = self.config['project_name']
                data['investigator'] = self.config['principal_investigator']
                data['processed_date'] = datetime.now().isoformat()
                data['processing_version'] = self.config.get('version', '1.0')
            return data
        
        def normalize_publication_dates(data):
            """Normalize publication dates across different sources."""
            date_fields = ['published_date', 'pubdate', 'date', 'pub_date']
            
            for field in date_fields:
                if field in data and data[field]:
                    try:
                        # Normalize to ISO format
                        if isinstance(data[field], str):
                            # Handle different date formats
                            if len(data[field]) == 4:  # Just year
                                data['normalized_date'] = f"{data[field]}-01-01"
                            elif '/' in data[field]:  # MM/DD/YYYY
                                parts = data[field].split('/')
                                if len(parts) == 3:
                                    data['normalized_date'] = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                            else:
                                data['normalized_date'] = data[field][:10]  # Take first 10 chars (YYYY-MM-DD)
                        break
                    except Exception:
                        continue
            
            return data
        
        def extract_research_keywords(data):
            """Extract and standardize research keywords."""
            import re
            
            # Combine title and abstract for keyword extraction
            text = ""
            if 'title' in data:
                text += data['title'] + " "
            if 'abstract' in data or 'summary' in data:
                text += data.get('abstract', data.get('summary', ''))
            
            # Simple keyword extraction (in practice, use NLP libraries)
            keywords = []
            research_terms = [
                'machine learning', 'deep learning', 'neural network',
                'artificial intelligence', 'data mining', 'algorithm',
                'protein', 'gene', 'DNA', 'genome', 'bioinformatics',
                'drug discovery', 'molecular', 'clinical', 'biomedical'
            ]
            
            text_lower = text.lower()
            for term in research_terms:
                if term in text_lower:
                    keywords.append(term)
            
            data['extracted_keywords'] = keywords
            data['keyword_count'] = len(keywords)
            
            return data
        
        # Register transformers
        self.linker.mapper.register_transformer("add_research_metadata", add_research_metadata)
        self.linker.mapper.register_transformer("normalize_publication_dates", normalize_publication_dates)
        self.linker.mapper.register_transformer("extract_research_keywords", extract_research_keywords)
    
    def setup_literature_review_workflow(self, search_terms, max_papers_per_term=100):
        """Set up automated literature review workflow."""
        
        self.linker.add_mapping(
            name="literature_review_mapping",
            source_endpoint="search",
            target_endpoint="store",
            fields=[
                {"source": "title", "target": "paper_title"},
                {"source": "authors", "target": "author_list"},
                {"source": "published_date", "target": "publication_date", "transformer": "normalize_publication_dates"},
                {"source": "abstract", "target": "abstract_text"},
                {"source": "journal", "target": "publication_venue"},
                {"source": "categories", "target": "research_categories"}
            ],
            transformers=[
                "add_research_metadata",
                "extract_research_keywords"
            ]
        )
        
        # Configure search parameters
        search_config = {
            'terms': search_terms,
            'max_results': max_papers_per_term,
            'date_range': self.config.get('date_range', '2020-2024'),
            'filters': self.config.get('search_filters', [])
        }
        
        return search_config
    
    def setup_collaboration_analysis(self, research_fields):
        """Set up collaboration network analysis."""
        
        def analyze_author_collaborations(papers):
            """Analyze collaboration patterns in papers."""
            from collections import defaultdict, Counter
            
            collaborations = defaultdict(list)
            author_stats = Counter()
            
            for paper in papers:
                authors = paper.get('authors', [])
                
                # Count papers per author
                for author in authors:
                    author_stats[author] += 1
                
                # Track collaborations
                for i, author1 in enumerate(authors):
                    for author2 in authors[i+1:]:
                        collaboration_key = tuple(sorted([author1, author2]))
                        collaborations[collaboration_key].append(paper.get('title', 'Unknown'))
            
            return {
                'collaboration_pairs': dict(collaborations),
                'author_productivity': dict(author_stats),
                'total_authors': len(author_stats),
                'total_collaborations': len(collaborations)
            }
        
        self.linker.mapper.register_transformer("analyze_collaborations", analyze_author_collaborations)
        
        return {
            'analysis_function': analyze_author_collaborations,
            'research_fields': research_fields
        }
    
    def setup_automated_monitoring(self, keywords, notification_config):
        """Set up automated research monitoring."""
        
        def create_research_alert(new_papers):
            """Create research alerts for new papers."""
            if not new_papers:
                return None
            
            alert = {
                'timestamp': datetime.now().isoformat(),
                'new_paper_count': len(new_papers),
                'keywords_triggered': keywords,
                'top_papers': new_papers[:5],  # Top 5 most relevant
                'notification_sent': False
            }
            
            # Send notification (implement based on your needs)
            if notification_config.get('email'):
                # Send email notification
                alert['notification_sent'] = True
            
            if notification_config.get('slack'):
                # Send Slack notification  
                alert['notification_sent'] = True
            
            return alert
        
        self.linker.mapper.register_transformer("create_research_alert", create_research_alert)
        
        # Schedule daily monitoring
        self.linker.add_scheduler(
            name="daily_research_monitoring",
            interval="daily",
            time="09:00",
            workflow="monitor_new_research",
            config={
                'keywords': keywords,
                'lookback_days': 1,
                'notification_config': notification_config
            }
        )

# Example usage
project_config = {
    'project_name': 'AI_Drug_Discovery_Review',
    'principal_investigator': 'Dr. Research Scientist',
    'investigator_email': 'researcher@university.edu',
    'ncbi_api_key': 'your_ncbi_api_key',  # Optional but recommended
    'date_range': '2020-2024',
    'search_filters': ['English[Language]', 'Journal Article[Publication Type]'],
    'version': '1.0'
}

# Set up research configuration
research = ResearchConfiguration(project_config)

# Configure literature review
search_terms = [
    'artificial intelligence drug discovery',
    'machine learning pharmaceutical',
    'deep learning drug design'
]

lit_review_config = research.setup_literature_review_workflow(search_terms, max_papers_per_term=150) 

# Configure collaboration analysis
collab_config = research.setup_collaboration_analysis(['drug discovery', 'machine learning', 'bioinformatics'])

# Set up monitoring
monitoring_config = research.setup_automated_monitoring(
    keywords=['AI drug discovery', 'ML pharmaceuticals'],
    notification_config={
        'email': 'researcher@university.edu',
        'slack': '#research-updates'
    }
)

print("Research configuration completed successfully!")
```

## Automated Research Workflows

### Daily Research Monitoring Configuration

```yaml
# automated_research_config.yaml
automation:
  daily_monitoring:
    enabled: true
    time: "09:00"
    timezone: "UTC"
    
    workflows:
      literature_scan:
        description: "Scan for new papers in research areas"
        sources: ["pubmed", "arxiv"]
        search_queries:
          - "artificial intelligence AND drug discovery"
          - "machine learning AND protein folding"
          - "deep learning AND genomics"
        
        filters:
          date_range: "last_1_day"
          min_relevance_score: 0.8
          exclude_review_papers: false
        
        actions:
          - save_to_database
          - notify_researchers
          - update_research_dashboard
      
      trend_analysis:
        description: "Analyze research trends weekly"
        frequency: "weekly"
        day: "monday"
        
        analysis_types:
          - keyword_frequency_changes
          - new_author_discoveries
          - citation_impact_tracking
          - institutional_collaboration_changes
        
        report_generation:
          format: "html_dashboard"
          include_visualizations: true
          email_recipients: ["team@university.edu"]

  real_time_alerts:
    enabled: true
    
    alert_triggers:
      high_impact_papers:
        condition: "citation_velocity > 10_per_day"
        notification: "immediate"
      
      collaboration_opportunities:
        condition: "author_similarity > 0.9 AND different_institutions"
        notification: "weekly_digest"
      
      grant_opportunities:
        condition: "funding_keywords_match > 3"
        notification: "immediate"

data_pipelines:
  preprocessing:
    - remove_duplicates
    - standardize_formats
    - extract_metadata
    - calculate_relevance_scores
  
  enrichment:
    - add_citation_data
    - extract_author_affiliations
    - identify_research_themes
    - calculate_impact_metrics
  
  postprocessing:
    - generate_summaries
    - create_visualizations
    - update_knowledge_graph
    - prepare_notifications
```

## Multi-Database Integration

### Cross-Database Research Configuration

```python
from apilinker import ApiLinker, NCBIConnector, ArXivConnector

class MultiDatabaseResearchSetup:
    """
    Configure ApiLinker for comprehensive multi-database research.
    """
    
    def __init__(self, research_profile):
        self.profile = research_profile
        self.linker = ApiLinker()
        self.setup_all_sources()
    
    def setup_all_sources(self):
        """Set up all research databases and APIs."""
        
        # Biomedical databases (NCBI)
        self.setup_ncbi_sources()
        
        # Preprint servers
        self.setup_preprint_sources()
        
        # Patent databases (if needed)
        if self.profile.get('include_patents'):
            self.setup_patent_sources()
        
        # Funding databases (if needed)
        if self.profile.get('include_funding'):
            self.setup_funding_sources()
        
        # Social media research tracking
        if self.profile.get('include_social_media'):
            self.setup_social_media_sources()
    
    def setup_ncbi_sources(self):
        """Set up NCBI database sources."""
        ncbi = NCBIConnector(
            email=self.profile['email'],
            api_key=self.profile.get('ncbi_api_key')
        )
        
        # Configure different NCBI databases
        ncbi_configs = {
            'pubmed': {
                'database': 'pubmed',
                'search_fields': ['title', 'abstract', 'keywords'],
                'filters': self.profile.get('pubmed_filters', [])
            },
            'genbank': {
                'database': 'nuccore',
                'search_fields': ['organism', 'gene', 'protein'],
                'sequence_types': ['nucleotide', 'protein']
            },
            'clinvar': {
                'database': 'clinvar',
                'search_fields': ['gene', 'condition', 'variant'],
                'significance_filters': ['pathogenic', 'likely_pathogenic']
            }
        }
        
        for db_name, config in ncbi_configs.items():
            self.linker.add_source(
                name=f"ncbi_{db_name}",
                type="ncbi",
                connector=ncbi,
                config=config
            )
    
    def setup_preprint_sources(self):
        """Set up preprint server sources."""
        # arXiv
        arxiv = ArXivConnector()
        self.linker.add_source(
            name="arxiv",
            type="arxiv", 
            connector=arxiv,
            config={
                'categories': self.profile.get('arxiv_categories', ['cs.AI', 'cs.LG']),
                'search_fields': ['title', 'abstract', 'categories']
            }
        )
        
        # bioRxiv (via API if available)
        if self.profile.get('include_biorxiv'):
            self.linker.add_source(
                name="biorxiv",
                type="rest",
                base_url="https://api.biorxiv.org",
                config={
                    'search_endpoint': '/details/biorxiv',
                    'date_range': self.profile.get('date_range', '2020-2024')
                }
            )
    
    def setup_cross_database_search(self, research_question):
        """Set up unified cross-database search."""
        
        # Define search strategy for each database type
        search_strategies = {
            'biomedical': {
                'databases': ['ncbi_pubmed', 'ncbi_clinvar'],
                'query_terms': self._extract_biomedical_terms(research_question),
                'weight': 0.4
            },
            'computational': {
                'databases': ['arxiv'],
                'query_terms': self._extract_computational_terms(research_question),
                'weight': 0.3
            },
            'interdisciplinary': {
                'databases': ['ncbi_pubmed', 'arxiv'],
                'query_terms': self._extract_interdisciplinary_terms(research_question),
                'weight': 0.3
            }
        }
        
        # Configure unified search workflow
        self.linker.add_workflow(
            name="cross_database_research",
            description=f"Cross-database search for: {research_question}",
            steps=[
                {
                    'name': 'parallel_search',
                    'type': 'parallel',
                    'sources': list(search_strategies.keys()),
                    'merge_strategy': 'weighted_relevance'
                },
                {
                    'name': 'deduplication',
                    'type': 'transform',
                    'function': 'remove_cross_database_duplicates'
                },
                {
                    'name': 'relevance_ranking',
                    'type': 'transform',
                    'function': 'calculate_unified_relevance_score'
                },
                {
                    'name': 'result_synthesis',
                    'type': 'transform',
                    'function': 'synthesize_cross_database_results'
                }
            ]
        )
        
        return search_strategies
    
    def _extract_biomedical_terms(self, question):
        """Extract biomedical search terms from research question."""
        biomedical_keywords = [
            'protein', 'gene', 'DNA', 'RNA', 'enzyme', 'pathway',
            'disease', 'treatment', 'drug', 'therapeutic', 'clinical',
            'molecular', 'cellular', 'biological', 'medical'
        ]
        
        terms = []
        question_lower = question.lower()
        for keyword in biomedical_keywords:
            if keyword in question_lower:
                terms.append(keyword)
        
        return terms
    
    def _extract_computational_terms(self, question):
        """Extract computational search terms from research question."""
        computational_keywords = [
            'machine learning', 'deep learning', 'neural network',
            'algorithm', 'artificial intelligence', 'AI', 'ML',
            'computational', 'data mining', 'statistical', 'model'
        ]
        
        terms = []
        question_lower = question.lower()
        for keyword in computational_keywords:
            if keyword in question_lower:
                terms.append(keyword)
        
        return terms
    
    def _extract_interdisciplinary_terms(self, question):
        """Extract interdisciplinary search terms."""
        interdisciplinary_keywords = [
            'bioinformatics', 'computational biology', 'systems biology',
            'bioengineering', 'medical informatics', 'digital health',
            'precision medicine', 'personalized medicine'
        ]
        
        terms = []
        question_lower = question.lower()
        for keyword in interdisciplinary_keywords:
            if keyword in question_lower:
                terms.append(keyword)
        
        return terms

# Example usage
research_profile = {
    'email': 'researcher@university.edu',
    'ncbi_api_key': 'your_api_key',
    'arxiv_categories': ['cs.AI', 'cs.LG', 'q-bio.QM'],
    'pubmed_filters': ['English[Language]', '2020:2024[Publication Date]'],
    'include_patents': False,
    'include_funding': True,
    'include_social_media': False,
    'date_range': '2020-2024'
}

# Set up multi-database research
multi_db_research = MultiDatabaseResearchSetup(research_profile)

# Configure cross-database search
research_question = "How can machine learning improve protein folding prediction?"
search_config = multi_db_research.setup_cross_database_search(research_question)

print("Multi-database research configuration completed!")
print(f"Configured {len(search_config)} search strategies")
```

## Custom Research Transformers

### Research-Specific Data Transformations

```python
from apilinker import ApiLinker

def setup_research_transformers(linker):
    """Set up custom transformers for research data."""
    
    def extract_research_impact_metrics(paper_data):
        """Calculate research impact metrics."""
        import re
        from datetime import datetime, date
        
        # Calculate paper age
        pub_date = paper_data.get('published_date')
        if pub_date:
            try:
                if isinstance(pub_date, str):
                    # Parse various date formats
                    if len(pub_date) == 4:  # Just year
                        pub_year = int(pub_date)
                        pub_date_obj = date(pub_year, 1, 1)
                    else:
                        pub_date_obj = datetime.fromisoformat(pub_date.replace('Z', '')).date()
                
                paper_age_days = (date.today() - pub_date_obj).days
                paper_data['paper_age_days'] = paper_age_days
                paper_data['paper_age_years'] = paper_age_days / 365.25
                
            except (ValueError, TypeError):
                paper_data['paper_age_days'] = None
                paper_data['paper_age_years'] = None
        
        # Estimate research maturity based on keyword analysis
        title = paper_data.get('title', '').lower()
        abstract = paper_data.get('abstract', paper_data.get('summary', '')).lower()
        
        emerging_keywords = [
            'novel', 'new', 'first', 'emerging', 'innovative', 'breakthrough',
            'cutting-edge', 'state-of-the-art', 'pioneering'
        ]
        
        established_keywords = [
            'review', 'survey', 'comprehensive', 'systematic', 'meta-analysis',
            'established', 'traditional', 'standard', 'conventional'
        ]
        
        emerging_score = sum(1 for keyword in emerging_keywords if keyword in title or keyword in abstract)
        established_score = sum(1 for keyword in established_keywords if keyword in title or keyword in abstract)
        
        if emerging_score > established_score:
            paper_data['research_maturity'] = 'emerging'
        elif established_score > emerging_score:
            paper_data['research_maturity'] = 'established'
        else:
            paper_data['research_maturity'] = 'developing'
        
        paper_data['emerging_score'] = emerging_score
        paper_data['established_score'] = established_score
        
        return paper_data
    
    def identify_research_themes(paper_data):
        """Identify research themes using keyword analysis."""
        title = paper_data.get('title', '').lower()
        abstract = paper_data.get('abstract', paper_data.get('summary', '')).lower()
        categories = paper_data.get('categories', [])
        
        # Define research theme categories
        theme_keywords = {
            'artificial_intelligence': [
                'artificial intelligence', 'machine learning', 'deep learning',
                'neural network', 'ai', 'ml', 'dl'
            ],
            'bioinformatics': [
                'bioinformatics', 'computational biology', 'genomics',
                'proteomics', 'systems biology', 'biostatistics'
            ],
            'drug_discovery': [
                'drug discovery', 'drug development', 'pharmaceutical',
                'molecular docking', 'qsar', 'admet', 'drug design'
            ],
            'clinical_research': [
                'clinical trial', 'patient', 'diagnosis', 'treatment',
                'medical', 'healthcare', 'clinical'
            ],
            'methodology': [
                'method', 'methodology', 'algorithm', 'framework',
                'approach', 'technique', 'model', 'system'
            ]
        }
        
        identified_themes = []
        theme_scores = {}
        
        full_text = f"{title} {abstract} {' '.join(categories)}"
        
        for theme, keywords in theme_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            if score > 0:
                identified_themes.append(theme)
                theme_scores[theme] = score
        
        paper_data['research_themes'] = identified_themes
        paper_data['theme_scores'] = theme_scores
        paper_data['primary_theme'] = max(theme_scores, key=theme_scores.get) if theme_scores else 'general'
        
        return paper_data
    
    def calculate_collaboration_metrics(paper_data):
        """Calculate collaboration-related metrics."""
        authors = paper_data.get('authors', [])
        
        if not authors:
            paper_data['collaboration_metrics'] = {
                'author_count': 0,
                'collaboration_level': 'none',
                'estimated_institutions': 0
            }
            return paper_data
        
        author_count = len(authors)
        
        # Estimate collaboration level
        if author_count == 1:
            collaboration_level = 'solo'
        elif author_count <= 3:
            collaboration_level = 'small_team'
        elif author_count <= 10:
            collaboration_level = 'medium_team'
        else:
            collaboration_level = 'large_team'
        
        # Estimate number of institutions (rough heuristic)
        # In practice, you'd use affiliation data
        estimated_institutions = min(max(1, author_count // 3), 10)
        
        paper_data['collaboration_metrics'] = {
            'author_count': author_count,
            'collaboration_level': collaboration_level,
            'estimated_institutions': estimated_institutions,
            'first_author': authors[0] if authors else None,
            'last_author': authors[-1] if len(authors) > 1 else None
        }
        
        return paper_data
    
    def assess_interdisciplinary_potential(paper_data):
        """Assess the interdisciplinary potential of research."""
        themes = paper_data.get('research_themes', [])
        categories = paper_data.get('categories', [])
        
        # Count different disciplinary areas
        disciplinary_areas = set()
        
        # Map themes to disciplines
        theme_to_discipline = {
            'artificial_intelligence': 'computer_science',
            'bioinformatics': 'biology', 
            'drug_discovery': 'chemistry',
            'clinical_research': 'medicine',
            'methodology': 'mathematics'
        }
        
        for theme in themes:
            if theme in theme_to_discipline:
                disciplinary_areas.add(theme_to_discipline[theme])
        
        # Analyze arXiv categories for additional discipline info
        cs_categories = [cat for cat in categories if cat.startswith('cs.')]
        bio_categories = [cat for cat in categories if cat.startswith('q-bio.')]
        physics_categories = [cat for cat in categories if cat.startswith('physics.')]
        
        if cs_categories:
            disciplinary_areas.add('computer_science')
        if bio_categories:
            disciplinary_areas.add('biology')
        if physics_categories:
            disciplinary_areas.add('physics')
        
        interdisciplinary_score = len(disciplinary_areas)
        
        if interdisciplinary_score >= 3:
            interdisciplinary_level = 'highly_interdisciplinary'
        elif interdisciplinary_score == 2:
            interdisciplinary_level = 'interdisciplinary'
        else:
            interdisciplinary_level = 'disciplinary'
        
        paper_data['interdisciplinary_assessment'] = {
            'disciplinary_areas': list(disciplinary_areas),
            'interdisciplinary_score': interdisciplinary_score,
            'interdisciplinary_level': interdisciplinary_level
        }
        
        return paper_data
    
    # Register all transformers
    linker.mapper.register_transformer("extract_research_impact_metrics", extract_research_impact_metrics)
    linker.mapper.register_transformer("identify_research_themes", identify_research_themes)
    linker.mapper.register_transformer("calculate_collaboration_metrics", calculate_collaboration_metrics)
    linker.mapper.register_transformer("assess_interdisciplinary_potential", assess_interdisciplinary_potential)
    
    return linker

# Example usage
linker = ApiLinker()
linker = setup_research_transformers(linker)

# Configure mapping with research transformers
linker.add_mapping(
    name="enhanced_research_mapping",
    source_endpoint="search_papers",
    target_endpoint="store_analysis",
    fields=[
        {"source": "title", "target": "paper_title"},
        {"source": "authors", "target": "author_list"},
        {"source": "published_date", "target": "publication_date"},
        {"source": "abstract", "target": "abstract_text"}
    ],
    transformers=[
        "extract_research_impact_metrics",
        "identify_research_themes", 
        "calculate_collaboration_metrics",
        "assess_interdisciplinary_potential"
    ]
)

print("Research transformers configured successfully!")
```

## Security and Ethics

### Ethical Research Configuration

```yaml
# ethical_research_config.yaml
ethics_compliance:
  institutional_review:
    irb_approval: "IRB-2024-001"  # If human subjects involved
    data_use_agreement: "signed"
    
  api_usage_ethics:
    rate_limiting:
      ncbi_requests_per_second: 3
      arxiv_requests_per_second: 1
      respect_api_limits: true
    
    attribution:
      cite_data_sources: true
      acknowledge_apis: true
      preserve_original_licensing: true
    
    data_handling:
      store_personal_data: false  # Don't store author personal info
      anonymize_when_possible: false  # Research often needs attribution
      retention_policy: "indefinite"  # Research data retention
      
  research_integrity:
    reproducibility:
      version_configurations: true
      archive_raw_data: true
      document_processing_steps: true
      
    transparency:
      public_methodology: true
      share_configurations: true
      open_source_preferred: true
      
    collaboration:
      respect_intellectual_property: true
      proper_attribution: true
      collaborative_sharing: true

security:
  api_credentials:
    storage: "environment_variables"  # Never hardcode
    encryption: "at_rest"
    access_control: "role_based"
    
  data_protection:
    encryption_in_transit: true
    secure_storage: true
    backup_encryption: true
    
  access_control:
    researcher_authentication: "institutional_sso"
    data_access_logging: true
    permission_levels: ["read", "write", "admin"]

compliance:
  institutional_policies:
    follow_university_guidelines: true
    data_governance_compliance: true
    international_regulations: ["GDPR", "CCPA"]  # If applicable
    
  funding_requirements:
    open_access_compliance: true
    data_sharing_requirements: true
    funder_acknowledgment: true
```

---

This comprehensive configuration guide provides researchers with everything they need to set up ApiLinker for their specific research needs, from simple literature searches to complex automated research workflows. The examples can be adapted and customized for different research domains and requirements.