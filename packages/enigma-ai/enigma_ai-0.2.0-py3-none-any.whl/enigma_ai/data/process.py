import base64
import joblib
import requests
from tqdm.auto import tqdm
from ..utils import get_extensions_dict


def get_repo_files(repo_name, branch='master', github_token=None):
    """
    Retrieves a list of file paths in a GitHub repository.

    Args:
        repo_name (str): The full name of the repository (e.g., 'user/repo').
        branch (str, optional): The name of the branch to retrieve files from. Defaults to 'master'.
        github_token (str, optional): The GitHub API token for authentication.

    Returns:
        list: A list of file paths in the repository.
    """
    headers = {}
    headers['Authorization'] = f"token {github_token}"
    url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        res = r.json()
        files = [file["path"] for file in res["tree"]]
        return files
    elif branch == "master":
        files = get_repo_files(repo_name, branch="main", github_token=github_token)
        return files
    else:
        return None
    

def read_github_file(full_name, file_path, github_token=None):
    """
    Reads the content of a file in a GitHub repository.

    Args:
        full_name (str): The full name of the repository (e.g., 'user/repo').
        file_path (str): The path to the file in the repository.
        github_token (str, optional): The GitHub API token for authentication.

    Returns:
        str: The content of the file.
    """
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
        
    url = f'https://api.github.com/repos/{full_name}/contents/{file_path}'
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    try:
      file_content = data['content']
      file_content_encoding = data.get('encoding')
      if file_content_encoding == 'base64':
          file_content = base64.b64decode(file_content).decode()
      return file_content
    except:
      pass


def extract_code_from_repos(df, filename, token):
    """
    Extracts code files from the repositories in a dataframe and adds them to a new column.

    Args:
        df (pandas.DataFrame): A dataframe containing repository information.
        filename (str): The filename to use for saving the processed dataframe.
        token (str): The GitHub API token for authentication.

    Returns:
        pandas.DataFrame: The updated dataframe with a new 'code' column containing the extracted code files.
    """
    code_extensions_column_name_dict = get_extensions_dict()
    extracted_filename = filename.replace(".csv", "_with_code.joblib")
    repos_bar_tqdm = tqdm(total=len(df), desc="Extracting Code Files From Repos...", position=0, leave=True)
    all_contents = []
    for _, row in df.iterrows():
        repo_name = row['full_name']
        repo = repo_name
        contents = get_repo_files(repo, github_token=token)
        code_files_dict = {}
        code_files_bar_tqdm = tqdm(total=len(contents), desc=f"Extracting Code Files From {repo}...", position=1, leave=True)
        for code_filepath in contents:
            ext = code_filepath.split('.')[-1]
            if ext not in code_extensions_column_name_dict:
                programming_language = 'Misc'
            else:
                programming_language = code_extensions_column_name_dict[ext]
            raw_content = read_github_file(repo_name, code_filepath, github_token=token)
            if programming_language not in code_files_dict:
                code_files_dict[programming_language] = {}
            code_files_dict[programming_language][code_filepath] = raw_content
            code_files_bar_tqdm.update(1)
        repos_bar_tqdm.update(1)
        all_contents.append(code_files_dict)
    df['code'] = all_contents
    joblib.dump(df, extracted_filename)
    print(f"Finished and saved to {extracted_filename}")
    return df