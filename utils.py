import subprocess

def get_commit_dependencies(repo_path, branch_name):
    log_command = ["git", "-C", repo_path, "log", branch_name, "--pretty=%H %P %s"]
    log_output = subprocess.check_output(log_command).decode('utf-8').strip()

    commit_data = []
    for line in log_output.splitlines():
        parts = line.split(" ", 2)
        commit_hash = parts[0]
        parents = parts[1].split() if len(parts) > 1 else []
        message = parts[2] if len(parts) > 2 else "No message"
        commit_data.append((commit_hash, parents, message))
    return commit_data

def generate_mermaid_graph(commit_data):
    mermaid = ["graph TD;"]
    for commit, parents, message in commit_data:
        node = f'{commit}["{commit}: {message}"]'
        if not parents:
            mermaid.append(node)
        for parent in parents:
            mermaid.append(f'    {parent} --> {commit}["{commit}: {message}"]')
    return "\n".join(mermaid)
