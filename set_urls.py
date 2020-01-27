#!/usr/bin/env python

'''
Script to update the URLs in the frontend.
Why? Because if running this locally you will need to chane the URLs from the
production URLs to localhost or 192.168.1.*
'''

import argparse
import sys

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument(
    '-p', '--prod', help='set urls to prod URLs', action='store_true')
group.add_argument(
    '-l', '--local', help='set urls to localhost URLs', action='store_true')
group.add_argument('-d', '--dev', help='set urls to dev URLs (requires IP)')
parser.add_argument('--dryrun', help='Dry run, show what lines will be changed',
                    required=False, action='store_true')
args = parser.parse_args()


if args.local:
    env = 'local'
elif args.prod:
    env = 'prod'
elif args.dev:
    env = 'dev'
else:
    print("Missing argument")
    sys.exit(1)

configs = {
    'prod': {
        'ws_url': 'wss://games.mickjohn.com:8010',
        'http_url': 'games.mickjohn.com',
    },
    'local': {
        'ws_url': 'ws://localhost:8080',
        'http_url': 'localhost',
    },
    'dev': {
        'ws_url': f"ws://{args.dev}:9000",
        'http_url': f"{args.dev}:9080",
    },
}


updates = [
    {
        'tag': '// CHANGEME #1',
        'replacement': f"export const config: Config = new Config('{configs[env]['ws_url']}','{configs[env]['http_url']}'); // CHANGEME #1",
        'file_paths': [
            'frontend/frontend/src/common/Config.tsx',
        ],
    },
    {
        'tag': '// CHANGEME #2',
        'replacement': f"const websocketBaseUrl = '{configs[env]['ws_url']}' // CHANGEME #2",
        'file_paths': ['frontend/frontend/src/homepage/components/HomePage/HomePage.tsx'],
    }
]


for update in updates:
    file_paths = update['file_paths']
    for file_path in file_paths:
        new_lines = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip().endswith(update['tag']):
                    print(
                        f"Changing line in {file_path}:\n  FROM {line.strip()}\n  TO   {update['replacement']}\n")
                    new_lines.append(update['replacement'] + '\n')
                else:
                    new_lines.append(line)

        if not args.dryrun:
            for file_path in file_paths:
                with open(file_path, 'w') as f:
                    f.writelines(new_lines)
