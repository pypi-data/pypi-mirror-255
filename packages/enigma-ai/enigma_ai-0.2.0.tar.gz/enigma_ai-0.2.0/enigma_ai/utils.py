
import datetime

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


def get_query_args(**args):
    """
    Builds a dictionary of query arguments based on the provided keyword arguments.
    """
    query_args = {
        'name': False,
        'description': False,
        'readme': False,
        'topics': False,
        'owner': 'skip',
        'repo_name': 'skip',
        'user': 'skip',
        'min_size': 666,
        'max_size': 666,
        'min_forks': 666,
        'max_forks': 666,
        'min_stars': 666,
        'max_stars': 666,
        'min_created': datetime.date(2000, 1, 1),
        'max_created': datetime.date(2000, 1, 1),
        'language': 'skip',
        'topic': 'skip',
        'license': 'skip'
    }

    for key, value in args.items():
        if key in query_args:
            query_args[key] = value

    kes_to_delete = []
    for key in query_args:
        if query_args[key] == 'skip':
            kes_to_delete.append(key)
        if query_args[key] == 666:
            kes_to_delete.append(key)
        if query_args[key] == datetime.date(2000, 1, 1):
            kes_to_delete.append(key)
    for key in kes_to_delete:
        del query_args[key]
    return query_args

def get_extensions_dict():
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
    return code_extensions_column_name_dict