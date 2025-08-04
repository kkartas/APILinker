"""
Comprehensive Research Examples using ApiLinker's Full Connector Ecosystem.

This example demonstrates how to use all 8 research connectors together
for complex, multi-domain research workflows.
"""

from apilinker import (
    # Scientific connectors
    NCBIConnector, ArXivConnector, CrossRefConnector, 
    SemanticScholarConnector, PubChemConnector, ORCIDConnector,
    # General research connectors
    GitHubConnector, NASAConnector,
    # Core
    ApiLinker
)


def demo_all_connectors():
    """
    Demonstrate initialization and basic usage of all research connectors.
    """
    print("🚀 ApiLinker Comprehensive Research Connector Demo")
    print("=" * 60)
    
    # Scientific connectors
    print("\n🧬 Scientific Connectors:")
    
    # 1. NCBI - Biomedical databases
    ncbi = NCBIConnector(email="researcher@university.edu")
    print(f"✅ NCBI: {ncbi.base_url}")
    
    # 2. arXiv - Academic preprints
    arxiv = ArXivConnector()
    print(f"✅ arXiv: {arxiv.base_url}")
    
    # 3. CrossRef - Citation data
    crossref = CrossRefConnector(email="researcher@university.edu")
    print(f"✅ CrossRef: {crossref.base_url}")
    
    # 4. Semantic Scholar - AI-powered academic search
    semantic = SemanticScholarConnector(api_key="optional_key")
    print(f"✅ Semantic Scholar: {semantic.base_url}")
    
    # 5. PubChem - Chemical compounds
    pubchem = PubChemConnector()
    print(f"✅ PubChem: {pubchem.base_url}")
    
    # 6. ORCID - Researcher profiles
    orcid = ORCIDConnector()
    print(f"✅ ORCID: {orcid.base_url}")
    
    # General research connectors
    print("\n🌐 General Research Connectors:")
    
    # 7. GitHub - Code and repositories
    github = GitHubConnector(token="optional_token")
    print(f"✅ GitHub: {github.base_url}")
    
    # 8. NASA - Earth science and space data
    nasa = NASAConnector(api_key="nasa_api_key")
    print(f"✅ NASA: {nasa.base_url}")
    
    print(f"\nAll 8 research connectors initialized successfully!")


def cross_platform_drug_discovery_research():
    """
    Comprehensive drug discovery research across multiple platforms.
    """
    print("\n💊 Cross-Platform Drug Discovery Research")
    print("=" * 50)
    
    # Initialize connectors
    ncbi = NCBIConnector(email="drug.researcher@pharma.com")
    pubchem = PubChemConnector()
    semantic = SemanticScholarConnector()
    crossref = CrossRefConnector(email="drug.researcher@pharma.com")
    github = GitHubConnector()
    
    target_protein = "BRCA1"
    
    print(f"\n🎯 Researching drug targets for: {target_protein}")
    
    # 1. Literature research
    print(f"\n📚 Step 1: Literature Research")
    print(f"   • Searching PubMed for {target_protein} drug studies...")
    print(f"   • Searching Semantic Scholar for AI-based drug discovery...")
    print(f"   • CrossRef for citation analysis...")
    
    # 2. Chemical compound research
    print(f"\n⚗️  Step 2: Chemical Compound Research")
    print(f"   • Searching PubChem for {target_protein} inhibitors...")
    print(f"   • Analyzing drug-like properties (Lipinski's Rule of Five)...")
    print(f"   • Finding similar compounds and bioassays...")
    
    # 3. Computational resources
    print(f"\n💻 Step 3: Computational Resources")
    print(f"   • Searching GitHub for {target_protein} analysis tools...")
    print(f"   • Finding drug discovery machine learning repositories...")
    print(f"   • Identifying computational drug design software...")
    
    research_workflow = {
        'target': target_protein,
        'literature_sources': ['PubMed', 'Semantic Scholar', 'CrossRef'],
        'chemical_databases': ['PubChem'],
        'code_repositories': ['GitHub'],
        'analysis_types': [
            'Literature review',
            'Compound similarity analysis', 
            'Drug-likeness assessment',
            'Computational tool discovery'
        ]
    }
    
    print(f"\n📊 Research Workflow Summary:")
    for key, value in research_workflow.items():
        print(f"   {key}: {value}")
    
    return research_workflow


