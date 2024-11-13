import unittest
import os
import csv
from visualizer import DependencyVisualizer
from utils import get_commit_dependencies, generate_mermaid_graph


def load_config_from_csv(config_path="config.csv"):
    config = {}
    with open(config_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            config['graph_tool'] = row['graph_tool']
            config['repo_path'] = row['repo_path']
            config['branch_name'] = row['branch_name']
    return config


class TestUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = load_config_from_csv()

    def test_get_commit_dependencies(self):
        repo_path = self.config['repo_path']
        branch_name = self.config['branch_name']

        dependencies = get_commit_dependencies(repo_path, branch_name)

        # Проверка, что функция возвращает список с нужной структурой
        self.assertTrue(isinstance(dependencies, list))
        for item in dependencies:
            self.assertEqual(len(item), 3)
            self.assertTrue(isinstance(item[0], str))  # Хеш коммита
            self.assertTrue(isinstance(item[1], list))  # Родители коммита
            self.assertTrue(isinstance(item[2], str))  # Сообщение коммита

    def test_generate_mermaid_graph(self):
        commit_data = [
            ("abc123", ["def456"], "Commit 1"),
            ("def456", ["ghi789"], "Commit 2"),
            ("ghi789", [], "Initial commit")
        ]

        expected_output = (
            'graph TD;\n'
            '    def456 --> abc123["abc123..: Commit 1"]\n'
            '    ghi789 --> def456["def456..: Commit 2"]\n'
            '    ghi789["ghi789..: Initial commit"]'
        )

        mermaid_graph = generate_mermaid_graph(commit_data)
        self.assertEqual(mermaid_graph, expected_output)


class TestDependencyVisualizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = load_config_from_csv()

    def test_initialize_visualizer(self):
        config_path = "config.csv"

        visualizer = DependencyVisualizer(config_path)

        self.assertIn("graph_tool", visualizer.config)
        self.assertIn("repo_path", visualizer.config)
        self.assertIn("branch_name", visualizer.config)
        self.assertTrue(os.path.isfile(visualizer.config["graph_tool"]))
        self.assertTrue(os.path.isdir(visualizer.config["repo_path"]))

    def test_visualize_creates_output(self):
        config_path = "config.csv"

        visualizer = DependencyVisualizer(config_path)

        try:
            visualizer.visualize()
        except Exception as e:
            self.fail(f"visualize() raised an exception unexpectedly: {e}")

        # Проверка, что выходной файл графа был создан
        branch_graph_file = f"{visualizer.config['branch_name']}_graph.png"
        self.assertTrue(os.path.exists(branch_graph_file))

        if os.path.exists(branch_graph_file):
            os.remove(branch_graph_file)


if __name__ == "__main__":
    unittest.main()
