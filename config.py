from pathlib import Path
import json


class Config:
    def __init__(self):
        self.config_path = Path.home() / ".music_app_config.json"
        self.defaults = {
            "foobar_path": r"C:\Program Files\foobar2000\foobar2000.exe",
            "last_folder": str(Path.home()),
            "theme": "light"
        }

    def load(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_path) as f:
                return {**self.defaults, **json.load(f)}
        except FileNotFoundError:
            return self.defaults

    def save(self, settings):
        """Сохранение конфигурации"""
        with open(self.config_path, 'w') as f:
            json.dump(settings, f)