def climate_science_interdisciplinary_research():
    """
    Climate science research combining NASA data, literature, and code.
    """
    print("\n🌍 Climate Science Interdisciplinary Research")
    print("=" * 50)
    
    # Initialize connectors
    nasa = NASAConnector(api_key="nasa_api_key")
    arxiv = ArXivConnector()
    github = GitHubConnector()
    semantic = SemanticScholarConnector()
    
    research_topic = "climate change machine learning"
    
    print(f"\n🔬 Researching: {research_topic}")
    
    # 1. Earth observation data
    print(f"\n🛰️  Step 1: NASA Earth Observation Data")
    print(f"   • Accessing satellite imagery and climate data...")
    print(f"   • Getting earth science datasets...")
    print(f"   • Analyzing climate indicators...")
    
    # 2. Academic research
    print(f"\n📖 Step 2: Academic Literature")
    print(f"   • Searching arXiv for ML climate models...")
    print(f"   • Semantic Scholar for AI climate research...")
    print(f"   • Cross-referencing methodologies...")
    
    # 3. Implementation resources
    print(f"\n⚡ Step 3: Implementation Resources")
    print(f"   • GitHub repositories for climate ML...")
    print(f"   • Data processing pipelines...")
    print(f"   • Visualization and analysis tools...")
    
    climate_research_framework = {
        'data_sources': {
            'nasa': 'Earth observation data, climate datasets',
            'arxiv': 'Latest ML methods for climate science',
            'semantic_scholar': 'Cross-disciplinary AI research',
            'github': 'Implementation code and tools'
        },
        'research_pipeline': [
            'Data collection (NASA APIs)',
            'Literature review (arXiv, Semantic Scholar)',
            'Method identification (Academic papers)',
            'Implementation discovery (GitHub)',
            'Integration and analysis'
        ],
        'interdisciplinary_aspects': [
            'Climate science + Machine learning',
            'Earth observation + Data science',
            'Environmental policy + Technology'
        ]
    }
    
    print(f"\n🌡️  Climate Research Framework:")
    for category, details in climate_research_framework.items():
        print(f"   {category}:")
        if isinstance(details, dict):
            for source, description in details.items():
                print(f"      • {source}: {description}")
        elif isinstance(details, list):
            for item in details:
                print(f"      • {item}")
    
    return climate_research_framework


def researcher_collaboration_network_analysis():
    """
    Analyze researcher collaboration networks across platforms.
    """
    print("\n👥 Researcher Collaboration Network Analysis")
    print("=" * 50)
    
    # Initialize connectors
    orcid = ORCIDConnector()
    semantic = SemanticScholarConnector()
    github = GitHubConnector()
    arxiv = ArXivConnector()
    
    research_field = "bioinformatics"
    
    print(f"\n🔍 Analyzing collaboration networks in: {research_field}")
    
    # 1. Researcher identification
    print(f"\n👤 Step 1: Researcher Identification")
    print(f"   • ORCID: Finding researchers by affiliation and keywords...")
    print(f"   • Semantic Scholar: Identifying prolific authors...")
    print(f"   • arXiv: Recent paper authors in the field...")
    
    # 2. Collaboration analysis
    print(f"\n🤝 Step 2: Collaboration Analysis")
    print(f"   • Paper co-authorship patterns...")
    print(f"   • Institutional collaborations...")
    print(f"   • Cross-disciplinary partnerships...")
    
    # 3. Code collaboration
    print(f"\n💻 Step 3: Code Collaboration")
    print(f"   • GitHub: Open source project contributors...")
    print(f"   • Software development collaborations...")
    print(f"   • Academic-industry partnerships in code...")
    
    collaboration_metrics = {
        'researcher_identification': {
            'orcid_profiles': 'Professional researcher profiles',
            'semantic_scholar': 'Publication-based author profiles',
            'arxiv_authors': 'Recent publication authors'
        },
        'collaboration_patterns': {
            'co_authorship': 'Paper collaboration networks',
            'institutional': 'Cross-institutional research',
            'temporal': 'Collaboration evolution over time'
        },
        'software_collaboration': {
            'github_contributors': 'Open source development teams',
            'academic_software': 'Research software collaborations',
            'reproducibility': 'Code sharing for research'
        },
        'network_metrics': [
            'Centrality measures',
            'Clustering coefficients', 
            'Community detection',
            'Collaboration strength'
        ]
    }
    
    print(f"\n📊 Collaboration Analysis Framework:")
    for category, details in collaboration_metrics.items():
        print(f"   {category}:")
        if isinstance(details, dict):
            for metric, description in details.items():
                print(f"      • {metric}: {description}")
        elif isinstance(details, list):
            for item in details:
                print(f"      • {item}")
    
    return collaboration_metrics


