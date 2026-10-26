import json
import re
import os


class ParserUtils:

    @staticmethod
    def parse_json(path):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        absolute_path = os.path.join(project_root, 'resources', path)
        with open(absolute_path) as f:
            return json.load(f)

    @staticmethod
    def parse_link(text):
        url_pattern = r'https?://\S+|www\.\S+'
        links = re.findall(url_pattern, text)
        return links
