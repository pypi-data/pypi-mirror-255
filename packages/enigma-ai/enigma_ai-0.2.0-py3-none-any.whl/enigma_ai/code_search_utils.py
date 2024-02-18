import base64
import joblib
import datetime
import requests
import pandas as pd
from tqdm.auto import tqdm


class GitHubRepoSearchQueryBuilder:
    def __init__(self):
        self.query_params = {}

    def init_from_args(self, args):
        value = args['value']

        search_in = ''
        prefix = ' in:'
        if args['name']:
            search_in += f'{prefix}name'
            prefix = ','
        if args['description']:
            search_in += f'{prefix}description'
            prefix = ','
        if args['readme']:
            search_in += f'{prefix}readme'
            prefix = ','
        if args['topics']:
            search_in += f'{prefix}topics'
            prefix = ','

        self.query_params[value] = search_in

        if 'owner' in args and 'name' in args:
            self.query_params['repo:'] = f'{args["owner"]}/{args["name"]}'
            
        if 'user' in args:
            self.query_params['user:'] = args['user']

        if 'min_size' in args and 'max_size' in args:
            self.query_params['size:'] = f'{args["min_size"]}..{args["max_size"]}'
        elif 'min_size' in args:
            self.query_params['size:'] = f'>{args["min_size"]}'
        elif 'max_size' in args:
            self.query_params['size:'] = f'<{args["max_size"]}'

        if 'min_forks' in args and 'max_forks' in args:
            self.query_params['forks:'] = f'{args["min_forks"]}..{args["max_forks"]}'
        elif 'min_forks' in args:
            self.query_params['forks:'] = f'>{args["min_forks"]}'
        elif 'max_forks' in args:
            self.query_params['forks:'] = f'<{args["max_forks"]}'

        if 'min_stars' in args and 'max_stars' in args:
            self.query_params['stars:'] = f'{args["min_stars"]}..{args["max_stars"]}'
        elif 'min_stars' in args:
            self.query_params['stars:'] = f'>{args["min_stars"]}'
        elif 'max_stars' in args:
            self.query_params['stars:'] = f'<{args["max_stars"]}'

        if 'min_created' in args and 'max_created' in args:
            self.query_params['created:'] = f'{args["min_created"]}..{args["max_created"]}'
        elif 'min_created' in args:
            self.query_params['created:'] = f'>{args["min_created"]}'
        elif 'max_created' in args:
            self.query_params['created:'] = f'<{args["max_created"]}'

        if 'license' in args:
            self.query_params['license:'] = args['license']

        if 'language' in args:
            self.query_params['language:'] = args['language']

        if 'topic' in args:
            self.query_params['topic:'] = args['topic']


    def build(self):
        full_query = ''
        for key, value in self.query_params.items():
            full_query += f'{key}{value} '
        return full_query.strip()


def get_repos_in_page(page_num, token, query):
  headers = {
      'Accept': 'application/vnd.github+json',
      'Authorization': f'Bearer {token}',
      'X-GitHub-Api-Version': '2022-11-28',
  }

  params = {
      'q': query,
      'page' : page_num
  }

  res = requests.get('https://api.github.com/search/repositories', params=params, headers=headers)
  if res.status_code == 200:
    return res.json()["items"]
  else:
      return None


def extract_repo_info(repos_list):
    """Extract info for a single repo"""
    df = pd.DataFrame(repos_list)
    df = df[["full_name", "html_url", "description", "stargazers_count", "forks_count", "updated_at", "created_at", "owner", "topics", "size", "language", "license"]]
    return df
    

def call_github_api(query, max_results, token):
    num_pages = max_results//30
    if max_results % 30 > 0:
        num_pages += 1

    outputs = []
    for page in range(num_pages):
        print(f'fetching repositories: {min(len(outputs), max_results)}')
        repos = get_repos_in_page(page, token, query)
        if repos:
            outputs.extend(repos)
    outputs = outputs[:max_results]
    repos_df = extract_repo_info(outputs)
    return repos_df


def get_repo_files(repo_name, branch = "master", github_token=None):
    headers = {}
    headers['Authorization'] = f"token {github_token}"
    url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1"
    r = requests.get(url, headers = headers)
    if r.status_code == 200:
        res = r.json()
        files = [file["path"] for file in res["tree"]]
        return files
    elif branch == "master":
        files = get_repo_files(repo_name, branch = "main", github_token = github_token)
        return files
    else:
        return None


def github_read_file(full_name, file_path, github_token=None):
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


def get_query_args(name, description, readme, topics, owner, repo_name, user,
                   min_size, max_size, min_forks, max_forks, min_stars, max_stars,
                   min_created, max_created, language, topic, license,
                   default_text="skip", default_number=666, default_date=datetime.date(2000, 1, 1)):
        query_args = {
            'name': name,
            'description': description,
            'readme': readme,
            'topics': topics
        }
        if owner != default_text and repo_name != default_text:
            query_args['owner'] = owner
            query_args['name'] = repo_name
        if user != default_text:
            query_args['user'] = user
        if min_size != default_number:
            query_args['min_size'] = min_size
        if max_size != default_number:
            query_args['max_size'] = max_size
        if min_forks != default_number:
            query_args['min_forks'] = min_forks
        if max_forks != default_number:
            query_args['max_forks'] = max_forks
        if min_stars != default_number:
            query_args['min_stars'] = min_stars
        if max_stars != default_number:
            query_args['max_stars'] = max_stars
        if min_created != default_date:
            query_args['min_created'] = min_created
        if max_created != default_date:
            query_args['max_created'] = max_created
        if language != default_text:
            query_args['language'] = language
        if topic != default_text:
            query_args['topic'] = topic
        if license != default_text:
            query_args['license'] = license
        return query_args


