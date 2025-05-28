import os
from pathlib import Path
from collections import defaultdict


class FileManager:
    def __init__(self, supported_formats):
        self.supported_formats = supported_formats

    def scan_folder(self, folder_path):
        """Рекурсивное сканирование папки"""
        library = defaultdict(lambda: defaultdict(dict))
        for root, _, files in os.walk(folder_path):
            rel_path = os.path.relpath(root, folder_path)
            current_node = library
            for part in rel_path.split(os.sep):
                current_node = current_node[part]

            for file in files:
                if file.lower().endswith(self.supported_formats):
                    if "_files" not in current_node:
                        current_node["_files"] = []
                    current_node["_files"].append((file, os.path.join(root, file)))
        return library