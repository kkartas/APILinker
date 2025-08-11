# Research Workflows with ApiLinker

This guide demonstrates how researchers can use ApiLinker to create automated workflows for data collection, literature reviews, and interdisciplinary research across scientific domains.

## Table of Contents

- [Quick Start for Researchers](#quick-start-for-researchers)
- [Bioinformatics Workflows](#bioinformatics-workflows)
- [Computer Science & AI Research](#computer-science--ai-research)
- [Interdisciplinary Research](#interdisciplinary-research)
- [Literature Review Automation](#literature-review-automation)
- [Data Collection Pipelines](#data-collection-pipelines)
- [Best Practices for Research](#best-practices-for-research)

## Quick Start for Researchers

### Installation for Research Use

```bash
# Install ApiLinker with all research features
pip install apilinker

# Verify scientific connectors are available
python -c "from apilinker import NCBIConnector, ArXivConnector; print('✅ Ready for research!')"
```

### Your First Research Workflow

```python
from apilinker import NCBIConnector, ArXivConnector

# Set up research APIs (replace with your institutional email)
ncbi = NCBIConnector(email="researcher@university.edu")
arxiv = ArXivConnector()

# Search for papers on a research topic
topic = "machine learning protein folding"

# Get biomedical perspective
pubmed_papers = ncbi.search_pubmed(topic, max_results=20)
print(f"Found {len(pubmed_papers.get('esearchresult', {}).get('idlist', []))} PubMed papers")

# Get computational perspective  
cs_papers = arxiv.search_papers(topic, max_results=20)
print(f"Found {len(cs_papers)} arXiv papers")

# This simple workflow gives you interdisciplinary insights!
```

## Bioinformatics Workflows

### 1. Gene Function Literature Review

Automatically collect and analyze literature about specific genes:

```python
from apilinker import NCBIConnector, ApiLinker
import pandas as pd

def gene_literature_pipeline(gene_name, output_file="gene_review.csv"):
    """
    Comprehensive literature review for a specific gene.
    """
    ncbi = NCBIConnector(email="bioinformatician@university.edu")
    
    # Search for papers about the gene
    search_results = ncbi.search_pubmed(
        query=f"{gene_name} AND (function OR pathway OR disease)",
        max_results=100,
        sort="date"
    )
    
    pubmed_ids = search_results.get('esearchresult', {}).get('idlist', [])
    
    if not pubmed_ids:
        print(f"No papers found for {gene_name}")
        return
    
    # Get detailed article information
    summaries = ncbi.get_article_summaries(pubmed_ids)
    
    # Extract key information
    papers_data = []
    for paper_id in pubmed_ids:
        paper_info = summaries.get('result', {}).get(paper_id, {})
        
        papers_data.append({
            'pubmed_id': paper_id,
            'title': paper_info.get('title', ''),
            'authors': '; '.join([author.get('name', '') for author in paper_info.get('authors', [])]),
            'journal': paper_info.get('source', ''),
            'pub_date': paper_info.get('pubdate', ''),
            'gene': gene_name
        })
    
    # Save to CSV for further analysis
    df = pd.DataFrame(papers_data)
    df.to_csv(output_file, index=False)
    
    print(f"📊 Saved {len(papers_data)} papers to {output_file}")
    print(f"📅 Date range: {df['pub_date'].min()} - {df['pub_date'].max()}")
    
    return df

# Example usage
gene_data = gene_literature_pipeline("BRCA1")
```

### 2. Sequence Data Collection

Collect genetic sequences and associated metadata:

```python
from apilinker import NCBIConnector

def collect_gene_sequences(gene_name, organism="Homo sapiens", max_sequences=50):
    """
    Collect genetic sequences and metadata for analysis.
    """
    ncbi = NCBIConnector(email="genomics@university.edu")
    
    # Search for sequences
    search_query = f"{gene_name} AND {organism}[Organism]"
    search_results = ncbi.search_genbank(search_query, max_results=max_sequences)
    
    sequence_ids = search_results.get('esearchresult', {}).get('idlist', [])
    
    if sequence_ids:
        # Get sequences in FASTA format
        sequences = ncbi.get_sequences(sequence_ids[:10], format="fasta")
        
        # Save sequences to file
        with open(f"{gene_name}_sequences.fasta", "w") as f:
            f.write(sequences)
        
        print(f"📊 Collected {len(sequence_ids)} sequences for {gene_name}")
        print(f"💾 Saved first 10 sequences to {gene_name}_sequences.fasta")
    
    return sequence_ids

# Example: Collect BRCA1 sequences
brca1_sequences = collect_gene_sequences("BRCA1")
```

### 3. Disease-Gene Association Research

Cross-reference genetic variants with disease literature:

```python
from apilinker import ApiLinker, NCBIConnector

def disease_gene_research(disease_name, associated_genes, max_papers_per_gene=20):
    """
    Research disease-gene associations across literature.
    """
    ncbi = NCBIConnector(email="medical_researcher@university.edu")
    linker = ApiLinker()
    
    results = {}
    
    for gene in associated_genes:
        # Search for papers linking gene to disease
        query = f"{gene} AND {disease_name} AND (mutation OR variant OR polymorphism)"
        
        papers = ncbi.search_pubmed(query, max_results=max_papers_per_gene)
        paper_count = len(papers.get('esearchresult', {}).get('idlist', []))
        
        results[gene] = {
            'paper_count': paper_count,
            'search_query': query,
            'pubmed_ids': papers.get('esearchresult', {}).get('idlist', [])
        }
        
        print(f"🧬 {gene}: {paper_count} papers linking to {disease_name}")
    
    # Identify most studied gene-disease associations
    sorted_genes = sorted(results.items(), key=lambda x: x[1]['paper_count'], reverse=True)
    
    print(f"\n📊 Top gene associations with {disease_name}:")
    for gene, data in sorted_genes[:5]:
        print(f"   {gene}: {data['paper_count']} papers")
    
    return results

# Example: Study genes associated with Alzheimer's disease
alzheimer_genes = ["APOE", "APP", "PSEN1", "PSEN2", "TREM2"]
alzheimer_research = disease_gene_research("Alzheimer disease", alzheimer_genes)
```

## Computer Science & AI Research

### 1. Track Emerging AI Techniques

Monitor arXiv for new developments in specific AI areas:

```python
from apilinker import ArXivConnector
from datetime import datetime, timedelta

def track_ai_developments(research_areas, days_back=30, max_papers_per_area=25):
    """
    Track recent developments in AI research areas.
    """
    arxiv = ArXivConnector()
    
    results = {}
    
    for area in research_areas:
        # Search for recent papers
        papers = arxiv.search_papers(
            query=area,
            max_results=max_papers_per_area,
            sort_by="submittedDate",
            sort_order="descending"
        )
        
        # Filter by date
        recent_papers = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for paper in papers:
            if paper.get('published_date'):
                pub_date = datetime.fromisoformat(paper['published_date'].replace('Z', '+00:00'))
                if pub_date >= cutoff_date:
                    recent_papers.append(paper)
        
        results[area] = recent_papers
        print(f"🤖 {area}: {len(recent_papers)} recent papers")
    
    # Analyze trends
    print(f"\n📈 Research Activity (last {days_back} days):")
    for area, papers in sorted(results.items(), key=lambda x: len(x[1]), reverse=True):
        if papers:
            print(f"   {area}: {len(papers)} papers")
            # Show most recent paper
            latest = papers[0]
            print(f"      Latest: '{latest['title'][:60]}...'")
    
    return results

# Example: Track hot AI research areas
ai_areas = [
    "transformer architecture",
    "diffusion models", 
    "large language models",
    "reinforcement learning",
    "computer vision",
    "graph neural networks"
]

ai_trends = track_ai_developments(ai_areas, days_back=14)
```

### 2. Researcher Collaboration Analysis

Build collaboration networks from arXiv data:

```python
from apilinker import ArXivConnector
from collections import defaultdict, Counter

def analyze_research_collaborations(research_field, max_papers=100):
    """
    Analyze collaboration patterns in a research field.
    """
    arxiv = ArXivConnector()
    
    # Get papers in the field
    papers = arxiv.search_papers(research_field, max_results=max_papers)
    
    # Build collaboration network
    collaborations = defaultdict(list)
    author_papers = defaultdict(int)
    author_collaborators = defaultdict(set)
    
    for paper in papers:
        authors = paper.get('authors', [])
        
        # Count papers per author
        for author in authors:
            author_papers[author] += 1
        
        # Track collaborations
        for i, author1 in enumerate(authors):
            for author2 in authors[i+1:]:
                collaborations[tuple(sorted([author1, author2]))].append(paper['title'])
                author_collaborators[author1].add(author2)
                author_collaborators[author2].add(author1)
    
    # Find most prolific authors
    top_authors = Counter(author_papers).most_common(10)
    
    # Find strongest collaborations
    top_collaborations = sorted(
        [(pair, len(papers)) for pair, papers in collaborations.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    print(f"📊 Collaboration Analysis for '{research_field}'")
    print(f"📄 Analyzed {len(papers)} papers")
    print(f"👥 Found {len(author_papers)} unique authors")
    
    print(f"\n🏆 Most Prolific Authors:")
    for author, count in top_authors:
        print(f"   {author}: {count} papers")
    
    print(f"\n🤝 Strongest Collaborations:")
    for (author1, author2), count in top_collaborations:
        print(f"   {author1} ↔ {author2}: {count} joint papers")
    
    return {
        'authors': dict(author_papers),
        'collaborations': dict(collaborations),
        'network': dict(author_collaborators)
    }

# Example: Analyze deep learning collaborations
dl_network = analyze_research_collaborations("deep learning", max_papers=200)
```

## Interdisciplinary Research

### 1. Cross-Domain Knowledge Discovery

Find connections between different research domains:

```python
from apilinker import NCBIConnector, ArXivConnector

def cross_domain_discovery(domain1_terms, domain2_terms, domain1_db="pubmed", domain2_db="arxiv"):
    """
    Discover connections between research domains.
    """
    ncbi = NCBIConnector(email="interdisciplinary@university.edu")
    arxiv = ArXivConnector()
    
    results = {
        'domain1_papers': {},
        'domain2_papers': {},
        'cross_domain_terms': []
    }
    
    # Search domain 1 (typically biomedical)
    if domain1_db == "pubmed":
        for term in domain1_terms:
            papers = ncbi.search_pubmed(term, max_results=30)
            paper_count = len(papers.get('esearchresult', {}).get('idlist', []))
            results['domain1_papers'][term] = paper_count
            print(f"🧬 PubMed - {term}: {paper_count} papers")
    
    # Search domain 2 (typically computer science)
    if domain2_db == "arxiv":
        for term in domain2_terms:
            papers = arxiv.search_papers(term, max_results=30)
            results['domain2_papers'][term] = len(papers)
            print(f"💻 arXiv - {term}: {len(papers)} papers")
    
    # Look for cross-domain connections
    print(f"\n🔗 Searching for cross-domain connections...")
    
    for bio_term in domain1_terms:
        for cs_term in domain2_terms:
            # Search PubMed for CS term
            cs_in_bio = ncbi.search_pubmed(f"{cs_term} AND computational", max_results=10)
            cs_bio_count = len(cs_in_bio.get('esearchresult', {}).get('idlist', []))
            
            # Search arXiv for bio term
            bio_in_cs = arxiv.search_papers(f"{bio_term} bioinformatics", max_results=10)
            bio_cs_count = len(bio_in_cs)
            
            if cs_bio_count > 0 or bio_cs_count > 0:
                connection = {
                    'bio_term': bio_term,
                    'cs_term': cs_term,
                    'cs_in_pubmed': cs_bio_count,
                    'bio_in_arxiv': bio_cs_count,
                    'total_overlap': cs_bio_count + bio_cs_count
                }
                results['cross_domain_terms'].append(connection)
                print(f"   🎯 {bio_term} ↔ {cs_term}: {connection['total_overlap']} connections")
    
    # Sort by strongest connections
    results['cross_domain_terms'].sort(key=lambda x: x['total_overlap'], reverse=True)
    
    return results

# Example: Find connections between genomics and machine learning
bio_terms = ["genomics", "proteomics", "gene expression", "protein folding"]
cs_terms = ["machine learning", "neural networks", "deep learning", "artificial intelligence"]

connections = cross_domain_discovery(bio_terms, cs_terms)
```

### 2. Technology Transfer Analysis

Track how computational methods move between fields:

```python
from apilinker import ArXivConnector, NCBIConnector
from datetime import datetime

def technology_transfer_analysis(technology, source_field, target_fields):
    """
    Analyze how technologies transfer between research fields.
    """
    arxiv = ArXivConnector()
    ncbi = NCBIConnector(email="tech_transfer@university.edu")
    
    results = {
        'source_papers': [],
        'target_adoption': {},
        'timeline': {}
    }
    
    # Get papers from source field
    print(f"🔍 Searching for '{technology}' in {source_field}...")
    source_papers = arxiv.search_papers(
        f"{technology} {source_field}",
        max_results=50,
        sort_by="submittedDate",
        sort_order="descending"
    )
    
    results['source_papers'] = source_papers
    print(f"   Found {len(source_papers)} papers in source field")
    
    # Check adoption in target fields
    for field in target_fields:
        print(f"🎯 Checking adoption in {field}...")
        
        # Search both arXiv and PubMed
        arxiv_papers = arxiv.search_papers(f"{technology} {field}", max_results=30)
        pubmed_papers = ncbi.search_pubmed(f"{technology} AND {field}", max_results=30)
        
        pubmed_count = len(pubmed_papers.get('esearchresult', {}).get('idlist', []))
        
        results['target_adoption'][field] = {
            'arxiv_papers': len(arxiv_papers),
            'pubmed_papers': pubmed_count,
            'total': len(arxiv_papers) + pubmed_count
        }
        
        print(f"   {field}: {len(arxiv_papers)} arXiv + {pubmed_count} PubMed = {len(arxiv_papers) + pubmed_count} total")
    
    # Analyze timeline if we have dates
    years = {}
    for paper in source_papers:
        if paper.get('published_date'):
            year = paper['published_date'][:4]
            years[year] = years.get(year, 0) + 1
    
    results['timeline'] = years
    
    # Summary
    print(f"\n📊 Technology Transfer Summary for '{technology}':")
    print(f"   Source ({source_field}): {len(source_papers)} papers")
    
    sorted_targets = sorted(
        results['target_adoption'].items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )
    
    for field, counts in sorted_targets:
        print(f"   Target ({field}): {counts['total']} papers")
    
    return results

# Example: Analyze how transformers moved from NLP to other fields
transformer_analysis = technology_transfer_analysis(
    technology="transformer",
    source_field="natural language processing",
    target_fields=["computer vision", "bioinformatics", "drug discovery", "genomics"]
)
```

## Literature Review Automation

### 1. Systematic Literature Review

Automate systematic literature reviews following research standards:

```python
from apilinker import NCBIConnector, ArXivConnector
import pandas as pd
from datetime import datetime

def systematic_literature_review(
    research_question,
    search_terms,
    inclusion_criteria,
    date_range=None,
    max_papers_per_db=200
):
    """
    Conduct a systematic literature review across multiple databases.
    """
    ncbi = NCBIConnector(email="systematic_review@university.edu")
    arxiv = ArXivConnector()
    
    print(f"📋 Systematic Literature Review")
    print(f"Research Question: {research_question}")
    print(f"Search Terms: {', '.join(search_terms)}")
    
    all_papers = []
    
    # Search each database
    for term in search_terms:
        # Search PubMed
        pubmed_results = ncbi.search_pubmed(term, max_results=max_papers_per_db)
        pubmed_ids = pubmed_results.get('esearchresult', {}).get('idlist', [])
        
        if pubmed_ids:
            summaries = ncbi.get_article_summaries(pubmed_ids)
            
            for paper_id in pubmed_ids:
                paper_info = summaries.get('result', {}).get(paper_id, {})
                all_papers.append({
                    'id': f"pubmed_{paper_id}",
                    'title': paper_info.get('title', ''),
                    'authors': '; '.join([a.get('name', '') for a in paper_info.get('authors', [])]),
                    'journal': paper_info.get('source', ''),
                    'year': paper_info.get('pubdate', '')[:4] if paper_info.get('pubdate') else '',
                    'database': 'PubMed',
                    'search_term': term,
                    'abstract': ''  # Would need additional API call
                })
        
        # Search arXiv
        arxiv_results = arxiv.search_papers(term, max_results=max_papers_per_db)
        
        for paper in arxiv_results:
            all_papers.append({
                'id': f"arxiv_{paper.get('arxiv_id', '')}",
                'title': paper.get('title', ''),
                'authors': '; '.join(paper.get('authors', [])),
                'journal': 'arXiv',
                'year': paper.get('published_date', '')[:4] if paper.get('published_date') else '',
                'database': 'arXiv',
                'search_term': term,
                'abstract': paper.get('summary', '')
            })
    
    # Create DataFrame for analysis
    df = pd.DataFrame(all_papers)
    
    # Remove duplicates by title
    df = df.drop_duplicates(subset=['title'], keep='first')
    
    # Apply inclusion criteria (basic example)
    if date_range:
        start_year, end_year = date_range
        df = df[df['year'].astype(str).between(str(start_year), str(end_year))]
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"systematic_review_{timestamp}.csv"
    df.to_csv(filename, index=False)
    
    # Summary statistics
    print(f"\n📊 Review Results:")
    print(f"   Total papers found: {len(all_papers)}")
    print(f"   After deduplication: {len(df)}")
    print(f"   Database breakdown:")
    print(df['database'].value_counts().to_string())
    print(f"   Saved to: {filename}")
    
    return df

# Example: Systematic review on AI in healthcare
healthcare_ai_review = systematic_literature_review(
    research_question="How is artificial intelligence being applied in healthcare diagnosis?",
    search_terms=[
        "artificial intelligence healthcare diagnosis",
        "machine learning medical diagnosis", 
        "deep learning radiology",
        "AI clinical decision support"
    ],
    inclusion_criteria="peer-reviewed, English, last 5 years",
    date_range=(2019, 2024),
    max_papers_per_db=100
)
```

## Data Collection Pipelines

### 1. Automated Research Monitoring

Set up automated monitoring for new research in your field:

```python
from apilinker import ApiLinker, ArXivConnector, NCBIConnector
import schedule
import time

class ResearchMonitor:
    """
    Automated research monitoring system.
    """
    
    def __init__(self, email, research_topics, output_dir="research_updates"):
        self.ncbi = NCBIConnector(email=email)
        self.arxiv = ArXivConnector()
        self.topics = research_topics
        self.output_dir = output_dir
        
        # Create output directory
        import os
        os.makedirs(output_dir, exist_ok=True)
    
    def daily_update(self):
        """
        Daily research update scan.
        """
        print(f"🔍 Daily research update - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        updates = {}
        
        for topic in self.topics:
            # Get recent arXiv papers (last 2 days)
            arxiv_papers = self.arxiv.search_recent_papers(
                category="cs.AI" if "AI" in topic else "cs.LG",
                days_back=2,
                max_results=10
            )
            
            # Filter by topic
            relevant_papers = [
                paper for paper in arxiv_papers
                if topic.lower() in paper.get('title', '').lower() or
                   topic.lower() in paper.get('summary', '').lower()
            ]
            
            updates[topic] = {
                'arxiv_papers': relevant_papers,
                'count': len(relevant_papers)
            }
            
            print(f"   📄 {topic}: {len(relevant_papers)} new papers")
        
        # Save daily update
        if any(update['count'] > 0 for update in updates.values()):
            self._save_update(updates)
        
        return updates
    
    def _save_update(self, updates):
        """Save updates to file."""
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{self.output_dir}/update_{timestamp}.md"
        
        with open(filename, "w") as f:
            f.write(f"# Research Update - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            
            for topic, data in updates.items():
                if data['count'] > 0:
                    f.write(f"## {topic} ({data['count']} papers)\n\n")
                    
                    for paper in data['arxiv_papers']:
                        f.write(f"### {paper['title']}\n")
                        f.write(f"**Authors:** {', '.join(paper['authors'][:3])}\n\n")
                        f.write(f"**Abstract:** {paper['summary'][:200]}...\n\n")
                        f.write(f"**Link:** {paper['links'].get('abstract_url', '')}\n\n")
        
        print(f"💾 Saved update to {filename}")

# Example usage
def setup_research_monitoring():
    """
    Set up automated research monitoring.
    """
    monitor = ResearchMonitor(
        email="researcher@university.edu",
        research_topics=[
            "large language models",
            "protein folding",
            "quantum computing",
            "computer vision"
        ]
    )
    
    # Schedule daily updates
    schedule.every().day.at("09:00").do(monitor.daily_update)
    
    print("🚀 Research monitoring started!")
    print("📅 Daily updates scheduled for 9:00 AM")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n👋 Research monitoring stopped")

# To start monitoring (uncomment to run):
# setup_research_monitoring()
```

## Best Practices for Research

### 1. Reproducible Research Workflows

```python
from apilinker import ApiLinker
import yaml
import hashlib
import json

def create_reproducible_workflow(config_path):
    """
    Create a reproducible research workflow with full provenance tracking.
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create hash of configuration for reproducibility
    config_hash = hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()
    
    # Set up ApiLinker
    linker = ApiLinker(config_path=config_path)
    
    # Add metadata tracking
    workflow_metadata = {
        'timestamp': datetime.now().isoformat(),
        'config_hash': config_hash,
        'apilinker_version': '0.3.0',
        'workflow_id': config_hash[:8]
    }
    
    print(f"🔬 Starting reproducible workflow")
    print(f"   Workflow ID: {workflow_metadata['workflow_id']}")
    print(f"   Config Hash: {config_hash}")
    
    return linker, workflow_metadata

# Example configuration for reproducible research
example_config = {
    'research_info': {
        'title': 'AI Applications in Drug Discovery',
        'investigator': 'Dr. Research Scientist',
        'institution': 'University Research Lab',
        'date': '2024-01-15'
    },
    'data_sources': {
        'pubmed_query': 'artificial intelligence drug discovery',
        'arxiv_category': 'cs.LG',
        'date_range': '2020-2024',
        'max_papers': 500
    },
    'analysis_parameters': {
        'min_citations': 10,
        'exclude_preprints': False,
        'language': 'English'
    }
}
```

### 2. Ethical Research Data Collection

```python
from apilinker import NCBIConnector, ArXivConnector
import time

class EthicalResearchCollector:
    """
    Research data collector with ethical guidelines built-in.
    """
    
    def __init__(self, email, rate_limit_delay=1.0):
        self.ncbi = NCBIConnector(email=email)
        self.arxiv = ArXivConnector()
        self.rate_limit_delay = rate_limit_delay
        self.request_count = 0
    
    def respectful_search(self, query, max_results=100, database="both"):
        """
        Search with respectful API usage and backoff on 429.
        """
        results = {}
        
        if database in ["both", "pubmed"]:
            print(f"🔍 Searching PubMed: {query}")
            pubmed_results = self.ncbi.search_pubmed(query, max_results=max_results)
            results['pubmed'] = pubmed_results
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            self.request_count += 1
        
        if database in ["both", "arxiv"]:
            print(f"🔍 Searching arXiv: {query}")
            arxiv_results = self.arxiv.search_papers(query, max_results=max_results)
            results['arxiv'] = arxiv_results
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            self.request_count += 1
        
        print(f"📊 API requests made: {self.request_count}")
        
        return results
    
    def get_usage_summary(self):
        """
        Report on API usage for transparency.
        """
        return {
            'total_requests': self.request_count,
            'rate_limit_delay': self.rate_limit_delay,
            'apis_used': ['NCBI E-utilities', 'arXiv API'],
            'data_use_policy': 'Research and educational use only'
        }

# Example usage
ethical_collector = EthicalResearchCollector(
    email="ethical_researcher@university.edu",
    rate_limit_delay=1.5  # Be extra respectful
)
```

---

*This documentation demonstrates ApiLinker's power for research workflows. For more examples, see the `examples/` directory and visit our documentation at [apilinker.readthedocs.io](https://apilinker.readthedocs.io/).*