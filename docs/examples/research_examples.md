# Research Examples

This page provides practical examples of using ApiLinker for research across different scientific domains.

## Table of Contents

- [Quick Research Examples](#quick-research-examples)
- [Bioinformatics Examples](#bioinformatics-examples)
- [Computer Science Examples](#computer-science-examples)
- [Interdisciplinary Research](#interdisciplinary-research)
- [Social Sciences Examples](#social-sciences-examples)
- [Climate Science Examples](#climate-science-examples)

## Quick Research Examples

### 30-Second Literature Search

```python
from apilinker import NCBIConnector, ArXivConnector

# Initialize (use your institutional email)
ncbi = NCBIConnector(email="researcher@university.edu")
arxiv = ArXivConnector()

# Search both databases
topic = "quantum computing"
pubmed_papers = ncbi.search_pubmed(topic, max_results=10)
arxiv_papers = arxiv.search_papers(topic, max_results=10)

print(f"PubMed: {len(pubmed_papers.get('esearchresult', {}).get('idlist', []))} papers")
print(f"arXiv: {len(arxiv_papers)} papers")
```

### Research Trend Analysis

```python
from apilinker import ArXivConnector
from collections import Counter

def analyze_research_trends(field, years=2):
    """Quick analysis of research trends in a field."""
    arxiv = ArXivConnector()
    
    papers = arxiv.search_recent_papers(
        category="cs.AI" if "AI" in field else "cs.LG",
        days_back=years*365,
        max_results=200
    )
    
    # Extract trending keywords from titles
    keywords = []
    for paper in papers:
        title_words = paper.get('title', '').lower().split()
        keywords.extend([word for word in title_words if len(word) > 4])
    
    trends = Counter(keywords).most_common(10)
    
    print(f"📈 Trending in {field}:")
    for keyword, count in trends:
        print(f"   {keyword}: {count} mentions")
    
    return trends

# Example usage
ai_trends = analyze_research_trends("artificial intelligence", years=1)
```

## Bioinformatics Examples

### Gene Function Research

```python
from apilinker import NCBIConnector

def research_gene_function(gene_name):
    """Comprehensive gene function research."""
    ncbi = NCBIConnector(email="bioinformatics@university.edu")
    
    # Search for functional studies
    function_papers = ncbi.search_pubmed(
        f"{gene_name} AND (function OR pathway OR regulation)",
        max_results=30
    )
    
    # Search for disease associations
    disease_papers = ncbi.search_pubmed(
        f"{gene_name} AND (disease OR disorder OR syndrome)",
        max_results=25
    )
    
    # Search for protein interactions
    interaction_papers = ncbi.search_pubmed(
        f"{gene_name} AND (protein interaction OR binding)",
        max_results=20
    )
    
    # Get sequences
    sequences = ncbi.search_genbank(f"{gene_name} Homo sapiens", max_results=5)
    
    # Summary
    results = {
        'gene': gene_name,
        'function_studies': len(function_papers.get('esearchresult', {}).get('idlist', [])),
        'disease_associations': len(disease_papers.get('esearchresult', {}).get('idlist', [])),
        'interaction_studies': len(interaction_papers.get('esearchresult', {}).get('idlist', [])),
        'sequence_entries': len(sequences.get('esearchresult', {}).get('idlist', []))
    }
    
    print(f"🧬 Gene Research Summary: {gene_name}")
    for key, value in results.items():
        if key != 'gene':
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    return results

# Example: Research BRCA1 gene
brca1_research = research_gene_function("BRCA1")
```

### Comparative Genomics Study

```python
from apilinker import NCBIConnector

def comparative_genomics_study(gene_list, organisms):
    """Compare gene research across organisms."""
    ncbi = NCBIConnector(email="comparative.genomics@university.edu")
    
    results = {}
    
    for gene in gene_list:
        results[gene] = {}
        
        for organism in organisms:
            # Search for sequences in this organism
            query = f"{gene} AND {organism}[Organism]"
            sequences = ncbi.search_genbank(query, max_results=10)
            
            # Search for functional studies
            papers = ncbi.search_pubmed(f"{gene} AND {organism}", max_results=15)
            
            results[gene][organism] = {
                'sequences': len(sequences.get('esearchresult', {}).get('idlist', [])),
                'studies': len(papers.get('esearchresult', {}).get('idlist', []))
            }
    
    # Display results matrix
    print(f"📊 Comparative Genomics Matrix")
    print(f"{'Gene':<12} " + " ".join([f"{org[:8]:<10}" for org in organisms]))
    print("-" * (12 + len(organisms) * 11))
    
    for gene, data in results.items():
        row = f"{gene:<12} "
        for organism in organisms:
            seqs = data[organism]['sequences']
            studies = data[organism]['studies']
            row += f"{seqs}s/{studies}p".ljust(10)
        print(row)
    
    return results

# Example: Compare genes across model organisms
comparison = comparative_genomics_study(
    gene_list=["TP53", "BRCA1", "MYC"],
    organisms=["Homo sapiens", "Mus musculus", "Drosophila melanogaster"]
)
```

## Computer Science Examples

### AI Research Landscape Analysis

```python
from apilinker import ArXivConnector
from datetime import datetime, timedelta

def analyze_ai_landscape(subfields, months_back=12):
    """Analyze the AI research landscape across subfields."""
    arxiv = ArXivConnector()
    
    landscape = {}
    cutoff_date = datetime.now() - timedelta(days=months_back*30)
    
    for subfield in subfields:
        papers = arxiv.search_papers(subfield, max_results=100, sort_by="submittedDate")
        
        # Filter recent papers
        recent_papers = []
        for paper in papers:
            if paper.get('published_date'):
                pub_date = datetime.fromisoformat(paper['published_date'].replace('Z', '+00:00'))
                if pub_date >= cutoff_date:
                    recent_papers.append(paper)
        
        # Analyze author activity
        authors = []
        for paper in recent_papers:
            authors.extend(paper.get('authors', []))
        
        from collections import Counter
        top_authors = Counter(authors).most_common(5)
        
        landscape[subfield] = {
            'total_papers': len(papers),
            'recent_papers': len(recent_papers),
            'activity_level': 'High' if len(recent_papers) > 20 else 'Moderate' if len(recent_papers) > 5 else 'Low',
            'top_authors': top_authors
        }
        
        print(f"🤖 {subfield}:")
        print(f"   Recent activity: {len(recent_papers)} papers ({landscape[subfield]['activity_level']})")
        if top_authors:
            print(f"   Top author: {top_authors[0][0]} ({top_authors[0][1]} papers)")
    
    return landscape

# Example: Analyze AI subfields
ai_landscape = analyze_ai_landscape([
    "large language models",
    "computer vision transformers", 
    "reinforcement learning",
    "graph neural networks"
])
```

### Technology Transfer Tracking

```python
from apilinker import ArXivConnector, NCBIConnector

def track_technology_transfer(cs_technique, application_domains):
    """Track how CS techniques are adopted in other fields."""
    arxiv = ArXivConnector()
    ncbi = NCBIConnector(email="tech.transfer@university.edu")
    
    transfer_analysis = {
        'technique': cs_technique,
        'origin_papers': [],
        'applications': {}
    }
    
    # Get origin papers in computer science
    cs_papers = arxiv.search_papers(cs_technique, max_results=50, category="cs.LG")
    transfer_analysis['origin_papers'] = cs_papers
    
    print(f"💻 Technology Transfer Analysis: {cs_technique}")
    print(f"   Origin papers (CS): {len(cs_papers)}")
    
    # Check adoption in application domains
    for domain in application_domains:
        # Search arXiv for applications
        arxiv_apps = arxiv.search_papers(f"{cs_technique} {domain}", max_results=25)
        
        # Search PubMed for biomedical applications
        if "bio" in domain.lower() or "medical" in domain.lower():
            pubmed_apps = ncbi.search_pubmed(f"{cs_technique} AND {domain}", max_results=20)
            pubmed_count = len(pubmed_apps.get('esearchresult', {}).get('idlist', []))
        else:
            pubmed_count = 0
        
        total_applications = len(arxiv_apps) + pubmed_count
        
        transfer_analysis['applications'][domain] = {
            'arxiv_papers': len(arxiv_apps),
            'pubmed_papers': pubmed_count,
            'total': total_applications,
            'transfer_level': 'High' if total_applications > 10 else 'Emerging' if total_applications > 3 else 'Minimal'
        }
        
        print(f"   {domain}: {total_applications} papers ({transfer_analysis['applications'][domain]['transfer_level']})")
    
    return transfer_analysis

# Example: Track transformer adoption
transformer_transfer = track_technology_transfer(
    cs_technique="transformer neural network",
    application_domains=["bioinformatics", "drug discovery", "climate modeling", "robotics"]
)
```

## Interdisciplinary Research

### Cross-Domain Knowledge Discovery

```python
from apilinker import NCBIConnector, ArXivConnector

def discover_cross_domain_connections(domain1_terms, domain2_terms, connection_threshold=3):
    """Discover unexpected connections between research domains."""
    ncbi = NCBIConnector(email="interdisciplinary@university.edu")
    arxiv = ArXivConnector()
    
    connections = []
    
    print(f"🔗 Cross-Domain Knowledge Discovery")
    print(f"Domain 1 terms: {', '.join(domain1_terms)}")
    print(f"Domain 2 terms: {', '.join(domain2_terms)}")
    
    for term1 in domain1_terms:
        for term2 in domain2_terms:
            # Search for papers mentioning both terms
            combined_query = f"{term1} AND {term2}"
            
            # Search both databases
            pubmed_results = ncbi.search_pubmed(combined_query, max_results=20)
            arxiv_results = arxiv.search_papers(combined_query, max_results=20)
            
            pubmed_count = len(pubmed_results.get('esearchresult', {}).get('idlist', []))
            arxiv_count = len(arxiv_results)
            total_connections = pubmed_count + arxiv_count
            
            if total_connections >= connection_threshold:
                connection_strength = "Strong" if total_connections > 10 else "Moderate"
                
                connections.append({
                    'term1': term1,
                    'term2': term2,
                    'pubmed_papers': pubmed_count,
                    'arxiv_papers': arxiv_count,
                    'total_papers': total_connections,
                    'connection_strength': connection_strength
                })
                
                print(f"   🎯 {term1} ↔ {term2}: {total_connections} papers ({connection_strength})")
    
    # Sort by connection strength
    connections.sort(key=lambda x: x['total_papers'], reverse=True)
    
    if not connections:
        print("   No strong connections found above threshold")
    
    return connections

# Example: Find connections between AI and biology
bio_ai_connections = discover_cross_domain_connections(
    domain1_terms=["protein folding", "gene expression", "drug discovery"],
    domain2_terms=["machine learning", "neural networks", "deep learning"]
)
```

### Research Gap Identification

```python
from apilinker import ArXivConnector, NCBIConnector

def identify_research_gaps(established_fields, emerging_technologies):
    """Identify potential research gaps at intersections."""
    arxiv = ArXivConnector()
    ncbi = NCBIConnector(email="gap_analysis@university.edu")
    
    gap_analysis = {}
    
    print(f"🕳️  Research Gap Analysis")
    
    for field in established_fields:
        gap_analysis[field] = {}
        
        # Get baseline research volume
        field_papers = ncbi.search_pubmed(field, max_results=100)
        baseline_count = len(field_papers.get('esearchresult', {}).get('idlist', []))
        
        for tech in emerging_technologies:
            # Search for intersection
            intersection_query = f"{field} AND {tech}"
            
            pubmed_intersection = ncbi.search_pubmed(intersection_query, max_results=50)
            arxiv_intersection = arxiv.search_papers(intersection_query, max_results=50)
            
            intersection_count = (
                len(pubmed_intersection.get('esearchresult', {}).get('idlist', [])) +
                len(arxiv_intersection)
            )
            
            # Calculate gap score (high baseline, low intersection = big gap)
            if baseline_count > 0:
                gap_score = baseline_count / (intersection_count + 1)  # +1 to avoid division by zero
            else:
                gap_score = 0
            
            gap_analysis[field][tech] = {
                'baseline_papers': baseline_count,
                'intersection_papers': intersection_count,
                'gap_score': gap_score,
                'opportunity_level': 'High' if gap_score > 20 else 'Moderate' if gap_score > 5 else 'Low'
            }
    
    # Find biggest gaps
    biggest_gaps = []
    for field, technologies in gap_analysis.items():
        for tech, data in technologies.items():
            if data['opportunity_level'] == 'High':
                biggest_gaps.append({
                    'field': field,
                    'technology': tech,
                    'gap_score': data['gap_score'],
                    'baseline': data['baseline_papers'],
                    'intersection': data['intersection_papers']
                })
    
    # Sort by gap score
    biggest_gaps.sort(key=lambda x: x['gap_score'], reverse=True)
    
    print(f"\n🎯 Top Research Opportunities:")
    for gap in biggest_gaps[:5]:
        print(f"   {gap['field']} + {gap['technology']}")
        print(f"      Gap score: {gap['gap_score']:.1f}")
        print(f"      Baseline: {gap['baseline']} papers, Intersection: {gap['intersection']} papers")
    
    return gap_analysis, biggest_gaps

# Example: Find gaps where AI could be applied
gaps, opportunities = identify_research_gaps(
    established_fields=["cardiology", "oncology", "neurology", "pathology"],
    emerging_technologies=["computer vision", "natural language processing", "reinforcement learning"]
)
```

## Social Sciences Examples

### Public Health Research Integration

```python
from apilinker import NCBIConnector

def public_health_research_integration(health_condition, social_factors):
    """Integrate biomedical and social determinants research."""
    ncbi = NCBIConnector(email="public.health@university.edu")
    
    integration_analysis = {
        'condition': health_condition,
        'biomedical_research': {},
        'social_research': {},
        'integrated_research': {}
    }
    
    # Biomedical research
    biomedical_papers = ncbi.search_pubmed(
        f"{health_condition} AND (pathophysiology OR treatment OR diagnosis)",
        max_results=50
    )
    integration_analysis['biomedical_research'] = {
        'paper_count': len(biomedical_papers.get('esearchresult', {}).get('idlist', [])),
        'focus': 'Clinical and biological aspects'
    }
    
    # Social determinants research
    for factor in social_factors:
        social_papers = ncbi.search_pubmed(
            f"{health_condition} AND {factor} AND (social determinants OR health equity)",
            max_results=30
        )
        
        integration_analysis['social_research'][factor] = {
            'paper_count': len(social_papers.get('esearchresult', {}).get('idlist', [])),
            'research_level': 'High' if len(social_papers.get('esearchresult', {}).get('idlist', [])) > 10 else 'Moderate' if len(social_papers.get('esearchresult', {}).get('idlist', [])) > 5 else 'Limited'
        }
    
    # Integrated research
    integrated_papers = ncbi.search_pubmed(
        f"{health_condition} AND (social determinants OR disparities OR equity) AND (biology OR pathophysiology)",
        max_results=25
    )
    integration_analysis['integrated_research'] = {
        'paper_count': len(integrated_papers.get('esearchresult', {}).get('idlist', [])),
        'integration_level': 'High' if len(integrated_papers.get('esearchresult', {}).get('idlist', [])) > 15 else 'Moderate' if len(integrated_papers.get('esearchresult', {}).get('idlist', [])) > 5 else 'Limited'
    }
    
    print(f"🏥 Public Health Integration Analysis: {health_condition}")
    print(f"   Biomedical research: {integration_analysis['biomedical_research']['paper_count']} papers")
    print(f"   Social factors research:")
    
    for factor, data in integration_analysis['social_research'].items():
        print(f"      {factor}: {data['paper_count']} papers ({data['research_level']})")
    
    print(f"   Integrated research: {integration_analysis['integrated_research']['paper_count']} papers ({integration_analysis['integrated_research']['integration_level']})")
    
    return integration_analysis

# Example: Analyze diabetes from multiple perspectives
diabetes_integration = public_health_research_integration(
    health_condition="diabetes mellitus",
    social_factors=["income inequality", "food access", "education level", "neighborhood environment"]
)
```

## Climate Science Examples

### Climate-Health Research Synthesis

```python
from apilinker import NCBIConnector, ArXivConnector

def climate_health_research_synthesis(climate_factors, health_outcomes):
    """Synthesize research on climate change and health impacts."""
    ncbi = NCBIConnector(email="climate.health@university.edu")
    arxiv = ArXivConnector()
    
    synthesis = {
        'climate_science': {},
        'health_impacts': {},
        'integrated_studies': {}
    }
    
    print(f"🌍 Climate-Health Research Synthesis")
    
    # Analyze each climate factor
    for factor in climate_factors:
        # Climate science papers
        climate_papers = arxiv.search_papers(
            f"{factor} climate change",
            max_results=30,
            category="physics:ao-ph"
        )
        
        synthesis['climate_science'][factor] = {
            'papers': len(climate_papers),
            'research_maturity': 'Mature' if len(climate_papers) > 20 else 'Developing'
        }
        
        print(f"   🌡️  {factor}: {len(climate_papers)} climate science papers")
    
    # Analyze health outcomes
    for outcome in health_outcomes:
        # Health research
        health_papers = ncbi.search_pubmed(
            f"{outcome} AND climate change AND health",
            max_results=40
        )
        
        synthesis['health_impacts'][outcome] = {
            'papers': len(health_papers.get('esearchresult', {}).get('idlist', [])),
            'evidence_level': 'Strong' if len(health_papers.get('esearchresult', {}).get('idlist', [])) > 15 else 'Moderate' if len(health_papers.get('esearchresult', {}).get('idlist', [])) > 5 else 'Limited'
        }
        
        print(f"   🏥 {outcome}: {len(health_papers.get('esearchresult', {}).get('idlist', []))} health impact papers")
    
    # Look for integrated studies
    for factor in climate_factors:
        for outcome in health_outcomes:
            integrated_query = f"{factor} AND {outcome} AND climate change AND health"
            integrated_papers = ncbi.search_pubmed(integrated_query, max_results=20)
            
            integration_count = len(integrated_papers.get('esearchresult', {}).get('idlist', []))
            
            if integration_count > 0:
                synthesis['integrated_studies'][f"{factor}-{outcome}"] = {
                    'papers': integration_count,
                    'integration_strength': 'Strong' if integration_count > 10 else 'Moderate' if integration_count > 3 else 'Emerging'
                }
                
                print(f"   🔗 {factor} → {outcome}: {integration_count} integrated studies")
    
    return synthesis

# Example: Analyze climate change and health connections
climate_health_synthesis = climate_health_research_synthesis(
    climate_factors=["extreme heat", "air pollution", "flooding", "drought"],
    health_outcomes=["cardiovascular disease", "respiratory illness", "mental health", "infectious disease"]
)
```

---

## Running These Examples

All examples are designed to be:
1. **Copy-paste ready** - Just replace email addresses
2. **Modular** - Use individual functions in larger workflows  
3. **Educational** - Comments explain the research logic
4. **Extensible** - Easy to modify for your specific needs

## Next Steps

- **Customize** these examples for your research domain
- **Combine** multiple examples into comprehensive workflows
- **Automate** using the scheduling features
- **Share** configurations with research collaborators

For more advanced examples, see:
- [Research Workflows](../research_workflows.md) - Complex multi-step workflows
- [Scientific Use Cases](../scientific_use_cases.md) - Domain-specific applications
- [Research Tutorial](../tutorials/research_getting_started.md) - Step-by-step learning