# enigma_ai Development Guide

## Package Structure

The package is structured as follows:

```
enigma_ai/
    __init__.py
    data/
        __init__.py
        scrape.py
        process.py
    finetuning/  
        __init__.py
        params.py
        train.py
    models/
        __init__.py
        peft.py
    utils.py
```

- `data/` is for the code scraping and processing functionality.
- `finetuning/` is for estimating training hyperparameters and fine-tuning models.
- `models/` is for custom model implementations and utilities.

## Local Development

To develop and test your changes locally, follow these steps:

1. Ensure you have the latest version of the package pulled from the repository.

2. Traverse to the parent directory of the package Customizable-Code-Assistant.

3. Install the package in editable mode:

```bash
pip install -e .
```

4. Make your changes to the relevant files in the package directory.

5. To test your changes, import and use the package as you would normally:

```python
from enigma_ai import your_module

# Use your module
```

## Pushing a New Version

1. Update the version number in `setup.py`.

2. Push your changes to the main branch.

3. Build the distribution (again after traversing to the parent directory of the package Customizable-Code-Assistant):

```bash
python -m build
```

4. Upload the package to PyPI:

```bash
python -m twine upload dist/*
```

5. When prompted, use the project token to authenticate as follows:

```bash
Username: __token__
Password: <project token>
``` 

5. Verify that the new version is available on PyPI by :
    
```bash
pip install enigma_ai
```

## Testing the Code Search Utility

To test the code search functionality, follow these steps:

1. Pip install the package:

```bash
pip install enigma_ai
```

2. Run the scraping script:

```python
from enigma_ai.data import scrape

# Set up your GitHub API token
github_token = 'your_github_api_token'

# Define your search query and parameters
search_term = 'pentest'
max_results = 100
filename = 'fetched_repos.csv'

# Fetch repositories matching the query
repos_df = scrape.fetch_repos(github_token, max_results, filename, search_term, min_stars=100)

# The 'repos_df' dataframe now contains information about the fetched repositories
```

3. Run the code extraction script:
```python
from enigma_ai.data import process
import pandas as pd

# Load the previously fetched repository data
filename = 'fetched_repos.csv'
repos_df = pd.read_csv(filename)

#Limit the number of repositories to process
repos_df = repos_df.head(1)

# Extract code files from the repositories
repos_with_code = process.extract_code_from_repos(repos_df, filename, github_token)

#Print the first 1000 characters of the README.md file of the first repository
print(repos_with_code['code'].values[0]['Markdown']['README.md'][:1000])
```

4. You can now inspect the `repos_with_code` dataframe to see the fetched repositories and extracted code files.
