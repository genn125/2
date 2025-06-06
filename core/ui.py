import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from tkinterdnd2 import TkinterDnD, DND_FILES

class MusicCollectionUI:
    def __init__(self, root, library, player):
        self.root = TkinterDnD.Tk()
        self.library = library
        self.player = player
        self._setup_ui()

    def _setup_ui(self):
        self.root.title("Твоя Музыка")
        self.root.geometry("1000x700")

        # Header
        header_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="ТВОЯ МУЗЫКА", font=('Arial', 14, 'bold'), bg="#f0f0f0").pack(side=tk.LEFT)

        # Toolbar
        toolbar = tk.Frame(self.root, padx=5, pady=5)
        toolbar.pack(fill=tk.X)

        scan_btn = tk.Button(toolbar, text="📁 Сканировать папку", command=self._scan_folder, bd=1, relief=tk.RIDGE, padx=10)
        scan_btn.pack(side=tk.LEFT, padx=5)

        right_frame = tk.Frame(toolbar)
        right_frame.pack(side=tk.RIGHT)

        formats_btn = tk.Button(right_frame, text="⚙️ Выбрать форматы", command=self._select_formats, bd=1, relief=tk.RAISED, padx=10)
        formats_btn.pack(side=tk.LEFT, padx=5)

        save_btn = tk.Button(right_frame, text="💾 Сохранить в DOCX", command=self._save_collection, bd=1, relief=tk.RAISED, padx=10)
        save_btn.pack(side=tk.LEFT, padx=5)

        # Treeview
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("type", "name", "path", "size", "date", "new"), show="headings")
        self.tree.tag_configure("folder", background="#f0f0f0", font=('Arial', 10, 'bold'))
        self.tree.tag_configure("file", background="white")
        self.tree.tag_configure("new_file", background="#e6f7ff")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Columns
        self.tree.heading("type", text="Тип", anchor=tk.CENTER)
        self.tree.heading("name", text="Название", anchor=tk.CENTER)
        self.tree.heading("path", text="Путь")
        self.tree.heading("size", text="Размер", anchor=tk.W)
        self.tree.heading("date", text="Дата изменения", anchor=tk.W)
        self.tree.heading("new", text="Статус", anchor=tk.W)

        self.tree.column("type", width=50, stretch=tk.NO)
        self.tree.column("name", width=220, stretch=tk.YES)
        self.tree.column("path", width=500, stretch=tk.YES)
        self.tree.column("size", width=60, stretch=tk.NO)
        self.tree.column("date", width=100, stretch=tk.NO)
        self.tree.column("new", width=40, stretch=tk.NO)

        # Player controls
        player_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=8)
        player_frame.pack(fill=tk.X)

        player_buttons = [
            ("▶ Воспроизвести", lambda: self.player.play_selected(self.tree)),
            ("⏏ В плейлист", lambda: self.player.add_to_playlist(self.tree)),
            ("⏹ Стоп", self.player.stop_foobar)
        ]
        for text, cmd in player_buttons:
            btn = tk.Button(player_frame, text=text, command=cmd, bg="#f8f8f8", padx=10)
            btn.pack(side=tk.LEFT, padx=5)

        self.status_bar = tk.Label(player_frame, text="Готов к работе", bg="#e0e0e0", fg="#333333", anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Воспроизвести", command=lambda: self.player.play_selected(self.tree))
        self.context_menu.add_command(label="Добавить в плейлист", command=lambda: self.player.add_to_playlist(self.tree))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Открыть в проводнике", command=self._open_in_explorer)
        self.context_menu.add_command(label="Удалить", command=self._delete_item)

        # Bindings
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.player.play_selected(self.tree))

        # Drag and Drop
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drop(self, event):
        success, message = self.player.handle_drop(event)
        self.update_status(message, "green" if success else "red")

    def _select_formats(self):
        self.library.show_format_selection(self.root)

    def _scan_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку с музыкой")
        if folder_path:
            success, message = self.library.scan_folder(folder_path, parent=self.root)
            if success:
                self.update_tree_view(self.library.get_library())
                self.update_status(message, "green")
            else:
                self.update_status(message, "red")
                if "Не выбрано ни одного формата" not in message:
                    messagebox.showwarning("Внимание", message)

    def _save_collection(self):
        success, result = self.library.save_to_docx()
        if success:
            self.update_status(f"Коллекция сохранена: {result}", "green")
        else:
            self.update_status(f"Ошибка сохранения: {result}", "red")
            messagebox.showerror("Ошибка", f"Не удалось сохранить коллекцию:\n{result}")

    def _open_in_explorer(self):
        selected = self.tree.focus()
        if not selected:
            return

        item_data = self.tree.item(selected)
        if item_data["values"][0] == "file":
            path = os.path.dirname(item_data["values"][2])
        else:
            path = self._find_folder_path(selected)
        if path and os.path.exists(path):
            os.startfile(path)

    def _delete_item(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        confirm = messagebox.askyesno("Подтверждение", f"Удалить {len(selected_items)} выбранных элементов?")
        if confirm:
            for item in selected_items:
                self._delete_item_recursive(item)
            self.update_tree_view(self.library.get_library())
            self.update_status(f"Удалено {len(selected_items)} элементов", "orange")

    def _delete_item_recursive(self, item):
        pass

    def _find_folder_path(self, folder_item):
        item_data = self.tree.item(folder_item)
        if item_data["values"][0] == "file":
            return os.path.dirname(item_data["values"][2])

    def update_tree_view(self, library):
        self.tree.delete(*self.tree.get_children())
        self._build_tree_recursive("", library)

    def _build_tree_recursive(self, parent_id, node):
        for name, content in node.items():
            if name == "_files":
                for file_name, file_path, is_new in content:
                    try:
                        abs_path = os.path.abspath(file_path) if file_path else ""
                        abs_path = abs_path.replace('/', '\\')

                        file_stats = os.stat(abs_path)
                        size = f"{file_stats.st_size / 1048576:.1f} MB"
                        date = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')

                        tags = ("new_file",) if is_new else ("file",)

                        self.tree.insert(
                            parent_id,
                            "end",
                            text=file_name,
                            values=(
                                "file",
                                file_name,
                                abs_path,
                                size,
                                date,
                                "NEW" if is_new else ""
                            ),
                            tags=tags
                        )
                    except Exception:
                        continue

            else:
                folder_id = self.tree.insert(
                    parent_id,
                    "end",
                    text=name,
                    values=(
                        "folder",
                        name,
                        "",
                        "",
                        "",
                        ""
                    ),
                    tags=("folder",)
                )
                self._build_tree_recursive(folder_id, content)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def update_status(self, text, color="black"):
        self.status_bar.config(text=text, fg=color)

##########################################################################

# Рабочий код без перетаскивания


# import tkinter as tk
# from tkinter import ttk, Menu, messagebox, filedialog
# import os
# from datetime import datetime
# from tkinterdnd2 import TkinterDnD, DND_FILES  # Импорт для DnD
#
# class MusicCollectionUI:
#     def __init__(self, root, library, player):
#         self.root = TkinterDnD.Tk()  # Используем TkinterDnD вместо tk.Tk
#         self.library = library
#         self.player = player
#         self._setup_ui()
#
#     def _setup_ui(self):
#         self.root.title("Твоя Музыка")
#         self.root.geometry("1200x700")
# # Заголовок
#         header_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
#         header_frame.pack(fill=tk.X)
#         tk.Label(header_frame, text="ТВОЯ МУЗЫКА",
#                  font=('Arial', 14, 'bold'), bg="#f0f0f0").pack(side=tk.LEFT)
# # Toolbar с кнопками
#         toolbar = tk.Frame(self.root, padx=5, pady=5)
#         toolbar.pack(fill=tk.X)
# # Кнопка сканирования слева
#         scan_btn = tk.Button(toolbar, text="📁 Сканировать папку",command=self._scan_folder, bd=1, relief=tk.RIDGE, padx=10)
#         scan_btn.pack(side=tk.LEFT, padx=5)
# # Кнопки справа
#         right_frame = tk.Frame(toolbar)
#         right_frame.pack(side=tk.RIGHT)
# # Кнопка выбора форматов
#         formats_btn = tk.Button(right_frame, text="⚙️ Выбрать форматы",command=self._select_formats, bd=1, relief=tk.RAISED, padx=10)
#         formats_btn.pack(side=tk.LEFT, padx=5)
# # Кнопка сохранения
#         save_btn = tk.Button(right_frame, text="💾 Сохранить в DOCX",command=self._save_collection, bd=1, relief=tk.RAISED, padx=10)
#         save_btn.pack(side=tk.LEFT, padx=5)
# # Treeview
#         tree_frame = tk.Frame(self.root)
#         tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
#         self.tree = ttk.Treeview(tree_frame, columns=("type", "name", "path", "size", "date", "new"), show="headings")
#         self.tree.tag_configure("folder", background="#f0f0f0", font=('Arial', 10, 'bold')) # фон папок
#         self.tree.tag_configure("file", background="white") # фон файлов
#         self.tree.tag_configure("new_file", background="#e6f7ff") # новые файлы
# # Скролл бар
#         scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.tree.configure(yscrollcommand=scrollbar.set)
#         self.tree.pack(fill=tk.BOTH, expand=True)
# # Настраиваем колонки, anchor - выравнивание (если нет - CENTER) n - право, w - лево, n - верх, s - низ
#         self.tree.heading("type", text="Тип")  # Добавьте эту строку, если хотите отображать тип
#         self.tree.heading("name", text="Название", anchor=tk.CENTER)
#         self.tree.heading("path", text="Путь")
#         self.tree.heading("size", text="Размер", anchor=tk.W)
#         self.tree.heading("date", text="Дата изменения", anchor=tk.W)
#         self.tree.heading("new", text="Статус", anchor=tk.W)
# # Настраиваем параметры колонок, width - ширина, tk.NO - запрет растяжения, anchor - выравнивание
#         self.tree.column("type", width=200, stretch=tk.YES)
#         self.tree.column("name", width=220, stretch=tk.YES)
#         self.tree.column("path", width=500, stretch=tk.YES)
#         self.tree.column("size", width=60, stretch=tk.YES)
#         self.tree.column("date", width=100, stretch=tk.YES)
#         self.tree.column("new", width=40, stretch=tk.YES)
# # Управление плеером
#         player_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=8)
#         player_frame.pack(fill=tk.X)
# # Кнопки плеера
#         player_buttons = [
#             ("▶ Воспроизвести", lambda: self.player.play_selected(self.tree)),
#             ("⏏ В плейлист", lambda: self.player.add_to_playlist(self.tree)),
#             ("⏹ Стоп", self.player.stop_foobar)
#         ]
#         for text, cmd in player_buttons:
#             btn = tk.Button(player_frame, text=text, command=cmd, bg="#f8f8f8", padx=10)
#             btn.pack(side=tk.LEFT, padx=5)
# # Строка состояния
#         self.status_bar = tk.Label(player_frame, text="Готов к работе", bg="#e0e0e0", fg="#333333", anchor=tk.W)
#         self.status_bar.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
# # Контекстное меню
#         self.context_menu = Menu(self.root, tearoff=0)
#         self.context_menu.add_command(label="Воспроизвести", command=lambda: self.player.play_selected(self.tree))
#         self.context_menu.add_command(label="Добавить в плейлист",command=lambda: self.player.add_to_playlist(self.tree))
#         self.context_menu.add_separator()
#         self.context_menu.add_command(label="Открыть в проводнике", command=self._open_in_explorer)
#         self.context_menu.add_command(label="Удалить", command=self._delete_item)
# # Привязки
#         self.tree.bind("<Button-3>", self.show_context_menu)
#         self.tree.bind("<Double-1>", lambda e: self.player.play_selected(self.tree))
# # Включение drag-and-drop
#         self.tree.bind("<DragEnter>", self._on_drag_enter)
#         self.tree.bind("<DragLeave>", self._on_drag_leave)
#         self.tree.bind("<B1-Motion>", self._on_drag_motion)
#         self.tree.bind("<ButtonRelease-1>", self._on_drop)
#         # В ui.py при настройке интерфейса:
#         self.tree.bind("<<Drop>>", lambda e: self.player.handle_drop(e))
# # Настройка drag-and-drop
#         self.tree.drop_target_register(DND_FILES)
#         self.tree.dnd_bind('<<Drop>>', self._on_drop)
#         self.tree.dnd_target = True  # Разрешаем принимать перетаскиваемые объекты
#
#     def _on_drop(self, event):
#         """Обработчик события перетаскивания."""
#         success, message = self.player.handle_drop(event)
#         self.update_status(message, "green" if success else "red")
#
#     def _on_drag_enter(self, event):
#         """Курсор с файлом вошел в TreeView."""
#         self.tree.config(cursor="hand2")  # Меняем курсор
#         return True
#
#     def _on_drag_leave(self, event):
#         """Курсор с файлом вышел из TreeView."""
#         self.tree.config(cursor="")
#         return True
#
#     def _on_drop(self, event):
#         """Обработка дропа файлов/папок."""
#         self.tree.config(cursor="")
#
#         # Получаем пути из перетаскиваемых объектов
#         paths = []
#         for item in self.root.tk.splitlist(event.data):
#             path = item.strip('{}')  # Удаляем лишние символы (для Windows)
#             if os.path.isdir(path):
#                 # Сканируем папку и добавляем все аудиофайлы
#                 for root_dir, _, files in os.walk(path):
#                     for file in files:
#                         if file.lower().endswith(('.mp3', '.flac', '.wav')):  # Фильтр по форматам
#                             paths.append(os.path.join(root_dir, file))
#             elif os.path.isfile(path):
#                 paths.append(path)
#
#         if paths:
#             self.player.add_to_playlist(paths)  # Передаем пути в плеер
#             self.update_status(f"Добавлено {len(paths)} треков", "green")
#
#     def _select_formats(self):
#         """Открывает окно выбора форматов"""
#         self.library.show_format_selection(self.root)
#
#     def _treeview_sort_column(self, col, reverse):
# # Получаем все элементы
#         items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
# # Сортируем элементы
#         items.sort(reverse=reverse)
# # Перемещаем элементы в отсортированном порядке
#         for index, (val, k) in enumerate(items):
#             self.tree.move(k, "", index)
# # Устанавливаем обратную сортировку для следующего клика
#         self.tree.heading(col, command=lambda: self._treeview_sort_column(col, not reverse))
#
#     def _scan_folder(self):
#         folder_path = filedialog.askdirectory(title="Выберите папку с музыкой")
#         if folder_path:
# # Передаем self.root как parent для окна выбора форматов
#             success, message = self.library.scan_folder(folder_path, parent=self.root)
#             if success:
#                 self.update_tree_view(self.library.get_library())
#                 self.update_status(message, "green")
#             else:
#                 self.update_status(message, "red")
#                 if "Не выбрано ни одного формата" not in message:  # Не показываем для отмены выбора
#                     messagebox.showwarning("Внимание", message)
#
#     def _save_collection(self):
#         success, result = self.library.save_to_docx()
#         if success:
#             self.update_status(f"Коллекция сохранена: {result}", "green")
#         else:
#             self.update_status(f"Ошибка сохранения: {result}", "red")
#             messagebox.showerror("Ошибка", f"Не удалось сохранить коллекцию:\n{result}")
#
#     def _open_in_explorer(self):
#         selected = self.tree.focus()
#         if not selected:
#             return
#
#         item_data = self.tree.item(selected)
#         if item_data["values"][0] == "file":
#             path = os.path.dirname(item_data["values"][2])
#         else:
#             path = self._find_folder_path(selected)
#         if path and os.path.exists(path):
#             os.startfile(path)
#
#     def _delete_item(self):
#         selected_items = self.tree.selection()
#         if not selected_items:
#             return
#         confirm = messagebox.askyesno("Подтверждение",f"Удалить {len(selected_items)} выбранных элементов?")
#         if confirm:
#             for item in selected_items:
#                 self._delete_item_recursive(item)
#             self.update_tree_view(self.library.get_library())
#             self.update_status(f"Удалено {len(selected_items)} элементов", "orange")
#
#     def _delete_item_recursive(self, item):
# # Заглушка для реализации удаления
#         pass
#
#     def _find_folder_path(self, folder_item):
# # Поиск пути к папке
#         item_data = self.tree.item(folder_item)
#         if item_data["values"][0] == "file":
#             return os.path.dirname(item_data["values"][2])
#
#     def update_tree_view(self, library):
#         self.tree.delete(*self.tree.get_children())
#         self._build_tree_recursive("", library)
#
#     def _build_tree_recursive(self, parent_id, node):
#         for name, content in node.items():
#             if name == "_files":
#                 for file_name, file_path, is_new in content:
#                     try:
#                         # Нормализуем путь (абсолютный + правильные разделители)
#                         abs_path = os.path.abspath(file_path) if file_path else ""
#                         abs_path = abs_path.replace('/', '\\')
#
#                         # Получаем информацию о файле
#                         file_stats = os.stat(abs_path)
#                         size = f"{file_stats.st_size / 1048576:.1f} MB"
#                         date = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')
#
#                         # Определяем теги для отображения
#                         tags = ("new_file",) if is_new else ("file",)
#
#                         # Вставляем данные в treeview
#                         self.tree.insert(
#                             parent_id,
#                             "end",
#                             text=file_name,
#                             values=(
#                                 "file",  # Тип элемента (добавлено)
#                                 file_name,  # Название
#                                 abs_path,  # Абсолютный путь
#                                 size,  # Размер
#                                 date,  # Дата изменения
#                                 "NEW" if is_new else ""  # Статус
#                             ),
#                             tags=tags
#                         )
#
#                     except FileNotFoundError:
#                         print(f"Файл не найден: {file_path}")
#                         continue
#                     except PermissionError:
#                         print(f"Нет доступа к файлу: {file_path}")
#                         continue
#                     except Exception as e:
#                         print(f"Ошибка обработки файла {file_path}: {str(e)}")
#                         continue
#
#             else:  # Обработка папок
#                 folder_id = self.tree.insert(
#                     parent_id,
#                     "end",
#                     text=name,
#                     values=(
#                         name,  # Название папки
#                         "",  # Путь (пусто для папок)
#                         "",  # Размер (пусто)
#                         "",  # Дата (пусто)
#                         ""  # Статус (пусто)
#                     ),
#                     tags=("folder",)
#                 )
#                 self._build_tree_recursive(folder_id, content)
#
#     def show_context_menu(self, event):
#         item = self.tree.identify_row(event.y)
#         if item:
#             self.tree.selection_set(item)
#             self.context_menu.post(event.x_root, event.y_root)
#
#     def update_status(self, text, color="black"):
#         self.status_bar.config(text=text, fg=color)
