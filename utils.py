import subprocess

def get_commit_dependencies(repo_path, branch_name):
    log_command = ["git", "-C", repo_path, "log", branch_name, "--pretty=%H %P"]
    log_output = subprocess.check_output(log_command).decode('utf-8').strip()

    dependencies = {}
    for line in log_output.splitlines():
        parts = line.split()
        commit = parts[0]
        parents = parts[1:]
        dependencies[commit] = parents
    return dependencies

def generate_mermaid_graph(dependencies):
    mermaid = ["graph TD;"]
    for commit, parents in dependencies.items():
        for parent in parents:
            mermaid.append(f"    {parent} --> {commit};")
    return "\n".join(mermaid)
