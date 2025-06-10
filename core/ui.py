import tkinter as tk
from tkinter import ttk, Menu, messagebox, filedialog
import os
from datetime import datetime
from tkinter.constants import RIGHT


class MusicCollectionUI:
    def __init__(self, root, library, player):
        self.root = root
        self.library = library
        self.player = player
        self._setup_ui()

    def _setup_ui(self):
        self.root.title("Твои файлы")
        self.root.geometry("1200x600")

        # Заголовок (Фрейм) с (ГЛАВНАЯ ХРЕНЬ, ОТВЕЧАЕТ ЗА РАСПОЛОЖЕНИЕ ВСЕГО ТЕКСТА СВЕРХУ)
        header_frame = tk.Frame(self.root, bg="#FFFFE0", padx=10, pady=0)  # цвет подложки светло-жёлтый
        header_frame.pack(fill=tk.X)

        # Метка "ПОИСК:" жирным шрифтом
        search_label = tk.Label(
            header_frame,
            text="ПОИСК:",
            font=('Arial', 10, 'bold underline'),
            bg="#FFFFE0" # цвет подложки светло-жёлтый
        )
        search_label.pack(side=tk.LEFT)

        # Фрейм для категорий форматов
        formats_frame = tk.Frame(header_frame)
        formats_frame.pack(side=tk.LEFT, padx=(10,500))

        # Метка (многострочная) для отображения форматов
        self.formats_text = tk.Text(
            formats_frame,
            height=2, # высота в строках
            width=55, # ширина в символах.
            bg="#20B2AA", # цвет подложки «светлый морской зелёный»
            font=('Arial', 10),
            wrap=tk.WORD, # WORD позволяет переносить слова на новую строку целиком, а не по буквам.
            padx=10,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        #self.formats_text.pack()
        # Скролл бар для выбранных категорий
        scrollbar = ttk.Scrollbar(formats_frame, orient="vertical", command=self.formats_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.formats_text.config(yscrollcommand=scrollbar.set)
        self.formats_text.pack(fill=tk.BOTH, expand=True)


        self._update_formats_display()

        # Toolbar с кнопками
        toolbar = tk.Frame(self.root, padx=5, pady=5)
        toolbar.pack(fill=tk.X)
        # Кнопка сканирования слева
        scan_btn = tk.Button(toolbar, text="📁 Сканировать папку", command=self._scan_folder,
                             bd=1, relief=tk.RIDGE, padx=10)
        scan_btn.pack(side=tk.LEFT, padx=5)
        # Кнопки справа
        right_frame = tk.Frame(toolbar)
        right_frame.pack(side=tk.RIGHT)
        # Кнопка выбора форматов
        formats_btn = tk.Button(right_frame, text="⚙️ Выбрать форматы", command=self._select_formats,
                                bd=1, relief=tk.RAISED, padx=10)
        formats_btn.pack(side=tk.LEFT, padx=5)
        # Кнопка сохранения
        save_btn = tk.Button(right_frame, text="💾 Сохранить в DOCX", command=self._save_collection,
                             bd=1, relief=tk.RAISED, padx=10)
        save_btn.pack(side=tk.LEFT, padx=5)

        # Treeview
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(tree_frame, columns=("type", "name", "path", "size", "date"), show="headings")
        self.tree.tag_configure("folder", background="#f0f0f0", font=('Arial', 10, 'bold'))
        self.tree.tag_configure("file", background="white")

        # Скролл бар основного окна с файлами
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Настройка колонок, anchor - выравнивание (если нет - CENTER) n - право, w - лево, n - ве
        self.tree.heading("type", text="Тип", anchor=tk.CENTER)
        self.tree.heading("name", text="Название")
        self.tree.heading("path", text="Путь")
        self.tree.heading("size", text="Размер", anchor=tk.W)
        self.tree.heading("date", text="Дата изменения", anchor=tk.W)

        # Настраиваем параметры колонок, width - ширина, tk.NO - запрет растяжения, anchor - выравнивание
        self.tree.column("type", width=150, stretch=tk.YES)
        self.tree.column("name", width=220, stretch=tk.YES)
        self.tree.column("path", width=500, stretch=tk.YES)
        self.tree.column("size", width=50, stretch=tk.YES)
        self.tree.column("date", width=90, stretch=tk.YES)

        # Управление плеером
        player_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=8)
        player_frame.pack(fill=tk.X)
        # Кнопки плеера
        player_buttons = [
            ("▶ Воспроизвести", lambda: self.player.play_selected(self.tree)),
            ("⏏ В плейлист", lambda: self.player.add_to_playlist(self.tree)),
            ("⏹ Стоп", self.player.stop_foobar)
        ]
        for text, cmd in player_buttons:
            btn = tk.Button(player_frame, text=text, command=cmd, bg="#f8f8f8", padx=10)
            btn.pack(side=tk.LEFT, padx=5)

        # Строка состояния
        self.status_bar = tk.Label(player_frame, text="Готов к работе", bg="#e0e0e0",
                                   fg="#333333", anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Контекстное меню
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Воспроизвести",
                                      command=lambda: self.player.play_selected(self.tree))
        self.context_menu.add_command(label="Добавить в плейлист",
                                      command=lambda: self.player.add_to_playlist(self.tree))
        self.context_menu.add_command(label="Добавить папку в плейлист",
                                      command=lambda: self._add_folder_to_playlist())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Открыть в проводнике", command=self._open_in_explorer)
        self.context_menu.add_command(label="Удалить", command=self._delete_item)

        # Привязки
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.player.play_selected(self.tree))

    def _update_formats_display(self):
        """Обновляет отображение форматов с жирными названиями категорий"""
        self.formats_text.config(state=tk.NORMAL)
        self.formats_text.delete(1.0, tk.END)

        selected_formats = self.library.supported_formats
        if not selected_formats:
            self.formats_text.insert(tk.END, "Форматы не выбраны")
            self.formats_text.config(state=tk.DISABLED)
            return

        # Группируем форматы по категориям
        format_groups = {
            'Аудио': [f for f in selected_formats if f in self.library.all_formats['Аудио']],
            'Изображения': [f for f in selected_formats if f in self.library.all_formats['Изображения']],
            'Видео': [f for f in selected_formats if f in self.library.all_formats['Видео']],
            'Документы': [f for f in selected_formats if f in self.library.all_formats['Документы']],
            'Исполняемые': [f for f in selected_formats if f in self.library.all_formats['Исполняемые']],
            'Разные': [f for f in selected_formats if f in self.library.all_formats['Разные']]
        }

        # Добавляем каждую категорию с жирным названием
        first_line = True
        for group, formats in format_groups.items():
            if formats:
                if not first_line:
                    self.formats_text.insert(tk.END, "\n")
                self.formats_text.insert(tk.END, group + ":   ", 'bold')
                self.formats_text.insert(tk.END, ', '.join(formats))
                first_line = False

        # Настраиваем тег для жирного текста
        self.formats_text.tag_config('bold', font=('Arial', 10, 'bold'))
        self.formats_text.config(state=tk.DISABLED)

    def _select_formats(self):
        """Открывает окно выбора форматов и обновляет отображение"""
        self.library.show_format_selection(self.root)
        self._update_formats_display()

    def _treeview_sort_column(self, col, reverse):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        # Сортируем элементы
        items.sort(reverse=reverse)
        # Перемещаем элементы в отсортированном порядке
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)
            # Устанавливаем обратную сортировку для следующего клика
        self.tree.heading(col, command=lambda: self._treeview_sort_column(col, not reverse))

    def _scan_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку для сканирования")
        if folder_path:
            success, message = self.library.scan_folder(folder_path, parent=self.root)
            if success:
                self.update_tree_view(self.library.get_library())
                self.update_status(message, "green")
                self._update_formats_display()
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
        pass  # Заглушка для реализации удаления

    def _find_folder_path(self, folder_item):
        # Поиск пути к папке
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
                        # Нормализуем путь (абсолютный + правильные разделители)
                        abs_path = os.path.abspath(file_path) if file_path else ""
                        abs_path = abs_path.replace('/', '\\')

                        # Получаем информацию о файле
                        file_stats = os.stat(abs_path)
                        size = f"{file_stats.st_size / 1048576:.1f} MB"
                        date = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')

                        # Определяем теги для отображения
                        tags = ("file",)
                        # Вставляем данные в treeview
                        self.tree.insert(
                            parent_id,
                            "end",
                            text=file_name,
                            values=(
                                "file",  # Вставляем данные в treeview
                                file_name, # Название
                                abs_path, # Абсолютный путь
                                size, # Размер
                                date, # Дата изменения
                            ),
                            tags=tags
                        )

                    except (FileNotFoundError, PermissionError) as e:
                        print(f"Ошибка обработки файла {file_path}: {str(e)}")
                        continue

            else: # Обработка папок
                folder_id = self.tree.insert(
                    parent_id,
                    "end",
                    text=name,
                    values=(
                        name,  # Название папки
                        "", # Путь (пусто для папок)
                        "", # Размер (пусто)
                        "", # Дата (пусто)
                        "" # Статус (пусто)
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

    def _add_folder_to_playlist(self):
        """Добавляет все файлы из выбранной папки в плейлист"""
        selected = self.tree.selection()
        if not selected:
            return
        # Получаем данные о выбранном элементе
        item_data = self.tree.item(selected[0])
        # Если выбран файл - просто добавляем его
        if item_data["values"][0] == "file":
            self.player.add_to_playlist(self.tree)
            return

        # Если выбрана папка - собираем все файлы из нее и подпапок
        paths = []
        self._collect_files_from_tree(self.tree, selected[0], paths)

        if paths:
            success, message = self.player.add_to_playlist(paths=paths)
            self.update_status(message, "green" if success else "red")
        else:
            self.update_status("В папке нет поддерживаемых файлов", "red")

    def _collect_files_from_tree(self, tree, folder_item, paths):
        """Рекурсивно собирает все файлы из папки в дереве"""
        for child in tree.get_children(folder_item):
            child_data = tree.item(child)
            if child_data["values"][0] == "file":
                normalized_path = self.player._normalize_path(child_data["values"][2])
                if normalized_path and normalized_path.lower().endswith(self.player.supported_formats):
                    paths.append(normalized_path)
            elif child_data["values"][0] == "folder":
                self._collect_files_from_tree(tree, child, paths)

