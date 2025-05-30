import tkinter as tk
from tkinter import ttk, Menu, messagebox, filedialog
import os
from datetime import datetime

class MusicCollectionUI:
    def __init__(self, root, library, player):
        self.root = root
        self.library = library
        self.player = player
        self._setup_ui()

    def _setup_ui(self):
        self.root.title("Твоя Музыка")
        self.root.geometry("1000x700")

        # Header
        header_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="ТВОЯ МУЗЫКА",
                font=('Arial', 14, 'bold'), bg="#f0f0f0").pack(side=tk.LEFT)

        # Toolbar with buttons
        toolbar = tk.Frame(self.root, padx=5, pady=5)
        toolbar.pack(fill=tk.X)

        # Кнопки (удалены кнопки поиска)
        buttons = [
            ("📁 Сканировать папку", self._scan_folder),
            ("💾 Сохранить", self._save_collection)
        ]

        for text, cmd in buttons:
            btn = tk.Button(toolbar, text=text, command=cmd, bd=1, relief=tk.RIDGE, padx=10)
            btn.pack(side=tk.LEFT, padx=10)

        # # Treeview версию с колонками
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(tree_frame, columns=("name", "path", "size", "date"), show="headings")
        self.tree.tag_configure("folder", background="#f0f0f0", font=('Arial', 10, 'bold'))# фон папок
        self.tree.tag_configure("file", background="white")# фон файлов

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

# Настраиваем колонки, anchor - выравнивание (n - право, w - лево, n - верх, s - низ)
        self.tree.heading("name", text="Название", anchor=tk.CENTER)
        self.tree.heading("path", text="Путь", anchor=tk.SW)
        self.tree.heading("size", text="Размер", anchor=tk.W)
        self.tree.heading("date", text="Дата изменения", anchor=tk.W)

# Настраиваем параметры колонок, width - ширина, tk.NO - запрет растяжения, anchor - выравнивание
        self.tree.column("name", width=200, stretch=tk.YES)
        self.tree.column("path", width=300, stretch=tk.YES)
        self.tree.column("size", width=100, stretch=tk.YES)
        self.tree.column("date", width=150, stretch=tk.YES)

        # Разрешаем изменение размера колонок
        for col in ("name", "path", "size", "date"):
            self.tree.heading(col, command=lambda _col=col: self._treeview_sort_column(_col, False))

        # Player controls frame
        player_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=8)
        player_frame.pack(fill=tk.X)

        # Player buttons
        player_buttons = [
            ("▶ Воспроизвести", lambda: self.player.play_selected(self.tree)),
            ("⏏ В плейлист", lambda: self.player.add_to_playlist(self.tree)),
            ("⏹ Стоп", self.player.stop_foobar)
        ]

        for text, cmd in player_buttons:
            btn = tk.Button(player_frame, text=text, command=cmd, bg="#f8f8f8", padx=10)
            btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_bar = tk.Label(player_frame, text="Готов к работе",
                                 bg="#e0e0e0", fg="#333333", anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Context menu
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Воспроизвести", command=lambda: self.player.play_selected(self.tree))
        self.context_menu.add_command(label="Добавить в плейлист", command=lambda: self.player.add_to_playlist(self.tree))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Открыть в проводнике", command=self._open_in_explorer)
        self.context_menu.add_command(label="Удалить", command=self._delete_item)

        # Bindings
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.player.play_selected(self.tree))

    def _treeview_sort_column(self, col, reverse):
        # Получаем все элементы
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # Сортируем элементы
        items.sort(reverse=reverse)

        # Перемещаем элементы в отсортированном порядке
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

        # Устанавливаем обратную сортировку для следующего клика
        self.tree.heading(col, command=lambda: self._treeview_sort_column(col, not reverse))

    def _scan_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку с музыкой")
        if folder_path:
            if self.library.scan_folder(folder_path):
                self.update_tree_view(self.library.get_library())
                self.update_status(f"Добавлено: {folder_path}", "green")

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
            path = os.path.dirname(item_data["values"][1])
        else:
            path = self._find_folder_path(selected)

        if path and os.path.exists(path):
            os.startfile(path)

    def _delete_item(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить {len(selected_items)} выбранных элементов?"
        )
        if confirm:
            for item in selected_items:
                self._delete_item_recursive(item)
            self.update_tree_view(self.library.get_library())
            self.update_status(f"Удалено {len(selected_items)} элементов", "orange")

    def _delete_item_recursive(self, item):
        # Реализация удаления из дерева
        pass

    def _find_folder_path(self, folder_item):
        # Реализация поиска пути к папке
        pass

    def update_tree_view(self, library):
        self.tree.delete(*self.tree.get_children())
        self._build_tree_recursive("", library)

    def _build_tree_recursive(self, parent_id, node):
        for name, content in node.items():
            if name == "_files":
                for file_name, file_path in content:
                    # Получаем информацию о файле
                    file_stats = os.stat(file_path)
                    size = f"{file_stats.st_size / 1024:.1f} KB"
                    date = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')

                    self.tree.insert(
                        parent_id, "end",
                        values=(file_name, file_path, size, date),
                        tags=("file",)
                    )
            else:
                folder_id = self.tree.insert(
                    parent_id, "end",
                    text=name,
                    values=(name, "", "", ""),
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