import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from collections import defaultdict


class MusicCollectionApp:
    def __init__(self, root):
        """Инициализация главного окна приложения"""
        self.root = root
        self.root.title("Твоя Музыка")  # Заголовок окна
        self.root.geometry("1000x700")  # Размер окна

        # Конфигурация путей и форматов
        self.foobar_path = r"C:\Program Files (x86)\foobar2000\foobar2000.exe"  # Путь к foobar2000
        self.supported_formats = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma')  # Поддерживаемые форматы

        # Структуры данных
        self.music_library = defaultdict(lambda: defaultdict(dict))  # Основное хранилище
        self._original_library = None  # Резервная копия для восстановления после поиска

        # Инициализация интерфейса
        self._setup_ui()

    def _setup_ui(self):
        """Создание пользовательского интерфейса"""
        # Верхняя панель с заголовком
        header_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="ТВОЯ МУЗЫКА",
                 font=('Arial', 14, 'bold'), bg="#f0f0f0").pack(side=tk.LEFT)

        # Панель инструментов
        toolbar = tk.Frame(self.root, padx=5, pady=5)
        toolbar.pack(fill=tk.X)

        # Кнопки управления
        buttons = [
            ("📁 Сканировать папку", self.scan_folder),
            ("🔍 Поиск", lambda: self.search_music(self.search_entry.get())),
            ("🗑️ Сбросить поиск", self.reset_search)
        ]

        for text, cmd in buttons:
            btn = tk.Button(toolbar, text=text, command=cmd, bd=1, relief=tk.RIDGE, padx=10)
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

        self.tree = ttk.Treeview(tree_frame, columns=("type", "path"), show="tree", selectmode="extended")

        # Настройка стилей для дерева
        self.tree.tag_configure("folder", background="#f0f0f0", font=('Arial', 10, 'bold'))
        self.tree.tag_configure("file", background="white")

        # Scrollbar для дерева
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Панель управления плеером
        player_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=8)
        player_frame.pack(fill=tk.X)

        # Кнопки управления плеером
        player_controls = [
            ("▶ Воспроизвести", self.play_selected),
            ("⏏ В плейлист", self.add_to_playlist),
            ("⏹ Стоп", self.stop_foobar)
        ]

        for text, cmd in player_controls:
            btn = tk.Button(player_frame, text=text, command=cmd, bg="#f8f8f8", padx=10)
            btn.pack(side=tk.LEFT, padx=5)

        # Строка состояния
        self.status_bar = tk.Label(player_frame, text="Готов к работе",
                                   bg="#e0e0e0", fg="#333333", anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Воспроизвести", command=self.play_selected)
        self.context_menu.add_command(label="Добавить в плейлист", command=self.add_to_playlist)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Открыть в проводнике", command=self.open_in_explorer)
        self.context_menu.add_command(label="Удалить", command=self.delete_item)

        # Привязка событий
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.play_selected)

    def scan_folder(self):
        """Сканирование выбранной папки и добавление музыки в коллекцию"""
        folder_path = filedialog.askdirectory(title="Выберите папку с музыкой")
        if not folder_path:
            return

        self.status_bar.config(text=f"Сканирование: {folder_path}", fg="blue")
        self.root.update()  # Обновляем интерфейс

        try:
            # Сохраняем копию оригинальной библиотеки перед изменением
            if not hasattr(self, '_original_library'):
                self._original_library = defaultdict(lambda: defaultdict(dict))

            # Рекурсивное сканирование
            self._scan_folder_recursive(folder_path, self.music_library)
            self._original_library = self.music_library.copy()
            self.update_tree_view()
            self.status_bar.config(text=f"Добавлено: {folder_path}", fg="green")
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
        """Обновление отображения дерева коллекции"""
        self.tree.delete(*self.tree.get_children())  # Очищаем текущее отображение

        # Рекурсивное построение дерева
        self._build_tree_recursive("", self.music_library)

    def _build_tree_recursive(self, parent_id, node):
        """Рекурсивное построение элементов дерева"""
        for name, content in node.items():
            if name == "_files":
                # Добавление файлов
                for file_name, file_path in content:
                    self.tree.insert(
                        parent_id, "end",
                        text=file_name,
                        values=("file", file_path),
                        tags=("file",)
                    )
            else:
                # Добавление папки
                folder_id = self.tree.insert(
                    parent_id, "end",
                    text=name,
                    values=("folder", ""),
                    tags=("folder",)
                )
                self._build_tree_recursive(folder_id, content)

    def search_music(self, query):
        """Фильтрация музыки по поисковому запросу"""
        query = query.lower().strip()

        # При первом поиске сохраняем оригинальную библиотеку
        if not hasattr(self, '_original_library'):
            self._original_library = self.music_library.copy()

        if not query:
            # Если запрос пустой - показываем всю коллекцию
            self.music_library = self._original_library.copy()
            self.update_tree_view()
            return

        # Создаем отфильтрованную копию
        filtered_library = defaultdict(lambda: defaultdict(dict))

        for artist, years in self._original_library.items():
            artist_matches = query in artist.lower()

            for year, albums in years.items():
                for album_name, songs in albums.items():
                    album_matches = (query in album_name.lower()) or artist_matches
                    filtered_songs = [
                        (song, path) for song, path in songs
                        if (query in song.lower()) or album_matches
                    ]

                    if filtered_songs:
                        # Сохраняем структуру папок
                        if artist not in filtered_library:
                            filtered_library[artist] = {}
                        if year not in filtered_library[artist]:
                            filtered_library[artist][year] = {}
                        filtered_library[artist][year][album_name] = filtered_songs

        self.music_library = filtered_library
        self.update_tree_view()
        self.status_bar.config(text=f"Найдено: {query}", fg="blue")

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

    def reset_search(self):
        """Сброс результатов поиска и восстановление полной коллекции"""
        self.search_entry.delete(0, tk.END)  # Очищаем поле поиска
        self.search_music("")  # Сбрасываем фильтрацию
        self.status_bar.config(text="Поиск сброшен. Показана вся коллекция", fg="green")

    # ... (остальные методы: play_selected, add_to_playlist и т.д. остаются без изменений)

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