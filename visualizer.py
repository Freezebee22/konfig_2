import os
import csv
import zlib
import subprocess


def read_config(file_path='config.csv'):
    """
    Считывает конфигурацию из CSV-файла.
    """
    config = {}
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            config['graph_tool'] = row['graph_tool']
            config['repo_path'] = row['repo_path']
            config['branch_name'] = row['branch_name']
    return config


def parse_object(object_hash, config, description=None):
    """
    Извлечь информацию из git-объекта по его хэшу.
    """
    object_path = os.path.join(config['repo_path'], '.git', 'objects', object_hash[:2], object_hash[2:])

    with open(object_path, 'rb') as file:
        raw_object_content = zlib.decompress(file.read())
        header, raw_object_body = raw_object_content.split(b'\x00', maxsplit=1)
        object_type, content_size = header.decode().split(' ')

        object_dict = {}

        if object_type == 'commit':
            commit_data = parse_commit(raw_object_body, config)
            object_dict['label'] = f'commit::{object_hash[:6]}'
            if commit_data['message']:
                message = commit_data['message'].replace(' ', '_')
                object_dict['label'] += f'::{message}'
            object_dict['children'] = commit_data['children']

        elif object_type == 'tree':
            object_dict['label'] = f'tree::{object_hash[:6]}'
            object_dict['children'] = parse_tree(raw_object_body, config)

        elif object_type == 'blob':
            object_dict['label'] = f'blob::{object_hash[:6]}'
            object_dict['children'] = []

        if description is not None:
            object_dict['label'] += f'::{description}'

        return object_dict


def parse_tree(raw_content, config):
    """
    Парсим git-объект дерева.
    """
    children = []
    rest = raw_content
    while rest:
        mode, rest = rest.split(b' ', maxsplit=1)
        name, rest = rest.split(b'\x00', maxsplit=1)
        sha1, rest = rest[:20].hex(), rest[20:]
        children.append(parse_object(sha1, config, description=name.decode()))

    return children


def parse_commit(raw_content, config):
    """
    Парсим git-объект коммита.
    """
    content = raw_content.decode()
    content_lines = content.split('\n')

    commit_data = {}

    commit_data['tree'] = content_lines[0].split()[1]
    content_lines = content_lines[1:]

    commit_data['parents'] = []
    while content_lines[0].startswith('parent'):
        commit_data['parents'].append(content_lines[0].split()[1])
        content_lines = content_lines[1:]

    while content_lines[0].strip():
        key, *values = content_lines[0].split()
        commit_data[key] = ' '.join(values)
        content_lines = content_lines[1:]

    commit_data['message'] = '\n'.join(content_lines[1:]).strip()

    commit_data['children'] = [parse_object(commit_data['tree'], config)] + \
                              [parse_object(parent, config) for parent in commit_data['parents']]

    return commit_data


def get_last_commit(config):
    """Получить хэш для последнего коммита в ветке"""
    head_path = os.path.join(config['repo_path'], '.git', 'refs', 'heads', config['branch_name'])
    with open(head_path, 'r') as file:
        return file.read().strip()


def generate_mermaid(filename, config):
    """Создать Mermaid-файл для графа зависимостей"""
    def recursive_write(file, tree, visited):
        label = tree['label']
        for child in tree['children']:
            child_label = child['label']
            if (label, child_label) not in visited:
                file.write(f'    {label} --> {child_label}\n')
                visited.add((label, child_label))
            recursive_write(file, child, visited)

    last_commit = get_last_commit(config)
    tree = parse_object(last_commit, config)
    with open(filename, 'w') as file:
        file.write('graph TD\n')
        recursive_write(file, tree, set())


if __name__ == '__main__':
    config = read_config()
    generate_mermaid(f'{config["branch_name"]}_graph.mmd', config)
    subprocess.run([
        config['graph_tool'],
        '-i', f'{config["branch_name"]}_graph.mmd',
        '-o', f'{config["branch_name"]}_graph.svg'
    ])
