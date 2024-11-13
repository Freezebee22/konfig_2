import csv
import subprocess
from utils import get_commit_dependencies, generate_mermaid_graph

class DependencyVisualizer:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)

    def load_config(self, path):
        config = {}
        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                config['graph_tool'] = row['graph_tool']
                config['repo_path'] = row['repo_path']
                config['branch_name'] = row['branch_name']
        return config

    def visualize(self):
        dependencies = get_commit_dependencies(
            self.config['repo_path'],
            self.config['branch_name']
        )

        mermaid_graph = generate_mermaid_graph(dependencies)

        with open('graph.mmd', 'w') as file:
            file.write(mermaid_graph)

        subprocess.run([self.config['graph_tool'], '-i', 'graph.mmd', '-o', f'{self.config['branch_name']}_graph.png'])


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python visualizer.py <path_to_config>")
        sys.exit(1)

    visualizer = DependencyVisualizer(sys.argv[1])
    visualizer.visualize()
