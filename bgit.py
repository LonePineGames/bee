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
                    bui.print("-- GIT STATUS --")
                    branch = repo.active_branch.name
                    dirty = repo.is_dirty()

                    merge_head = os.path.join(repo.git_dir, "MERGE_HEAD")
                    merge_in_progress = os.path.exists(merge_head)
                    rebase_in_progress = ".git/rebase-apply" in repo.submodules

                    state = "dirty" if dirty else "clean"
                    if merge_in_progress:
                        state = "merge in progress"
                    elif rebase_in_progress:
                        state = "rebase in progress"
                    result.append(f"branch: {branch} ({state})")

                elif command == 'files':
                    files = {
                        "🛠️ modified": [item.a_path for item in repo.index.diff(None)],
                        "📝 added": [item.a_path for item in repo.index.diff("HEAD")],
                        "📝 untracked": repo.untracked_files,
                        "🗑️ deleted": [item.a_path for item in repo.index.diff(None) if item.deleted_file],
                    }

                    for key, value in files.items():
                        if value:
                            if len(value) > 5:
                                value = value[:5] + ["..."]
                            result.append(f"{key}: {', '.join(value)}")

                elif command == 'diff':
                    result.append("-- GIT DIFF --\n" + repo.git.diff())

                elif command == 'upstream':
                    try:
                        branch = repo.active_branch.name
                        upstream = f"origin/{branch}"
                        ahead, behind = repo.git.rev_list("--count", "--left-right", f"HEAD...{upstream}").split()

                        if int(ahead) > 0:
                            result.append(f"👉 We are {ahead} commits ahead of {upstream}")
                        if int(behind) > 0:
                            result.append(f"👈 {upstream} is {behind} commits ahead of us")

                        if not ahead and not behind:
                            result.append("No commits to push or pull.")

                    except Exception as e:
                        result.append("No upstream branch found.")


                elif command.startswith('log:'):
                    result.append("-- GIT HISTORY --\n" + repo.git.log('--oneline', '-' + command[4:]))
                else:
                    pass

            content = '\n'.join(result)
            bui.print(content)

            return [{ "role": role, "content": content }]

        except Exception as e:
            bui.print("Not a git repository: " + str(e))
            return [{ "role": role, "content": "Not a git repository: " + str(e) }]

    return git_info_source


