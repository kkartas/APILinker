# Interactive Tutorial

Try ApiLinker in your browser with our interactive Jupyter notebook!

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kkartas/APILinker/HEAD?labpath=examples%2FApiLinker_Research_Tutorial.ipynb)

## What You'll Learn

This hands-on tutorial demonstrates:

1. **Basic API Integration**: Connect to NCBI/PubMed and fetch research papers
2. **Data Transformation**: Map fields and apply transformations
3. **Research Workflows**: Cross-platform literature search
4. **Visualization**: Plot citation networks and author collaborations

## Running Locally

If you prefer to run the notebook on your local machine:

```bash
git clone https://github.com/kkartas/APILinker.git
cd APILinker
pip install -e ".[dev]"
pip install jupyter matplotlib pandas
jupyter notebook examples/ApiLinker_Research_Tutorial.ipynb
```

## Notebook Contents

### Section 1: Installation & Setup
Learn how to install ApiLinker and verify the installation.

### Section 2: Basic Connectivity
Connect to the PubMed API and fetch your first research paper.

```python
from apilinker.connectors.scientific import NCBIConnector

ncbi = NCBIConnector(email="your-email@university.edu")
results = ncbi.search_pubmed("CRISPR gene editing", max_results=10)
```

### Section 3: Cross-Platform Research
Combine data from multiple research APIs (NCBI, arXiv, Semantic Scholar).

### Section 4: Data Visualization
Visualize research trends, citation networks, and co-authorship graphs.

### Section 5: Advanced Workflows
Build reproducible research pipelines with scheduling and error handling.

## Interactive Features

- **Live Code Execution**: Run and modify code directly in the browser
- **Instant Feedback**: See results immediately without installation
- **Visualization**: Generate charts and graphs
- **No Setup Required**: Powered by Binder for zero-config execution

## Troubleshooting

### Binder Not Loading?

If Binder takes too long to build, try:

1. **Refresh the page** and wait (first build can take 5-10 minutes)
2. **Run locally** using the instructions above
3. **View the notebook** on GitHub: [ApiLinker_Research_Tutorial.ipynb](https://github.com/kkartas/APILinker/blob/main/examples/ApiLinker_Research_Tutorial.ipynb)

## Feedback

Found issues with the tutorial? [Open an issue on GitHub](https://github.com/kkartas/APILinker/issues).
