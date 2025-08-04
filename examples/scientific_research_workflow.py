"""
Scientific Research Workflow Example using ApiLinker.

This example demonstrates how researchers can use ApiLinker with 
scientific connectors to create automated research workflows.
"""

import os
from apilinker import ApiLinker
from apilinker.connectors.scientific.ncbi import NCBIConnector
from apilinker.connectors.scientific.arxiv import ArXivConnector


def example_pubmed_to_csv_workflow():
    """
    Example: Search PubMed for papers and export to CSV format.
    
    This workflow demonstrates how a researcher might:
    1. Search for recent papers on a specific topic
    2. Get detailed metadata for each paper
    3. Transform the data for analysis
    4. Export to a CSV file for further processing
    """
    
    print("🔬 PubMed Research Workflow Example")
    print("=" * 50)
    
    # Initialize ApiLinker with programmatic configuration
    linker = ApiLinker()
    
    # Set up NCBI source (replace with your email)
    research_email = "researcher@university.edu"  # Required by NCBI
    
    linker.add_source(
        type="rest",
        base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        endpoints={
            "search_pubmed": {
                "path": "/esearch.fcgi",
                "method": "GET",
                "params": {
                    "email": research_email,
                    "tool": "ApiLinker-Research",
                    "retmode": "json",
                    "db": "pubmed"
                }
            },
            "get_summaries": {
                "path": "/esummary.fcgi", 
                "method": "GET",
                "params": {
                    "email": research_email,
                    "tool": "ApiLinker-Research",
                    "retmode": "json",
                    "db": "pubmed"
                }
            }
        }
    )
    
    # Set up CSV target (simulated as a REST endpoint)
    linker.add_target(
        type="rest",
        base_url="https://httpbin.org",  # Using httpbin for demo
        endpoints={
            "save_csv": {
                "path": "/post",
                "method": "POST"
            }
        }
    )
    
    # Define data transformation mapping
    linker.add_mapping(
        source="search_pubmed",
        target="save_csv",
        fields=[
            {"source": "esearchresult.idlist", "target": "pubmed_ids"},
            {"source": "esearchresult.count", "target": "total_results"},
            {"source": "esearchresult.retmax", "target": "returned_results"}
        ]
    )
    
    # Alternative: Use the specialized NCBI connector directly
    print("\n📊 Using NCBI Connector directly:")
    
    ncbi = NCBIConnector(email=research_email)
    
    # Search for papers on CRISPR gene editing
    search_results = ncbi.search_pubmed(
        query="CRISPR gene editing",
        max_results=10,
        sort="date"
    )
    
    print(f"Found {len(search_results.get('esearchresult', {}).get('idlist', []))} papers")
    
    # Get detailed information for first few papers
    pubmed_ids = search_results.get('esearchresult', {}).get('idlist', [])[:5]
    
    if pubmed_ids:
        summaries = ncbi.get_article_summaries(pubmed_ids)
        print(f"Retrieved summaries for {len(pubmed_ids)} papers")
        
        # Example: Extract key information
        for paper_id in pubmed_ids:
            paper_info = summaries.get('result', {}).get(paper_id, {})
            title = paper_info.get('title', 'Unknown Title')
            authors = paper_info.get('authors', [])
            print(f"- {title} (Authors: {len(authors)})")


def example_arxiv_literature_review():
    """
    Example: Automated literature review using arXiv papers.
    
    This workflow shows how to:
    1. Search for recent papers in a specific field
    2. Filter by research area
    3. Extract and analyze paper metadata
    4. Create a structured literature review dataset
    """
    
    print("\n📚 arXiv Literature Review Workflow")
    print("=" * 50)
    
    # Initialize arXiv connector
    arxiv = ArXivConnector()
    
    # Search for recent machine learning papers
    ml_papers = arxiv.search_recent_papers(
        category="cs.LG",  # Machine Learning category
        max_results=20
    )
    
    print(f"Found {len(ml_papers)} recent ML papers")
    
    # Analyze the papers
    research_areas = {}
    for paper in ml_papers:
        for category in paper.get('categories', []):
            research_areas[category] = research_areas.get(category, 0) + 1
    
    print("\n🔍 Research Area Distribution:")
    for area, count in sorted(research_areas.items(), key=lambda x: x[1], reverse=True):
        print(f"  {area}: {count} papers")
    
    # Search for specific research topic
    print("\n🎯 Searching for 'transformer neural networks'...")
    transformer_papers = arxiv.search_papers(
        query="transformer neural network",
        max_results=10,
        sort_by="relevance"
    )
    
    print(f"Found {len(transformer_papers)} relevant papers:")
    for i, paper in enumerate(transformer_papers[:5], 1):
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
        print(f"   Categories: {', '.join(paper['categories'])}")
        print(f"   Date: {paper['published_date'][:10]}")
        print()


