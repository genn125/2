import os
from collections import defaultdict
from tkinter import filedialog
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


class MusicLibrary:
    def __init__(self):
        self.supported_formats = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma')
        self.music_library = defaultdict(lambda: defaultdict(dict))

    def scan_folder(self, folder_path, clear_existing=True):
        """
        Сканирует папку и добавляет музыку в коллекцию
        :param folder_path: Путь к сканируемой папке
        :param clear_existing: Если True, очищает существующую коллекцию перед сканированием
        :return: True если успешно, False если отменено
        """
        if not folder_path:
            return False

        self.music_library.clear()
        self.music_library = defaultdict(lambda: defaultdict(dict))  # Восстанавливаем структуру

        self._scan_folder_recursive(folder_path, self.music_library)
        return True

    def _scan_folder_recursive(self, current_path, node):
        for entry in os.listdir(current_path):
            full_path = os.path.join(current_path, entry)

            if os.path.isdir(full_path):
                if entry not in node:
                    node[entry] = {}
                self._scan_folder_recursive(full_path, node[entry])
            elif entry.lower().endswith(self.supported_formats):
                if "_files" not in node:
                    node["_files"] = []
                node["_files"].append((entry, full_path))

    def get_library(self):
        return self.music_library

    def clear_library(self):
        """Полностью очищает музыкальную коллекцию"""
        self.music_library.clear()
        # Восстанавливаем структуру defaultdict
        self.music_library = defaultdict(lambda: defaultdict(dict))

    def save_to_docx(self, output_path=None):
        if not output_path:
            output_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word Documents", "*.docx")],
                title="Сохранить коллекцию как"
            )
            if not output_path:
                return False, ""

        try:
            doc = Document()
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(12)

            title = doc.add_heading('Моя музыкальная коллекция', level=1)
            title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            def add_items(node, level=1):
                for name, content in node.items():
                    if name == "_files":
                        for file_name, _ in content:
                            p = doc.add_paragraph('    ' * level + f"🎵 {file_name}")
                            p.runs[0].font.color.rgb = RGBColor(0, 0, 0)
                    else:
                        heading = doc.add_heading('    ' * (level - 1) + f"📁 {name}", level=min(level + 1, 6))
                        heading.runs[0].font.color.rgb = RGBColor(0, 0, 128)
                        add_items(content, level + 1)

            add_items(self.music_library)
            doc.save(output_path)
            return True, output_path

        except Exception as e:
            return False, str(e)