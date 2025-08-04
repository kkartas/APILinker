# Getting Started with ApiLinker for Research

This tutorial provides a step-by-step introduction to using ApiLinker for research workflows, specifically designed for researchers who may be new to API integration.

## Prerequisites

- Python 3.8 or higher
- Basic familiarity with Python programming
- Research email address (required for NCBI APIs)
- Understanding of your research domain and key terms

## Installation

### Step 1: Install ApiLinker

```bash
# Install ApiLinker with all features
pip install apilinker

# Verify installation
python -c "import apilinker; print(f'ApiLinker {apilinker.__version__} installed successfully!')"
```

### Step 2: Verify Scientific Connectors

```bash
# Test scientific connectors
python -c "from apilinker import NCBIConnector, ArXivConnector; print('Scientific connectors ready!')"
```

## Your First Research Query

Let's start with a simple example that demonstrates the power of cross-database research.

### Example 1: Basic Literature Search

```python
from apilinker import NCBIConnector, ArXivConnector

# Step 1: Set up your research credentials
# Replace with your institutional email address
research_email = "your.name@university.edu"

# Step 2: Initialize scientific connectors
ncbi = NCBIConnector(email=research_email)
arxiv = ArXivConnector()

# Step 3: Define your research topic
research_topic = "CRISPR gene editing"

# Step 4: Search biomedical literature (PubMed)
print(f"🔍 Searching PubMed for '{research_topic}'...")
pubmed_results = ncbi.search_pubmed(research_topic, max_results=10)
pubmed_count = len(pubmed_results.get('esearchresult', {}).get('idlist', []))
print(f"   Found {pubmed_count} papers in PubMed")

# Step 5: Search computer science literature (arXiv)
print(f"🔍 Searching arXiv for '{research_topic}'...")
arxiv_results = arxiv.search_papers(research_topic, max_results=10)
print(f"   Found {len(arxiv_results)} papers in arXiv")

# Step 6: Analyze the results
print(f"\n📊 Research Landscape for '{research_topic}':")
print(f"   Biomedical papers: {pubmed_count}")
print(f"   Computer science papers: {len(arxiv_results)}")
print(f"   Total papers found: {pubmed_count + len(arxiv_results)}")

if len(arxiv_results) > 0:
    print(f"\n📄 Recent arXiv paper:")
    latest_paper = arxiv_results[0]
    print(f"   Title: {latest_paper['title']}")
    print(f"   Authors: {', '.join(latest_paper['authors'][:3])}")
    print(f"   Published: {latest_paper['published_date'][:10]}")
```

### Example 2: Detailed Paper Analysis

