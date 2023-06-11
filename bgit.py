from git import Repo
import os

def info_source(config, role="system"):
    # print('git_info_source')
    # bgit.info_source('status,log:5,diff'),
    def git_info_source():
        repo = Repo(os.getcwd(), search_parent_directories=True)

        if not repo.git_dir:
            return [{ "role": role, "content": "Not a git repository" }]

        result = []

        for command in config.split(','):
            if command == 'status':
                result.append(repo.git.status())
            elif command == 'diff':
                result.append("-- DIFF --\n" + repo.git.diff())
            elif command.startswith('log:'):
                result.append("-- HISTORY --\n" + repo.git.log('--oneline', '-' + command[4:]))
            else:
                pass

        content = '\n\n'.join(result)
        # print(content)

        return [{ "role": role, "content": content }]

    return git_info_source


