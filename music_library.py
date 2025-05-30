import os
from collections import defaultdict
from tkinter import filedialog
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class MusicLibrary:
    def __init__(self):
        self.supported_formats = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma')
        self.music_library = defaultdict(lambda: defaultdict(dict))

    def scan_folder(self, folder_path, clear_existing=True):
        if not folder_path:
            return False

        if clear_existing:
            self.clear_library()

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
        self.music_library.clear()
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
            self._setup_document_styles(doc)

            # Заголовок
            title = doc.add_heading('Моя музыкальная коллекция', level=1)
            title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            # Основное содержимое
            for folder_name, content in sorted(self.music_library.items()):
                self._add_folder(doc, folder_name, content)

            doc.save(output_path)
            return True, output_path

        except Exception as e:
            return False, str(e)

    def _setup_document_styles(self, doc):
        """Настраивает стили документа"""
        styles = doc.styles
        style = styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(12)

        if 'FolderHeading' not in styles:
            heading_style = styles.add_style('FolderHeading', WD_STYLE_TYPE.PARAGRAPH)
            heading_style.base_style = styles['Heading 2']
            heading_style.font.color.rgb = RGBColor(0, 0, 128)
            heading_style.font.bold = True

    def _add_folder(self, doc, folder_name, content, level=1):
        """Добавляет папку со сворачиваемым содержимым"""
        # Заголовок папки
        para = doc.add_paragraph(style='Heading 2')
        run = para.add_run(f"📁 {folder_name}")
        run.font.color.rgb = RGBColor(0, 0, 128)
        run.font.bold = True

        # Добавляем файлы
        if "_files" in content:
            for file_name, _ in sorted(content["_files"], key=lambda x: x[0]):
                file_para = doc.add_paragraph(f"    🎵 {file_name}", style='List Bullet')
                file_para.paragraph_format.left_indent = Pt(level * 20)

        # Рекурсивно добавляем подпапки
        for subfolder_name, subcontent in sorted(content.items()):
            if subfolder_name != "_files":
                self._add_folder(doc, subfolder_name, subcontent, level + 1)