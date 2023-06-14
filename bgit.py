from git import Repo
import os

import bui

def info_source(config, role="system"):
    def git_info_source():
        try:
            repo = Repo(os.getcwd(), search_parent_directories=True)

            if not repo.git_dir:
                return [{ "role": role, "content": "Not a git repository" }]

            result = []

            for command in config.split(','):
                if command == 'status':
                    status_output = repo.git.status()

                    result.append(f"branch: {repo.active_branch}")
                    if repo.is_dirty():
                        result.append("dirty")
                    if 'MERGING' in status_output:
                        result.append("MERGE in progress")
                    if 'REBASING' in status_output:
                        result.append("REBASE in progress")

                    lines = status_output.split('\n')
                    modified_files = [line.replace('modified:', '').strip() for line in lines if 'modified:' in line]

                    result.append(f"modified files: {', '.join(modified_files)}")

                elif command == 'diff':
                    result.append("-- DIFF --\n" + repo.git.diff())

                elif command.startswith('log:'):
                    result.append("-- HISTORY --\n" + repo.git.log('--oneline', '-' + command[4:]))
                else:
                    pass

            content = '\n'.join(result)
            bui.print(content)

            return [{ "role": role, "content": content }]

        except Exception as e:
            return [{ "role": role, "content": "Not a git repository" }]

    return git_info_source


