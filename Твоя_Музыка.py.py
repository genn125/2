import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from collections import defaultdict


class MusicCollectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Твоя Музыка")
        self.root.geometry("1000x1000")

        # Путь к foobar2000 (замените на ваш)
        self.foobar_path = r"C:\Program Files (x86)\foobar2000\foobar2000.exe"

        # Поддерживаемые форматы файлов
        self.supported_formats = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma')

        # Структура данных: {"Папка": {"Подпапка": {"_files": [(имя, путь)]}}}
        self.music_library = defaultdict(lambda: defaultdict(dict))

        # Инициализация интерфейса
        self._setup_ui()

        # Загрузка тестовых данных (можно удалить)
        self._load_demo_data()

    def _setup_ui(self):
        """Создание интерфейса"""
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Label(
            top_frame,
            text="Альбомы групп без повторов одинаковых композиций",
            font=('Arial', 14, 'bold'),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT)

        # Панель инструментов
        tool_frame = tk.Frame(self.root, padx=5, pady=5)
        tool_frame.pack(fill=tk.X)

        buttons = [
            ("📁 Сканировать папку", self.scan_folder),
            ("🔍 Поиск", lambda: self.search_music(self.search_entry.get())),
            ("🗑️ Очистить", self.clear_library)
        ]

        for text, cmd in buttons:
            btn = tk.Button(
                tool_frame,
                text=text,
                command=cmd,
                bd=1,
                relief=tk.RIDGE,
                padx=10
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Поле поиска
        search_frame = tk.Frame(self.root, pady=5)
        search_frame.pack(fill=tk.X, padx=10)

        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(fill=tk.X, padx=5, expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_music(self.search_entry.get()))

        # Дерево коллекции
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("type", "path"),
            show="tree",
            selectmode="extended"
        )

        # Настройка стилей
        self.tree.tag_configure("folder", background="#f0f0f0", font=('Arial', 10, 'bold'))
        self.tree.tag_configure("file", background="white")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Панель управления плеером
        player_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=8)
        player_frame.pack(fill=tk.X)

        controls = [
            ("▶ Воспроизвести", self.play_selected),
            ("⏏ В плейлист", self.add_to_playlist),
            ("⏹ Стоп", self.stop_foobar)
        ]

        for text, cmd in controls:
            btn = tk.Button(
                player_frame,
                text=text,
                command=cmd,
                bg="#f8f8f8",
                padx=10
            )
            btn.pack(side=tk.LEFT, padx=5)

        self.status_bar = tk.Label(
            player_frame,
            text="Готов к работе",
            bg="#e0e0e0",
            fg="#333333",
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Воспроизвести", command=self.play_selected)
        self.context_menu.add_command(label="Добавить в плейлист", command=self.add_to_playlist)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Открыть в проводнике", command=self.open_in_explorer)
        self.context_menu.add_command(label="Удалить", command=self.delete_item)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.play_selected)

    def _load_demo_data(self):
        """Тестовые данные для демонстрации (можно удалить)"""
        self.music_library = {
            "Rock": {
                "2020 - Album1": {
                    "_files": [("song1.mp3", "/fake/path/song1.mp3")]
                },
                "Subfolder": {
                    "2023 - Album2": {
                        "_files": [("track1.mp3", "/fake/path/track1.mp3")]
                    }
                }
            }
        }
        self.update_tree_view()

    def scan_folder(self):
        """Сканирование выбранной папки"""
        folder_path = filedialog.askdirectory(title="Выберите корневую папку")
        if not folder_path:
            return

        self.status_bar.config(text=f"Сканирование: {folder_path}", fg="blue")
        self.root.update()

        try:
            self.music_library.clear()
            self._scan_folder_recursive(folder_path, self.music_library)
            self.update_tree_view()
            self.status_bar.config(text=f"Готово: {len(self.tree.get_children())} папок", fg="green")
        except Exception as e:
            self.status_bar.config(text=f"Ошибка: {str(e)}", fg="red")

    def _scan_folder_recursive(self, current_path, node):
        """Рекурсивное сканирование папок"""
        for entry in os.listdir(current_path):
            full_path = os.path.join(current_path, entry)

            if os.path.isdir(full_path):
                # Обработка подпапки
                if entry not in node:
                    node[entry] = {}
                self._scan_folder_recursive(full_path, node[entry])
            elif entry.lower().endswith(self.supported_formats):
                # Обработка аудиофайла
                if "_files" not in node:
                    node["_files"] = []
                node["_files"].append((entry, full_path))

    def update_tree_view(self):
        """Обновление отображения дерева"""
        self.tree.delete(*self.tree.get_children())
        self._build_tree_recursive("", self.music_library)

    def _build_tree_recursive(self, parent_id, node):
        """Рекурсивное построение дерева"""
        for name, content in node.items():
            if name == "_files":
                # Добавление файлов
                for file_name, file_path in content:
                    self.tree.insert(
                        parent_id,
                        "end",
                        text=file_name,
                        values=("file", file_path),
                        tags=("file",)
                    )
            else:
                # Добавление папки
                folder_id = self.tree.insert(
                    parent_id,
                    "end",
                    text=name,
                    values=("folder", ""),
                    tags=("folder",)
                )
                self._build_tree_recursive(folder_id, content)

    def search_music(self, query):
        """Поиск по коллекции"""
        query = query.lower().strip()
        if not query:
            for item in self.tree.get_children():
                self.tree.item(item, open=False)
                self._reset_item_visibility(item)
            return

        for item in self.tree.get_children():
            self._search_item(item, query)

    def _search_item(self, item, query):
        """Рекурсивный поиск элементов"""
        item_text = self.tree.item(item, "text").lower()

        # Показываем/скрываем элементы
        if query in item_text:
            self.tree.item(item, open=True)
            self._highlight_parents(item)
        else:
            self._hide_item_if_no_matches(item, query)

        # Рекурсивная обработка дочерних элементов
        for child in self.tree.get_children(item):
            self._search_item(child, query)

    def _highlight_parents(self, item):
        """Раскрытие родительских папок для найденного элемента"""
        parent = self.tree.parent(item)
        while parent:
            self.tree.item(parent, open=True)
            parent = self.tree.parent(parent)

    def _hide_item_if_no_matches(self, item, query):
        """Скрытие элементов, не соответствующих запросу"""
        has_visible_children = any(
            query in self.tree.item(child, "text").lower()
            for child in self.tree.get_children(item)
        )

        if not has_visible_children and query not in self.tree.item(item, "text").lower():
            self.tree.detach(item)

    def _reset_item_visibility(self, item):
        """Сброс видимости всех элементов"""
        self.tree.reattach(item, self.tree.parent(item), "end")
        for child in self.tree.get_children(item):
            self._reset_item_visibility(child)

    def play_selected(self, event=None):
        """Воспроизведение выбранного"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        paths = []
        names = []

        for item in selected_items:
            item_data = self.tree.item(item)
            if item_data["values"][0] == "file":
                paths.append(item_data["values"][1])
                names.append(item_data["text"])
            elif item_data["values"][0] == "folder":
                self._collect_files_from_folder(item, paths, names)

        if paths:
            self._play_in_foobar(paths, " | ".join(names))

    def _collect_files_from_folder(self, folder_item, paths, names):
        """Сбор всех файлов из папки"""
        for child in self.tree.get_children(folder_item):
            child_data = self.tree.item(child)
            if child_data["values"][0] == "file":
                paths.append(child_data["values"][1])
                names.append(child_data["text"])
            elif child_data["values"][0] == "folder":
                self._collect_files_from_folder(child, paths, names)

    def _play_in_foobar(self, file_paths, display_name):
        """Запуск воспроизведения в foobar2000"""
        try:
            subprocess.Popen([self.foobar_path, "/play"] + file_paths)
            self.status_bar.config(text=f"Воспроизведение: {display_name[:50]}...", fg="blue")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить foobar2000:\n{str(e)}")

    def add_to_playlist(self):
        """Добавление в плейлист foobar2000"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        paths = []
        for item in selected_items:
            item_data = self.tree.item(item)
            if item_data["values"][0] == "file":
                paths.append(item_data["values"][1])
            elif item_data["values"][0] == "folder":
                self._collect_files_from_folder(item, paths, [])

        if paths:
            try:
                subprocess.Popen([self.foobar_path, "/add"] + paths)
                self.status_bar.config(text=f"Добавлено {len(paths)} треков в плейлист", fg="green")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить в плейлист:\n{str(e)}")

    def stop_foobar(self):
        """Остановка воспроизведения"""
        try:
            subprocess.Popen([self.foobar_path, "/stop"])
            self.status_bar.config(text="Воспроизведение остановлено", fg="black")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить foobar2000:\n{str(e)}")

    def open_in_explorer(self):
        """Открытие папки в проводнике"""
        selected = self.tree.focus()
        if not selected:
            return

        item_data = self.tree.item(selected)
        if item_data["values"][0] == "file":
            path = os.path.dirname(item_data["values"][1])
        else:
            path = self._find_folder_path(selected)

        if path and os.path.exists(path):
            os.startfile(path)

    def _find_folder_path(self, folder_item):
        """Поиск физического пути к папке в дереве"""
        parts = []
        current_item = folder_item

        while current_item:
            item_data = self.tree.item(current_item)
            parts.insert(0, item_data["text"])
            current_item = self.tree.parent(current_item)

        # Попытка найти существующий путь
        test_path = os.path.join(*parts)
        if os.path.exists(test_path):
            return test_path

        return None

    def delete_item(self):
        """Удаление выбранных элементов"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить {len(selected_items)} выбранных элементов?"
        )
        if not confirm:
            return

        for item in selected_items:
            self._delete_item_recursive(item)

        self.update_tree_view()
        self.status_bar.config(text=f"Удалено {len(selected_items)} элементов", fg="orange")

    def _delete_item_recursive(self, item):
        """Рекурсивное удаление элемента из структуры данных"""
        parent = self.tree.parent(item)
        if not parent:  # Корневой элемент
            return

        item_data = self.tree.item(item)
        parent_data = self.tree.item(parent)

        # Удаление из структуры данных
        if parent == "":  # Верхний уровень
            if item_data["text"] in self.music_library:
                del self.music_library[item_data["text"]]
        else:
            # Находим соответствующий узел в структуре данных
            current_node = self.music_library
            path = []

            # Строим путь от корня к элементу
            current_item = item
            while current_item and current_item != "":
                path.insert(0, self.tree.item(current_item, "text"))
                current_item = self.tree.parent(current_item)

            # Находим родительский узел
            for step in path[:-1]:
                if step in current_node:
                    current_node = current_node[step]
                else:
                    return

            # Удаляем целевой узел
            if path[-1] in current_node:
                del current_node[path[-1]]

    def clear_library(self):
        """Полная очистка библиотеки"""
        if messagebox.askyesno("Подтверждение", "Очистить всю коллекцию?"):
            self.music_library.clear()
            self.update_tree_view()
            self.status_bar.config(text="Коллекция очищена", fg="red")

    def show_context_menu(self, event):
        """Отображение контекстного меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicCollectionApp(root)
    root.mainloop()