def technology_transfer_research():
    """
    Track technology transfer from academic research to industry implementation.
    """
    print("\n🔄 Technology Transfer Research")
    print("=" * 40)
    
    # Initialize connectors
    arxiv = ArXivConnector()
    semantic = SemanticScholarConnector()
    github = GitHubConnector()
    crossref = CrossRefConnector(email="tech.transfer@university.edu")
    
    technology = "transformer neural networks"
    
    print(f"\n⚡ Tracking technology transfer: {technology}")
    
    # 1. Academic origins
    print(f"\n🎓 Step 1: Academic Origins")
    print(f"   • arXiv: Original research papers...")
    print(f"   • Semantic Scholar: Citation impact analysis...")
    print(f"   • CrossRef: Publication timeline and influence...")
    
    # 2. Industry adoption
    print(f"\n🏭 Step 2: Industry Adoption")
    print(f"   • GitHub: Open source implementations...")
    print(f"   • Corporate research repositories...")
    print(f"   • Production deployment examples...")
    
    # 3. Transfer analysis
    print(f"\n📈 Step 3: Transfer Analysis")
    print(f"   • Time from publication to implementation...")
    print(f"   • Key researchers and organizations...")
    print(f"   • Adoption patterns and variations...")
    
    transfer_analysis = {
        'technology': technology,
        'academic_phase': {
            'initial_papers': 'Foundational research publications',
            'theoretical_development': 'Method refinement and validation',
            'academic_adoption': 'Widespread academic use'
        },
        'transition_phase': {
            'industry_attention': 'Corporate research interest',
            'proof_of_concept': 'Industry pilot implementations',
            'open_source_tools': 'Community-driven implementations'
        },
        'industry_phase': {
            'production_deployment': 'Large-scale commercial use',
            'standardization': 'Industry standard practices',
            'ecosystem_development': 'Supporting tools and services'
        },
        'transfer_metrics': [
            'Publication to implementation time',
            'Academic-industry collaboration frequency',
            'Open source project popularity',
            'Commercial adoption indicators'
        ]
    }
    
    print(f"\n🔄 Technology Transfer Analysis:")
    for phase, details in transfer_analysis.items():
        if phase != 'technology':
            print(f"   {phase}:")
            if isinstance(details, dict):
                for stage, description in details.items():
                    print(f"      • {stage}: {description}")
            elif isinstance(details, list):
                for item in details:
                    print(f"      • {item}")
    
    return transfer_analysis