def example_cross_database_research():
    """
    Example: Cross-database research combining PubMed and arXiv.
    
    This demonstrates how to:
    1. Search multiple databases for the same topic
    2. Compare results across databases
    3. Identify complementary research perspectives
    """
    
    print("\n🔄 Cross-Database Research Workflow")
    print("=" * 50)
    
    research_topic = "neural network protein folding"
    
    # Search biomedical literature (PubMed)
    print(f"🧬 Searching PubMed for '{research_topic}'...")
    ncbi = NCBIConnector(email="researcher@university.edu")
    
    pubmed_results = ncbi.search_pubmed(
        query=research_topic,
        max_results=15
    )
    
    pubmed_count = len(pubmed_results.get('esearchresult', {}).get('idlist', []))
    print(f"   Found {pubmed_count} biomedical papers")
    
    # Search computer science literature (arXiv)
    print(f"💻 Searching arXiv for '{research_topic}'...")
    arxiv = ArXivConnector()
    
    arxiv_results = arxiv.search_papers(
        query=research_topic,
        max_results=15,
        category="cs.LG"  # Focus on machine learning
    )
    
    print(f"   Found {len(arxiv_results)} computer science papers")
    
    # Analyze temporal distribution
    if arxiv_results:
        years = {}
        for paper in arxiv_results:
            if paper.get('published_date'):
                year = paper['published_date'][:4]
                years[year] = years.get(year, 0) + 1
        
        print("\n📅 arXiv Papers by Year:")
        for year in sorted(years.keys()):
            print(f"   {year}: {years[year]} papers")
    
    print(f"\n📈 Research Insights:")
    print(f"   • Total papers found: {pubmed_count + len(arxiv_results)}")
    print(f"   • Biomedical focus: {pubmed_count} papers")
    print(f"   • Computational focus: {len(arxiv_results)} papers")
    print(f"   • Interdisciplinary opportunity: High (topic spans both domains)")


def example_researcher_collaboration_network():
    """
    Example: Building researcher collaboration networks.
    
    This shows how to:
    1. Find papers by specific researchers
    2. Identify frequent collaborators
    3. Map research networks
    """
    
    print("\n👥 Researcher Collaboration Network")
    print("=" * 50)
    
    # Search for papers by a specific researcher
    target_researcher = "Geoffrey Hinton"  # Example researcher name
    
    arxiv = ArXivConnector()
    
    # Find papers by this researcher
    papers = arxiv.search_by_author(target_researcher, max_results=20)
    
    print(f"📖 Found {len(papers)} papers by {target_researcher}")
    
    # Analyze collaborators
    collaborators = {}
    for paper in papers:
        authors = paper.get('authors', [])
        for author in authors:
            if author != target_researcher:
                collaborators[author] = collaborators.get(author, 0) + 1
    
    # Sort by collaboration frequency
    top_collaborators = sorted(
        collaborators.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    print(f"\n🤝 Top Collaborators with {target_researcher}:")
    for collaborator, count in top_collaborators:
        print(f"   {collaborator}: {count} joint papers")
    
    # Analyze research evolution
    if papers:
        recent_categories = set()
        for paper in papers[:5]:  # Most recent papers
            recent_categories.update(paper.get('categories', []))
        
        print(f"\n🔬 Recent Research Areas:")
        for category in sorted(recent_categories):
            print(f"   • {category}")


if __name__ == "__main__":
    """
    Run all example workflows.
    
    Note: These examples use real APIs. For actual research:
    1. Replace email addresses with your institutional email
    2. Consider getting NCBI API keys for higher rate limits
    3. Implement proper data storage and analysis
    4. Add error handling and logging
    """
    
    print("🚀 Scientific Research Workflows with ApiLinker")
    print("=" * 60)
    print()
    print("Note: This is a demonstration. Replace email addresses and")
    print("implement proper data storage for actual research use.")
    print()
    
    try:
        # Run workflow examples
        example_pubmed_to_csv_workflow()
        example_arxiv_literature_review()
        example_cross_database_research()
        example_researcher_collaboration_network()
        
        print("\n" + "=" * 60)
        print("✅ All workflow examples completed successfully!")
        print()
        print("Next steps for researchers:")
        print("• Customize queries for your research domain")
        print("• Implement data storage and analysis pipelines") 
        print("• Set up automated workflows with scheduling")
        print("• Integrate with your existing research tools")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("This is expected in a demo environment.")
        print("The code structure demonstrates the workflow patterns.")