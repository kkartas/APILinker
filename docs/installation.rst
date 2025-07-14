============
Installation
============

ApiLinker can be installed using pip:

.. code-block:: bash

    pip install apilinker

Development Installation
-----------------------

For development, clone the repository and install in development mode:

.. code-block:: bash

    git clone https://github.com/yourusername/APILinker.git
    cd APILinker
    pip install -e ".[dev]"

This will install all dependencies including development tools like pytest, flake8, and mypy.

Dependencies
-----------

ApiLinker depends on the following packages:

* httpx: Modern HTTP client
* pydantic: Data validation and settings management
* pyyaml: YAML parser
* typer: CLI interface
* croniter: Cron expression parser
* rich: Terminal formatting