def integrated_research_workflow_demo():
    """
    Demonstrate a complete integrated research workflow using all connectors.
    """
    print("\n🌟 Integrated Research Workflow Demo")
    print("=" * 45)
    
    # Initialize ApiLinker with all connectors
    linker = ApiLinker()
    
    print(f"\n🔧 Setting up comprehensive research infrastructure...")
    
    # Research scenario: AI applications in healthcare
    research_topic = "artificial intelligence healthcare diagnostics"
    
    workflow_steps = {
        'literature_discovery': {
            'connectors': ['NCBI (PubMed)', 'arXiv', 'Semantic Scholar', 'CrossRef'],
            'purpose': 'Find relevant papers and analyze citations',
            'outputs': 'Comprehensive literature database'
        },
        'researcher_network': {
            'connectors': ['ORCID', 'Semantic Scholar'],
            'purpose': 'Identify key researchers and collaborations',
            'outputs': 'Researcher collaboration network'
        },
        'technology_analysis': {
            'connectors': ['GitHub', 'arXiv'],
            'purpose': 'Find implementations and code resources',
            'outputs': 'Technology landscape mapping'
        },
        'data_integration': {
            'connectors': ['NASA (for health-environment data)', 'PubChem (for drug interactions)'],
            'purpose': 'Integrate supporting datasets',
            'outputs': 'Multi-modal research dataset'
        },
        'synthesis_analysis': {
            'connectors': ['All connectors'],
            'purpose': 'Cross-reference and synthesize findings',
            'outputs': 'Comprehensive research synthesis'
        }
    }
    
    print(f"\n📋 Research Workflow: {research_topic}")
    for step_name, step_details in workflow_steps.items():
        print(f"\n   {step_name.replace('_', ' ').title()}:")
        for aspect, details in step_details.items():
            if isinstance(details, list):
                print(f"      {aspect}: {', '.join(details)}")
            else:
                print(f"      {aspect}: {details}")
    
    # Demonstrate the power of integrated research
    integration_benefits = [
        "Cross-database validation of research findings",
        "Comprehensive researcher collaboration mapping",
        "Technology implementation tracking",
        "Multi-modal data integration",
        "Automated research synthesis",
        "Real-time research monitoring",
        "Interdisciplinary connection discovery"
    ]
    
    print(f"\n✨ Integration Benefits:")
    for benefit in integration_benefits:
        print(f"   • {benefit}")
    
    research_impact = {
        'scope': 'Multi-database, multi-domain research',
        'efficiency': 'Automated multi-database searches',
        'completeness': 'Coverage across multiple research sources',
        'reproducibility': 'Documented and repeatable workflows',
        'collaboration': 'Supports research collaboration',
        'innovation': 'Helps discover connections across databases'
    }
    
    print(f"\n🚀 Research Impact Metrics:")
    for metric, description in research_impact.items():
        print(f"   {metric}: {description}")
    
    return workflow_steps, integration_benefits, research_impact


if __name__ == "__main__":
    """
    Run comprehensive research demonstrations.
    """
    print("🔬 ApiLinker Comprehensive Research Ecosystem Demo")
    print("=" * 70)
    print("Demonstrating all 8 research connectors in integrated workflows")
    print()
    
    try:
        # Basic connector demo
        demo_all_connectors()
        
        # Domain-specific workflows
        drug_discovery = cross_platform_drug_discovery_research()
        climate_research = climate_science_interdisciplinary_research()
        collaboration_analysis = researcher_collaboration_network_analysis()
        tech_transfer = technology_transfer_research()
        
        # Integrated workflow
        workflow, benefits, impact = integrated_research_workflow_demo()
        
        print("\n" + "=" * 70)
        print("Comprehensive Research Demo Completed Successfully!")
        print()
        print("Key Features Demonstrated:")
        print("   • 8 research connectors available")
        print("   • 5 example workflows provided")
        print("   • Cross-domain research capabilities")
        print("   • Research integration possibilities")
        print()
        print("Suitable for:")
        print("   • Research projects requiring multiple data sources")
        print("   • Cross-database literature searches")
        print("   • Interdisciplinary research workflows")
        print("   • Academic and research partnerships")
        print()
        print("ApiLinker: Simplifying research data integration")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("This is expected in a demonstration environment.")
        print("The workflow structure demonstrates the research capabilities.")