```python
from apilinker import NCBIConnector

def analyze_research_topic(topic, max_papers=20):
    """
    Perform detailed analysis of a research topic.
    """
    ncbi = NCBIConnector(email="researcher@university.edu")  # Replace with your email
    
    # Search for papers
    results = ncbi.search_pubmed(topic, max_results=max_papers)
    paper_ids = results.get('esearchresult', {}).get('idlist', [])
    
    if not paper_ids:
        print(f"No papers found for '{topic}'")
        return None
    
    # Get detailed information
    summaries = ncbi.get_article_summaries(paper_ids)
    
    # Analyze the papers
    analysis = {
        'topic': topic,
        'total_papers': len(paper_ids),
        'journals': {},
        'years': {},
        'top_papers': []
    }
    
    print(f"📊 Analyzing {len(paper_ids)} papers on '{topic}'...\n")
    
    for paper_id in paper_ids[:10]:  # Analyze first 10 papers
        paper_info = summaries.get('result', {}).get(paper_id, {})
        
        # Extract information
        title = paper_info.get('title', 'Unknown Title')
        journal = paper_info.get('source', 'Unknown Journal')
        pub_date = paper_info.get('pubdate', 'Unknown Date')
        authors = paper_info.get('authors', [])
        
        # Count journals
        analysis['journals'][journal] = analysis['journals'].get(journal, 0) + 1
        
        # Count years
        year = pub_date[:4] if len(pub_date) >= 4 else 'Unknown'
        analysis['years'][year] = analysis['years'].get(year, 0) + 1
        
        # Store paper info
        analysis['top_papers'].append({
            'title': title,
            'journal': journal,
            'year': year,
            'author_count': len(authors),
            'pubmed_id': paper_id
        })
    
    # Display results
    print(f"🏆 Top Journals:")
    top_journals = sorted(analysis['journals'].items(), key=lambda x: x[1], reverse=True)[:5]
    for journal, count in top_journals:
        print(f"   {journal}: {count} papers")
    
    print(f"\n📅 Publication Years:")
    top_years = sorted(analysis['years'].items(), key=lambda x: x[1], reverse=True)[:5]
    for year, count in top_years:
        print(f"   {year}: {count} papers")
    
    print(f"\n📋 Recent Papers:")
    for i, paper in enumerate(analysis['top_papers'][:5], 1):
        print(f"   {i}. {paper['title'][:60]}...")
        print(f"      {paper['journal']} ({paper['year']}) | PubMed ID: {paper['pubmed_id']}")
    
    return analysis

# Example usage
analysis = analyze_research_topic("artificial intelligence healthcare")
```

## Building Your First Research Workflow

Now let's create a more sophisticated workflow that combines multiple data sources:

### Example 3: Cross-Domain Research Discovery

```python
from apilinker import ApiLinker, NCBIConnector, ArXivConnector

def cross_domain_research_workflow(primary_topic, secondary_topic, max_papers_each=25):
    """
    Discover connections between two research domains.
    """
    # Initialize components
    linker = ApiLinker()
    ncbi = NCBIConnector(email="interdisciplinary.researcher@university.edu")
    arxiv = ArXivConnector()
    
    print(f"🔬 Cross-Domain Research Workflow")
    print(f"Primary domain: {primary_topic}")
    print(f"Secondary domain: {secondary_topic}")
    print("-" * 50)
    
    # Step 1: Research each domain separately
    print(f"📚 Step 1: Individual domain research")
    
    # Primary domain (biomedical)
    primary_papers = ncbi.search_pubmed(primary_topic, max_results=max_papers_each)
    primary_count = len(primary_papers.get('esearchresult', {}).get('idlist', []))
    
    # Secondary domain (computer science)  
    secondary_papers = arxiv.search_papers(secondary_topic, max_results=max_papers_each)
    secondary_count = len(secondary_papers)
    
    print(f"   {primary_topic}: {primary_count} PubMed papers")
    print(f"   {secondary_topic}: {secondary_count} arXiv papers")
    
    # Step 2: Look for intersections
    print(f"\n🔗 Step 2: Finding intersections")
    
    # Search for primary topic in computer science
    primary_in_cs = arxiv.search_papers(f"{primary_topic} computational", max_results=15)
    
    # Search for secondary topic in biomedical literature
    secondary_in_bio = ncbi.search_pubmed(f"{secondary_topic} AND biomedical", max_results=15)
    secondary_bio_count = len(secondary_in_bio.get('esearchresult', {}).get('idlist', []))
    
    print(f"   {primary_topic} in CS literature: {len(primary_in_cs)} papers")
    print(f"   {secondary_topic} in biomedical literature: {secondary_bio_count} papers")
    
    # Step 3: Identify collaboration opportunities
    print(f"\n🤝 Step 3: Collaboration opportunities")
    
    intersection_strength = len(primary_in_cs) + secondary_bio_count
    
    if intersection_strength > 5:
        opportunity_level = "High"
    elif intersection_strength > 2:
        opportunity_level = "Moderate" 
    else:
        opportunity_level = "Low"
    
    print(f"   Intersection strength: {intersection_strength} papers")
    print(f"   Collaboration opportunity: {opportunity_level}")
    
    # Step 4: Generate research suggestions
    print(f"\n💡 Step 4: Research suggestions")
    
    if len(primary_in_cs) > 0:
        print(f"   • Computational approaches to {primary_topic} are emerging")
        print(f"   • Latest computational paper: '{primary_in_cs[0]['title'][:50]}...'")
    
    if secondary_bio_count > 0:
        print(f"   • {secondary_topic} applications in biomedicine exist")
        print(f"   • Consider interdisciplinary collaboration")
    
    if intersection_strength < 3:
        print(f"   • Limited intersection suggests novel research opportunity")
        print(f"   • Pioneer work could have high impact")
    
    # Return structured results
    return {
        'primary_domain': {
            'topic': primary_topic,
            'papers': primary_count,
            'cs_intersection': len(primary_in_cs)
        },
        'secondary_domain': {
            'topic': secondary_topic,
            'papers': secondary_count,
            'bio_intersection': secondary_bio_count
        },
        'collaboration_potential': opportunity_level,
        'intersection_strength': intersection_strength
    }

# Example: Explore protein folding and machine learning
research_results = cross_domain_research_workflow(
    primary_topic="protein folding",
    secondary_topic="machine learning"
)
```

