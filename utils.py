import subprocess

def get_commit_dependencies(repo_path, branch_name):
    rev_list_command = ["git", "-C", repo_path, "rev-list", branch_name]
    rev_list_output = subprocess.check_output(rev_list_command).decode('utf-8').strip()
    commit_hashes = rev_list_output.splitlines()

    commit_data = []
    for commit_hash in commit_hashes:
        log_command = ["git", "-C", repo_path, "log", "-n", "1", "--pretty=%H %P %s", commit_hash]
        log_output = subprocess.check_output(log_command).decode('utf-8').strip()
        parts = log_output.split(" ", 2)
        commit_hash = parts[0]
        parents = parts[1].split() if len(parts) > 1 else []
        message = parts[2] if len(parts) > 2 else "No message"
        commit_data.append((commit_hash, parents, message))
    return commit_data

def generate_mermaid_graph(commit_data):
    mermaid = ["graph TD;"]
    for commit, parents, message in commit_data:
        node = f'    {commit}["{commit[:7]}..: {message}"]'
        if not parents:
            mermaid.append(node)
        for parent in parents:
            mermaid.append(f'    {parent} --> {commit}["{commit[:7]}..: {message}"]')
    return "\n".join(mermaid)
