import requests
import pandas as pd
from tqdm.auto import tqdm
from ..utils import GitHubRepoSearchQueryBuilder, get_query_args



def get_repos_in_page(page_num, token, query):
    """
    Fetches a page of repositories from GitHub based on the provided query.
    Args:
        page_num (int): The page number to fetch.
        token (str): The GitHub API token for authentication.
        query (str): The search query to use.
    Returns:
        list: A list of dictionaries containing information about the fetched repositories.
    """
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }

    params = {
        'q': query,
        'page': page_num
    }

    res = requests.get('https://api.github.com/search/repositories', params=params, headers=headers)
    if res.status_code == 200:
        return res.json()["items"]
    else:
        print(f"Failed to fetch page {page_num} of repositories: {res.status_code}")
        print(res.text)
        return None

def search_github_repos(query, max_results, token):
    """
    Searches GitHub for repositories based on the given query.
    Returns a dataframe containing information about the matched repositories.

    Args:
        query (str): The search query to use.
        max_results (int): The maximum number of repositories to return.
        token (str): The GitHub API token for authentication.

    Returns:
        pandas.DataFrame: A dataframe containing information about the matched repositories.
    """
    num_pages = max_results//30
    if max_results % 30 > 0:
        num_pages += 1

    outputs = []
    for page in tqdm(range(num_pages), desc="Fetching Repositories", total=num_pages):
        print(f'fetching repositories: {min(len(outputs), max_results)}')
        repos = get_repos_in_page(page, token, query)
        if repos:
            outputs.extend(repos)
    outputs = outputs[:max_results]
    repos_df = extract_repo_info(outputs)
    print(f'fetched {len(repos_df)} repositories')
    return repos_df

def extract_repo_info(repos_list):
    """
    Extracts basic information from a list of GitHub repositories.
    Args:
        repos_list (list): A list of dictionaries containing information about GitHub repositories.

    Returns:
        pandas.DataFrame: A dataframe containing basic information about the repositories.
    """
    df = pd.DataFrame(repos_list)
    df = df[["full_name", "html_url", "description", "stargazers_count", "forks_count", "updated_at", "created_at", "owner", "topics", "size", "language", "license"]]
    return df

def fetch_repos(token, max_results, filename, search_term, **args): 
    """
    Fetches repositories from GitHub based on the provided search term and query arguments.
    Saves the fetched repositories to a CSV file.

    Args:
        token (str): The GitHub API token for authentication.
        max_results (int): The maximum number of repositories to return.
        filename (str): The name of the file to save the fetched repositories to.
        search_term (str): The search term to use.
        **args: Additional keyword arguments to use as query parameters these include:
            - name (bool): if True, the search term will be matched against the repository name.
            - description (bool): if True, the search term will be matched against the repository description.
            - readme (bool): if True, the search term will be matched against the repository readme.
            - topics (bool): if True, the search term will be matched against the repository topics.
            - owner (str): Specifies the owner of the repositories.
            - repo_name (str): Specifies the name of the repository.
            - user (str): Specifies the user of the repositories.
            - min_size (int): Specifies the minimum size of the repository.
            - max_size (int): Specifies the maximum size of the repository.
            - min_forks (int): Specifies the minimum number of forks of the repository.
            - max_forks (int): Specifies the maximum number of forks of the repository.
            - min_stars (int): Specifies the minimum number of stars of the repository.
            - max_stars (int): Specifies the maximum number of stars of the repository.
            - min_created (datetime.date): Specifies the minimum creation date of the repository.
            - max_created (datetime.date): Specifies the maximum creation date of the repository.
            - language (str): Specifies the language of the repository.
            - topic (str): Specifies the topic of the repository.
            - license (str): Specifies the license of the repository.
    Returns:
        pandas.DataFrame: A dataframe containing information about the fetched repositories.
    """
    qb_obj = GitHubRepoSearchQueryBuilder()
    query_args = get_query_args(**args)
    query_args['value'] = search_term
    qb_obj.init_from_args(query_args)
    query = qb_obj.build()
    print(f"The Full Query is: {query}")

    df = search_github_repos(query,  max_results, token)
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")
    return df