def extract_code_fun(df, filename, token):
    code_extensions_column_name_dict = {
        'py': 'Python',
        'ipynb': 'Python',
        'rmd': 'R',
        'r': 'R',
        'scala': 'Scala',
        'java': 'Java',
        'js': 'JavaScript',
        'go': 'Go',

        'c': 'C',
        'cpp': 'C++',
        'cs': 'C#',


        'html': 'HTML',
        'css': 'CSS',
        'php': 'PHP',

        'rb': 'Ruby',
        'pl': 'Perl',
        'jl': 'Julia',
        'kt': 'Kotlin',
        'swift': 'Swift',
        'vb': 'Visual Basic',
        'vba': 'Visual Basic',
        'vbnet': 'Visual Basic',
        'vb.net': 'Visual Basic',
        'ts': 'TypeScript',
        'tsx': 'TypeScript',
        'jsx': 'JavaScript',
        'tsx': 'TypeScript',
        'dart': 'Dart',
        'lua': 'Lua',
        'sh': 'Shell',
        'bash': 'Shell',
        'ps1': 'PowerShell',
        'psm1': 'PowerShell',
        'psd1': 'PowerShell',
        'ps1xml': 'PowerShell',
        'psc1': 'PowerShell',
        'psrc': 'PowerShell',
        'pp': 'Pascal',
        'pas': 'Pascal',
        'pl': 'Perl',
        'pm': 'Perl',
        't': 'Perl',
        'pod': 'Perl',
        

        'sql': 'SQL',
        'sh': 'Shell',
        'json': 'JSON',
        'xml': 'XML',
        'yml': 'YAML',
        'yaml': 'YAML',
        'md': 'Markdown',
        'txt': 'Text',
        'cfg': 'Config',
        'ini': 'Config',
        'conf': 'Config',
        'cfg': 'Config',
        'gitignore': 'Config',
        'gitattributes': 'Config',
        'gitmodules': 'Config',
        'gitkeep': 'Config',
        'gitconfig': 'Config',
        'git': 'Config',
    }
    extracted_filename = filename.replace(".csv", "_with_code.joblib")
    repos_bar_tqdm = tqdm(total=len(df), desc="Extracting Code Files From Repos...", position=0, leave=True)
    all_contents = []
    for _, row in df.iterrows():
        repo_name = row['full_name']
        repo = repo_name
        contents = get_repo_files(repo, github_token = token)
        code_files_dict = {}
        code_files_bar_tqdm = tqdm(total=len(contents), desc=f"Extracting Code Files From {repo}...", position=1, leave=True)
        for code_filepath in contents:
            ext = code_filepath.split('.')[-1]
            if ext not in code_extensions_column_name_dict:
                programming_language = 'Misc'
            else:
                programming_language = code_extensions_column_name_dict[ext]
            raw_content = github_read_file(repo_name, code_filepath, github_token=token)
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



def fetch_repos(token, max_results, filename, search_term,args={}):
    name = args['name'] if 'name' in args else False
    description = args['description'] if 'description' in args else False
    readme = args['readme'] if 'readme' in args else False
    topics = args['topics'] if 'topics' in args else False
    owner = args['owner'] if 'owner' in args else 'skip'
    repo_name = args['repo_name'] if 'repo_name' in args else 'skip'
    user = args['user'] if 'user' in args else 'skip'
    min_size = args['min_size'] if 'min_size' in args else 666
    max_size = args['max_size'] if 'max_size' in args else 666
    min_forks = args['min_forks'] if 'min_forks' in args else 666
    max_forks = args['max_forks'] if 'max_forks' in args else 666
    min_stars = args['min_stars'] if 'min_stars' in args else 666
    max_stars = args['max_stars'] if 'max_stars' in args else 666
    min_created = args['min_created'] if 'min_created' in args else datetime.date(2000, 1, 1)
    max_created = args['max_created'] if 'max_created' in args else datetime.date(2000, 1, 1)
    language = args['language'] if 'language' in args else 'skip'
    topic = args['topic'] if 'topic' in args else 'skip'
    license = args['license'] if 'license' in args else 'skip'
    
    qb_obj = GitHubRepoSearchQueryBuilder()
    query_args = get_query_args(name, description, readme, topics, owner, repo_name, user,
                                min_size, max_size, min_forks, max_forks, min_stars, max_stars,
                                min_created, max_created, language, topic, license)
    query_args['value'] = search_term
    qb_obj.init_from_args(query_args)
    query = qb_obj.build()
    print(f"building query finished with {query}")

    df = call_github_api(query, max_results, token)
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")

    print("extracting code from repos...")
    return extract_code_fun(df, filename, token)


if __name__ == "__main__":
    fetch_repos(token='', max_results=1, filename='test.csv', search_term='pentest')
