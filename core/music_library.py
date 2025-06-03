


import os
import json
import hashlib
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


class MusicLibrary:
    def __init__(self):
        self.config_file = "config.json"
        self.all_formats = {
            'Аудио': ['.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.wma'],
            'Изображения': ['.jpg', '.jpeg', '.png', '.gif'],
            'Видео': ['.mp4', '.avi', '.mkv'],
            'Документы': ['.txt', '.docx', '.doc', '.xlsx', '.xls']
        }
        self.supported_formats = []
        self.music_library = defaultdict(lambda: defaultdict(dict))
        self.previous_files = set()
        self.load_config()
        self.save_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.supported_formats = config.get('formats', [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.supported_formats = [fmt for group in self.all_formats.values() for fmt in group]

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'formats': self.supported_formats}, f)

    def show_format_selection(self, parent):
        """Окно выбора форматов с прогресс-баром"""
        selection_window = tk.Toplevel(parent)
        selection_window.title("Выберите форматы файлов")
        selection_window.geometry("600x500")

        main_frame = tk.Frame(selection_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления выбором
        select_all_frame = tk.Frame(scrollable_frame)
        select_all_frame.pack(fill=tk.X, pady=5)
        tk.Button(select_all_frame, text="Выбрать все",
                  command=lambda: self.toggle_all(True, format_vars)).pack(side=tk.LEFT)
        tk.Button(select_all_frame, text="Снять все",
                  command=lambda: self.toggle_all(False, format_vars)).pack(side=tk.LEFT)

        format_vars = {}

        # Группы форматов
        for group_name, formats in self.all_formats.items():
            group_frame = tk.LabelFrame(scrollable_frame, text=group_name, padx=5, pady=5)
            group_frame.pack(fill=tk.X, pady=5)

            cols = [tk.Frame(group_frame) for _ in range(3)]
            for col in cols:
                col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            for i, fmt in enumerate(formats):
                col = cols[i % 3]
                format_vars[fmt] = tk.IntVar(value=1 if fmt in self.supported_formats else 0)
                tk.Checkbutton(col, text=fmt, variable=format_vars[fmt],
                               anchor='w').pack(anchor='w')

        # Кнопки подтверждения
        button_frame = tk.Frame(selection_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def apply_selection():
            self.supported_formats = [fmt for fmt, var in format_vars.items() if var.get()]
            self.save_config()
            selection_window.destroy()

        tk.Button(button_frame, text="Применить", command=apply_selection,
                  bg="#4CAF50", fg="white").pack(side=tk.RIGHT)
        tk.Button(button_frame, text="Отмена",
                  command=selection_window.destroy).pack(side=tk.LEFT)

        selection_window.grab_set()
        selection_window.wait_window()

#         def apply_selection():
#             self.supported_formats = [fmt for fmt, var in format_vars.items() if var.get()]
#             self.save_config()
#             selection_window.destroy()
#
#         tk.Button(button_frame, text="Применить", command=apply_selection,
#                   bg="#4CAF50", fg="white", padx=20).pack(side=tk.RIGHT)
#         tk.Button(button_frame, text="Отмена", command=selection_window.destroy,
#                   padx=20).pack(side=tk.LEFT)
#
#         selection_window.grab_set()
#         selection_window.wait_window()
#         return len(self.supported_formats) > 0
#
    def toggle_all(self, state, format_vars):
        for fmt, var in format_vars.items():
            var.set(1 if state else 0)

    def scan_folder(self, folder_path, clear_existing=True, parent=None):
        """Оптимизированное сканирование с прогресс-баром"""
        if not folder_path:
            return False, "Не выбрана папка"

        # Окно прогресса
        progress = tk.Toplevel(parent)
        progress.title("Сканирование...")
        progress.geometry("300x100")
        tk.Label(progress, text="Идет сканирование...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress, mode="indeterminate")
        progress_bar.pack(pady=5)
        progress_bar.start()
        progress.update()

        try:
            if clear_existing:
                self.music_library.clear()
                self.music_library = defaultdict(lambda: defaultdict(dict))

            file_count = defaultdict(int)
            current_files = set()

            def scan_recursive(current_path, node):
                nonlocal file_count
                has_valid_files = False

                try:
                    entries = os.listdir(current_path)
                    progress.update()  # Обновляем окно
                except (PermissionError, OSError):
                    return False

                for entry in entries:
                    try:
                        full_path = os.path.join(current_path, entry)

                        if os.path.isdir(full_path):
                            subnode = {}
                            if scan_recursive(full_path, subnode):
                                node[entry] = subnode
                                has_valid_files = True
                        elif any(entry.lower().endswith(fmt) for fmt in self.supported_formats):
                            file_hash = self.get_file_hash(full_path)
                            if "_files" not in node:
                                node["_files"] = []

                            is_new = file_hash not in self.previous_files if file_hash else True
                            node["_files"].append((entry, full_path, is_new))
                            ext = os.path.splitext(entry)[1].lower()
                            file_count[ext] += 1
                            if file_hash:
                                current_files.add(file_hash)
                            has_valid_files = True

                    except (PermissionError, OSError):
                        continue

                return has_valid_files

            success = scan_recursive(folder_path, self.music_library)
            self.previous_files = current_files

            if not success:
                return False, "Не найдено файлов с выбранными форматами"

            stats = ", ".join([f"{ext.upper()}: {count}" for ext, count in file_count.items()])
            return True, f"Найдено: {sum(file_count.values())} файлов ({stats})"

        finally:
            progress.destroy()  # Закрываем окно прогресса в любом случае

#     def scan_folder(self, folder_path, clear_existing=True, parent=None):
#         if not folder_path:
#             return False, "Не выбрана папка"
#
#         # Показываем прогресс-бар
#         progress = tk.Toplevel(parent)
#         progress.title("Сканирование...")
#         progress.geometry("300x100")
#         tk.Label(progress, text="Идет сканирование папок...").pack(pady=10)
#         progress_bar = ttk.Progressbar(progress, orient="horizontal", length=200, mode="indeterminate")
#         progress_bar.pack()
#         progress_bar.start()
#         progress.update()
#
#         try:
#             if clear_existing:
#                 self.music_library.clear()
#                 self.music_library = defaultdict(lambda: defaultdict(dict))
#
#             file_count = defaultdict(int)
#             current_files = set()
#
#             def scan_recursive(current_path, node):
#                 nonlocal file_count
#                 has_valid_files = False
#
#                 try:
#                     entries = os.listdir(current_path)
#                     progress.update()  # Обновляем окно прогресса
#                 except (PermissionError, OSError):
#                     return False
#
#                 for entry in entries:
#                     try:
#                         full_path = os.path.join(current_path, entry)
#
#                         if os.path.isdir(full_path):
#                             subnode = {}
#                             if scan_recursive(full_path, subnode):
#                                 node[entry] = subnode
#                                 has_valid_files = True
#                         elif any(entry.lower().endswith(fmt) for fmt in self.supported_formats):
#                             file_hash = self.get_file_hash(full_path)
#                             if "_files" not in node:
#                                 node["_files"] = []
#
#                             is_new = file_hash not in self.previous_files if file_hash else True
#                             node["_files"].append((entry, full_path, is_new))
#                             ext = os.path.splitext(entry)[1].lower()
#                             file_count[ext] += 1
#                             if file_hash:
#                                 current_files.add(file_hash)
#                             has_valid_files = True
#
#                     except (PermissionError, OSError):
#                         continue
#
#                 return has_valid_files
#
#             success = scan_recursive(folder_path, self.music_library)
#             self.previous_files = current_files
#
#             if not success:
#                 return False, "Не найдено файлов с выбранными форматами"
#
#             stats = ", ".join([f"{ext.upper()}: {count}" for ext, count in file_count.items()])
#             return True, f"Найдено: {sum(file_count.values())} файлов ({stats})"
#
#         finally:
#             progress.destroy()  # Закрываем окно прогресса в любом случае
#

    def get_file_hash(self, filepath):
        if not os.path.isfile(filepath):
            return None

        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                buf = f.read(65536)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(65536)
            return hasher.hexdigest()
        except (PermissionError, OSError):
            return None

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
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(12)

            title = doc.add_heading('Моя музыкальная коллекция', level=1)
            title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            def add_items(node, level=1):
                for name, content in node.items():
                    if name == "_files":
                        for file_name, _, is_new in content:
                            p = doc.add_paragraph('    ' * level + f"🎵 {file_name}" + (" (NEW)" if is_new else ""))
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

#
#
#
#
#
# # # import os
# # # import tkinter as tk
# # # from collections import defaultdict
# # # from tkinter import filedialog, messagebox, Toplevel, Checkbutton, IntVar
# # # from docx import Document
# # # from docx.shared import Pt, RGBColor
# # # from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
# # #
# # #
# # # class MusicLibrary:
# # #     def __init__(self):
# # #         self.all_formats = {
# # #             '.mp3': 1,
# # #             '.flac': 1,
# # #             '.wav': 1,
# # #             '.ogg': 1,
# # #             '.m4a': 1,
# # #             '.aac': 1,
# # #             '.wma': 1,
# # #             '.jpg': 0,
# # #             '.jpeg': 0,
# # #             '.mp4': 0,
# # #             '.avi' : 0,
# # #             '.docx' : 0,
# # #             '.doc' : 0,
# # #             '.xlsx': 0,
# # #             '.xls': 0,
# # #         }
# # #         self.supported_formats = [fmt for fmt, enabled in self.all_formats.items() if enabled]
# # #         self.music_library = defaultdict(lambda: defaultdict(dict))
# # #
# # #     def show_format_selection(self, parent):
# # #         """Показывает окно выбора форматов файлов с расположением в 3 столбца"""
# # #         selection_window = tk.Toplevel(parent)
# # #         selection_window.title("Выберите форматы файлов")
# # #         selection_window.geometry("500x400")  # Увеличим ширину для 3 столбцов
# # #
# # #         # Фрейм для чекбоксов с прокруткой
# # #         main_frame = tk.Frame(selection_window)
# # #         main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
# # #
# # #         # Холст и скроллбар
# # #         canvas = tk.Canvas(main_frame)
# # #         scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
# # #         scrollable_frame = tk.Frame(canvas)
# # #
# # #         scrollable_frame.bind(
# # #             "<Configure>",
# # #             lambda e: canvas.configure(
# # #                 scrollregion=canvas.bbox("all")
# # #             )
# # #         )
# # #
# # #         canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
# # #         canvas.configure(yscrollcommand=scrollbar.set)
# # #
# # #         canvas.pack(side="left", fill="both", expand=True)
# # #         scrollbar.pack(side="right", fill="y")
# # #
# # #         # Создаем 3 фрейма для столбцов
# # #         col1 = tk.Frame(scrollable_frame)
# # #         col2 = tk.Frame(scrollable_frame)
# # #         col3 = tk.Frame(scrollable_frame)
# # #
# # #         col1.pack(side="left", fill="both", expand=True, padx=5)
# # #         col2.pack(side="left", fill="both", expand=True, padx=5)
# # #         col3.pack(side="left", fill="both", expand=True, padx=5)
# # #
# # #         format_vars = {}
# # #         formats = sorted(self.all_formats.keys())  # Сортируем форматы по алфавиту
# # #
# # #         # Распределяем форматы по 3 столбцам
# # #         for i, fmt in enumerate(formats):
# # #             format_vars[fmt] = tk.IntVar(value=self.all_formats[fmt])
# # #
# # #             # Выбираем столбец (0,1,2 -> col1,col2,col3)
# # #             target_col = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
# # #
# # #             cb = tk.Checkbutton(target_col, text=fmt, variable=format_vars[fmt],
# # #                                 anchor='w', padx=5, pady=2)
# # #             cb.pack(fill='x')
# # #
# # #         # Фрейм для кнопок внизу
# # #         button_frame = tk.Frame(selection_window)
# # #         button_frame.pack(fill=tk.X, padx=10, pady=10)
# # #
# # #         def apply_selection():
# # #             for fmt, var in format_vars.items():
# # #                 self.all_formats[fmt] = var.get()
# # #             self.supported_formats = [fmt for fmt, enabled in self.all_formats.items() if enabled]
# # #             selection_window.destroy()
# # #
# # #         # Кнопка подтверждения
# # #         confirm_btn = tk.Button(button_frame, text="Применить", command=apply_selection,
# # #                                 bg="#4CAF50", fg="white", padx=20)
# # #         confirm_btn.pack(side=tk.RIGHT)
# # #
# # #         # Кнопка отмены
# # #         cancel_btn = tk.Button(button_frame, text="Отмена", command=selection_window.destroy,
# # #                                padx=20)
# # #         cancel_btn.pack(side=tk.LEFT)
# # #
# # #         selection_window.grab_set()
# # #         selection_window.wait_window()
# # #         return len(self.supported_formats) > 0
# # #
# # #     def scan_folder(self, folder_path, clear_existing=True, parent=None):
# # #         if not folder_path:
# # #             return False
# # #
# # #         if not self.show_format_selection(parent):
# # #             messagebox.showwarning("Предупреждение", "Не выбрано ни одного формата файлов")
# # #             return False
# # #
# # #         if clear_existing:
# # #             self.music_library.clear()
# # #             self.music_library = defaultdict(lambda: defaultdict(dict))
# # #
# # #         # Запускаем сканирование и проверяем, есть ли вообще подходящие файлы
# # #         has_content = self._scan_folder_recursive(folder_path, self.music_library)
# # #
# # #         if not has_content:
# # #             messagebox.showinfo("Информация",
# # #                                 "В выбранной папке и подпапках не найдено файлов с выбранными расширениями")
# # #             return False
# # #
# # #         return True
# # #
# #     def _scan_folder_recursive(self, current_path, node):
# #         has_valid_files = False  # Флаг для отслеживания наличия нужных файлов
# #
# #         for entry in os.listdir(current_path):
# #             full_path = os.path.join(current_path, entry)
# #
# #             if os.path.isdir(full_path):
# #                 # Рекурсивно сканируем подпапку
# #                 subnode = {}
# #                 subnode_has_content = self._scan_folder_recursive(full_path, subnode)
# #
# #                 if subnode_has_content:
# #                     node[entry] = subnode
# #                     has_valid_files = True
# #
# #             elif any(entry.lower().endswith(fmt) for fmt in self.supported_formats):
# #                 if "_files" not in node:
# #                     node["_files"] = []
# #                 node["_files"].append((entry, full_path))
# #                 has_valid_files = True
# #
# #         return has_valid_files  # Возвращаем информацию о наличии подходящих файлов
# #
# #     def get_library(self):
# #         return self.music_library
# #
# #     def clear_library(self):
# #         """Полностью очищает музыкальную коллекцию"""
# #         self.music_library.clear()
# #         # Восстанавливаем структуру defaultdict
# #         self.music_library = defaultdict(lambda: defaultdict(dict))
# #
# #     def save_to_docx(self, output_path=None):
# #         if not output_path:
# #             output_path = filedialog.asksaveasfilename(
# #                 defaultextension=".docx",
# #                 filetypes=[("Word Documents", "*.docx")],
# #                 title="Сохранить коллекцию как"
# #             )
# #             if not output_path:
# #                 return False, ""
# #
# #         try:
# #             doc = Document()
# #             style = doc.styles['Normal']
# #             style.font.name = 'Arial'
# #             style.font.size = Pt(12)
# #
# #             title = doc.add_heading('Моя музыкальная коллекция', level=1)
# #             title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
# #
# #             def add_items(node, level=1):
# #                 for name, content in node.items():
# #                     if name == "_files":
# #                         for file_name, _ in content:
# #                             p = doc.add_paragraph('    ' * level + f"🎵 {file_name}")
# #                             p.runs[0].font.color.rgb = RGBColor(0, 0, 0)
# #                     else:
# #                         heading = doc.add_heading('    ' * (level - 1) + f"📁 {name}", level=min(level + 1, 6))
# #                         heading.runs[0].font.color.rgb = RGBColor(0, 0, 128)
# #                         add_items(content, level + 1)
# #
# #             add_items(self.music_library)
# #             doc.save(output_path)
# #             return True, output_path
# #
# #         except Exception as e:
# #             return False, str(e)