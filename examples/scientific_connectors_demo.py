"""
Scientific Connectors Demo for ApiLinker.

This demo shows how to use the new scientific API connectors
to access research databases like NCBI and arXiv.
"""

from apilinker import NCBIConnector, ArXivConnector


def demo_ncbi_connector():
    """
    Demonstrate NCBI connector capabilities.
    """
    print("🧬 NCBI Connector Demo")
    print("=" * 30)
    
    # Initialize NCBI connector (replace with your email)
    ncbi = NCBIConnector(
        email="researcher@university.edu",  # Required by NCBI
        tool_name="ApiLinker-Demo"
    )
    
    print("Connector initialized successfully!")
    print(f"Base URL: {ncbi.base_url}")
    print(f"Available endpoints: {list(ncbi.endpoints.keys())}")
    
    # Note: Actual API calls would require network connection
    # This demo shows the interface structure
    
    print("\n📚 Example Usage:")
    print("# Search PubMed for CRISPR papers")
    print("results = ncbi.search_pubmed('CRISPR gene editing', max_results=10)")
    
    print("\n# Search GenBank for BRCA1 sequences")  
    print("sequences = ncbi.search_genbank('BRCA1 Homo sapiens')")
    
    print("\n# Get article summaries")
    print("summaries = ncbi.get_article_summaries(['12345', '67890'])")


def demo_arxiv_connector():
    """
    Demonstrate arXiv connector capabilities.
    """
    print("\n📄 arXiv Connector Demo")
    print("=" * 30)
    
    # Initialize arXiv connector (no authentication required)
    arxiv = ArXivConnector()
    
    print("Connector initialized successfully!")
    print(f"Base URL: {arxiv.base_url}")
    print(f"Available endpoints: {list(arxiv.endpoints.keys())}")
    
    print("\n🔍 Example Usage:")
    print("# Search for machine learning papers")
    print("papers = arxiv.search_papers('machine learning', max_results=20)")
    
    print("\n# Get specific paper by ID")
    print("paper = arxiv.get_paper_by_id('2301.00001')")
    
    print("\n# Search by author")
    print("author_papers = arxiv.search_by_author('Geoffrey Hinton')")
    
    print("\n# Get recent papers in AI category")
    print("recent = arxiv.search_recent_papers('cs.AI', days_back=7)")


def demo_integrated_workflow():
    """
    Demonstrate how scientific connectors integrate with ApiLinker.
    """
    print("\n🔄 Integrated Research Workflow Demo")
    print("=" * 40)
    
    from apilinker import ApiLinker
    
    # Create ApiLinker instance
    linker = ApiLinker()
    
    print("✅ ApiLinker initialized")
    print("✅ Scientific connectors available")
    
    print("\n📝 Workflow Example:")
    print("1. Search arXiv for recent AI papers")
    print("2. Extract author names and research topics") 
    print("3. Search PubMed for biomedical applications")
    print("4. Cross-reference and analyze findings")
    print("5. Generate research summary report")
    
    print("\n💡 Research Use Cases:")
    print("• Literature reviews across multiple databases")
    print("• Citation analysis and collaboration networks")
    print("• Interdisciplinary research discovery")
    print("• Automated research monitoring and alerts")
    print("• Data collection for meta-analyses")


def show_research_examples():
    """
    Show specific research examples that benefit from scientific connectors.
    """
    print("\n🔬 Research Domain Examples")
    print("=" * 35)
    
    examples = {
        "Bioinformatics": [
            "Search PubMed for gene function studies",
            "Retrieve GenBank sequences for analysis", 
            "Cross-reference genomic variants with literature"
        ],
        "Computer Science": [
            "Monitor arXiv for new ML architectures",
            "Track citation networks in AI research",
            "Analyze research trend evolution"
        ],
        "Interdisciplinary": [
            "Find AI applications in biology papers",
            "Identify computational methods in medicine",
            "Map technology transfer from CS to other fields"
        ]
    }
    
    for domain, use_cases in examples.items():
        print(f"\n{domain}:")
        for use_case in use_cases:
            print(f"  • {use_case}")


if __name__ == "__main__":
    """
    Run the scientific connectors demo.
    """
    print("🚀 ApiLinker Scientific Connectors Demo")
    print("=" * 50)
    
    try:
        demo_ncbi_connector()
        demo_arxiv_connector() 
        demo_integrated_workflow()
        show_research_examples()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\nNext Steps:")
        print("• Try the examples/scientific_research_workflow.py")
        print("• Customize connectors for your research domain")
        print("• Integrate with your existing research pipeline")
        print("• Check the documentation for advanced features")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Scientific connectors may not be properly installed.")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("This is expected in a demonstration environment.")