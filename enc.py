#!/usr/bin/python3
import argparse
import re
import sys
import yaml
from typing import Any, Dict


parser = argparse.ArgumentParser(description="Stupid Puppet node classifier.")
parser.add_argument('node', help="Node name as recognized by Puppet")
parser.add_argument('-c', '--config', dest='config', default='nodes.yaml',
                    help="Path to the `%(default)s` configuration, defaults to the current directory")


def fetch_node(node: str, config: Dict):
    """Fetches node definition from the dictionary created from a YAML file.

    Supports the following special keys:
    - ::defaults - All values are prepended to the found entry
    - /<anything>/ - <anything> is treated as a regular expression
    """
    defaults: dict = config.pop('::defaults', {})

    all_nodes = config.keys()
    if node not in all_nodes:
        # Treat keys as regex patterns, first match wins
        for pattern in all_nodes:
            if not pattern.startswith('/') and not pattern.endswith('/'):
                continue

            if re.search(pattern.strip('/'), node):
                config_node = config[pattern]
                break
        else:
            raise Exception(f"Node {node} was not found in the configuration.")
    else:
        config_node = config[node]

    print(yaml.safe_dump(merge(config_node, defaults), explicit_start=True))


def merge(tree: Dict, default: Dict) -> Dict:
    """Performs a recursive deep-merge of given dictionaries.
    """
    if isinstance(tree, dict) and isinstance(default, dict):
        for k, v in default.items():
            if k not in tree:
                tree[k] = v
            else:
                tree[k] = merge(tree[k], v)
    return tree


if __name__ == '__main__':
    args = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(1)

    with open(args.config, 'r', encoding='utf-8') as stream:
        try:
            yaml_config = yaml.safe_load(stream)
        except yaml.YAMLError as ex:
            print(f"YAML config `{args.config} is invalid.")
            raise

    fetch_node(args.node, dict(yaml_config))