## Research Workflow Automation

### Example 4: Automated Research Monitoring

Set up automated monitoring for your research area:

```python
from apilinker import ArXivConnector, NCBIConnector
from datetime import datetime
import schedule
import time

class ResearchMonitor:
    """
    Automated research monitoring for your field.
    """
    
    def __init__(self, email, research_keywords, output_file="research_updates.txt"):
        self.ncbi = NCBIConnector(email=email)
        self.arxiv = ArXivConnector()
        self.keywords = research_keywords
        self.output_file = output_file
        self.last_check = datetime.now()
    
    def daily_research_update(self):
        """
        Check for new research daily.
        """
        print(f"🔍 Daily research update - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        updates = []
        
        for keyword in self.keywords:
            # Check arXiv for recent papers (last 3 days)
            recent_papers = self.arxiv.search_recent_papers(
                category="cs.LG",  # Adjust category as needed
                days_back=3,
                max_results=20
            )
            
            # Filter by keyword
            relevant_papers = [
                paper for paper in recent_papers
                if keyword.lower() in paper.get('title', '').lower() or
                   keyword.lower() in paper.get('summary', '').lower()
            ]
            
            if relevant_papers:
                updates.append(f"\n📄 New papers for '{keyword}':")
                for paper in relevant_papers[:3]:  # Top 3 papers
                    updates.append(f"   • {paper['title']}")
                    updates.append(f"     Authors: {', '.join(paper['authors'][:2])}")
                    updates.append(f"     Date: {paper['published_date'][:10]}")
        
        # Save updates
        if updates:
            with open(self.output_file, "a") as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Research Update - {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write("\n".join(updates))
                f.write("\n")
            
            print(f"💾 Updates saved to {self.output_file}")
            print(f"📊 Found updates for {len([u for u in updates if 'New papers' in u])} keywords")
        else:
            print("📭 No new papers found today")
    
    def start_monitoring(self):
        """
        Start automated monitoring.
        """
        print("🚀 Starting research monitoring...")
        print(f"📧 Email: {self.ncbi.email}")
        print(f"🔍 Keywords: {', '.join(self.keywords)}")
        print(f"📄 Output: {self.output_file}")
        
        # Schedule daily updates at 9 AM
        schedule.every().day.at("09:00").do(self.daily_research_update)
        
        # Run initial check
        self.daily_research_update()
        
        # Keep monitoring (in practice, run this as a service)
        print("⏰ Monitoring scheduled. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")

# Example usage (uncomment to run):
# monitor = ResearchMonitor(
#     email="your.email@university.edu",
#     research_keywords=["quantum computing", "machine learning", "drug discovery"],
#     output_file="my_research_updates.txt"
# )
# monitor.start_monitoring()
```

