import unittest
from unittest.mock import patch, mock_open
import zlib
import visualizer


class TestGitVisualization(unittest.TestCase):

    def test_read_config(self):
        config_csv = "graph_tool,repo_path,branch_name\n/tool/path,/repo/path,main\n"
        with patch('builtins.open', mock_open(read_data=config_csv)) as mock_file:
            config = visualizer.read_config('test_config.csv')
            mock_file.assert_called_with('test_config.csv', 'r')
            self.assertEqual(config, {
                'graph_tool': '/tool/path',
                'repo_path': '/repo/path',
                'branch_name': 'main'
            })


    @patch('os.path.join', return_value='/repo/path/.git/objects/12/34abcd')
    @patch('builtins.open', new_callable=mock_open, read_data=zlib.compress(b'blob 6\0Hello!'))
    def test_parse_object_blob(self, mock_open, mock_join):
        config = {'repo_path': '/repo/path'}
        result = visualizer.parse_object('1234abcd', config)
        self.assertEqual(result, {
            'label': 'blob::1234ab',
            'children': []
        })
        mock_open.assert_called_with('/repo/path/.git/objects/12/34abcd', 'rb')


    def test_parse_tree(self):
        raw_content = b'100644 file.txt\0' + b'\x00' * 20  # Mocked tree object
        config = {'repo_path': '/repo/path'}
        with patch('visualizer.parse_object',
                   return_value={'label': 'blob::dummy', 'children': []}) as mock_parse_object:
            result = visualizer.parse_tree(raw_content, config)
            self.assertEqual(len(result), 1)
            mock_parse_object.assert_called_once()


    @patch('visualizer.parse_object', return_value={'label': 'commit::1234ab', 'children': []})
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_mermaid(self, mock_open, mock_parse_object):
        config = {'repo_path': '/repo/path', 'branch_name': 'main'}
        with patch('visualizer.get_last_commit', return_value='1234abcd'):
            visualizer.generate_mermaid('output.mmd', config)
            mock_open().write.assert_called()
            self.assertTrue(mock_open().write.called)


if __name__ == '__main__':
    unittest.main()