## Best Practices for Research

### 1. Ethical API Usage

```python
import time
from apilinker import NCBIConnector

class EthicalResearcher:
    """
    Research class that follows ethical API usage guidelines.
    """
    
    def __init__(self, email, rate_limit=1.0):
        self.ncbi = NCBIConnector(email=email)  # Always provide institutional email
        self.rate_limit = rate_limit  # Seconds between requests
        self.request_count = 0
    
    def respectful_search(self, query, max_results=50):
        """
        Search with respectful rate limiting.
        """
        print(f"🔍 Searching (request #{self.request_count + 1}): {query}")
        
        result = self.ncbi.search_pubmed(query, max_results=max_results)
        
        # Rate limiting
        time.sleep(self.rate_limit)
        self.request_count += 1
        
        if self.request_count % 10 == 0:
            print(f"📊 Made {self.request_count} requests total")
        
        return result

# Always use your institutional email
researcher = EthicalResearcher("your.name@university.edu", rate_limit=1.5)
```

### 2. Reproducible Research

```python
import yaml
import hashlib
import json
from datetime import datetime

def create_reproducible_workflow_config(research_params):
    """
    Create a reproducible research configuration.
    """
    config = {
        'metadata': {
            'created': datetime.now().isoformat(),
            'researcher': research_params.get('researcher_name'),
            'institution': research_params.get('institution'),
            'project': research_params.get('project_name')
        },
        'search_parameters': {
            'keywords': research_params.get('keywords'),
            'max_results_per_query': research_params.get('max_results', 50),
            'databases': research_params.get('databases', ['pubmed', 'arxiv']),
            'date_range': research_params.get('date_range')
        },
        'analysis_settings': {
            'exclude_review_papers': research_params.get('exclude_reviews', False),
            'minimum_citation_count': research_params.get('min_citations', 0),
            'language_filter': research_params.get('language', 'English')
        }
    }
    
    # Create reproducibility hash
    config_string = json.dumps(config, sort_keys=True)
    config['metadata']['reproducibility_hash'] = hashlib.md5(config_string.encode()).hexdigest()
    
    # Save configuration
    filename = f"research_config_{config['metadata']['reproducibility_hash'][:8]}.yaml"
    with open(filename, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=True)
    
    print(f"📋 Reproducible config saved: {filename}")
    print(f"🔗 Reproducibility hash: {config['metadata']['reproducibility_hash'][:16]}...")
    
    return config, filename

# Example usage
config, config_file = create_reproducible_workflow_config({
    'researcher_name': 'Dr. Research Scientist',
    'institution': 'University Research Lab',
    'project_name': 'AI in Drug Discovery Survey',
    'keywords': ['artificial intelligence', 'drug discovery', 'machine learning'],
    'max_results': 100,
    'databases': ['pubmed', 'arxiv'],
    'exclude_reviews': True
})
```

## Next Steps

After completing this tutorial, you're ready to:

1. **Explore Advanced Features**: Check out `docs/research_workflows.md` for complex workflows
2. **Domain-Specific Examples**: See `docs/scientific_use_cases.md` for your research area
3. **Automation**: Set up scheduled research monitoring
4. **Integration**: Combine ApiLinker with your existing research tools
5. **Collaboration**: Share configurations with research collaborators

## Common Issues and Solutions

### Issue: "No papers found"
**Solution**: Try broader search terms or check spelling

### Issue: Rate limiting errors
**Solution**: Increase delays between requests and use institutional email

### Issue: Too many results
**Solution**: Use more specific search terms or date ranges

### Issue: Missing dependencies
**Solution**: Ensure all packages are installed: `pip install apilinker`

---

*This tutorial gets you started with research-focused API integration. For more advanced examples and domain-specific workflows, explore the other documentation files.*