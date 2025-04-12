import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from collections import defaultdict


class TvojaMuzykaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Твоя Музыка 🎵")
        self.root.geometry("1000x700")
        self.root.iconbitmap(default=self._get_icon_path())  # Добавим иконку

        # Настройки
        self.foobar_path = r"C:\Program Files (x86)\foobar2000\foobar2000.exe"
        self.supported_formats = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma')
        self.music_library = defaultdict(lambda: defaultdict(dict))

        # Стиль
        self._setup_styles()
        self.create_widgets()

        # Стартовое сообщение
        self.status_bar.config(text="Добро пожаловать в 'Твою Музыку'! Начните со сканирования папки.")

    def _get_icon_path(self):
        # Попытка найти иконку (можно заменить на свой файл)
        try:
            return "music.ico"  # Положите файл в папку с программой
        except:
            return None

    def _setup_styles(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("TButton", padding=5, font=('Arial', 9))

    def create_widgets(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="ТВОЯ МУЗЫКА", font=('Arial', 14, 'bold'), bg="#f0f0f0").pack(side=tk.LEFT)

        # Панель инструментов
        tool_frame = tk.Frame(self.root, padx=5, pady=5)
        tool_frame.pack(fill=tk.X)

        buttons = [
            ("🔍 Сканировать папку", self.scan_folder),
            ("➕ Добавить группу", self.add_artist),
            ("💿 Добавить альбом", self.add_album),
            ("🎵 Импорт треков", self.import_music)
        ]

        for text, cmd in buttons:
            btn = tk.Button(tool_frame, text=text, command=cmd, bd=1, relief=tk.RIDGE)
            btn.pack(side=tk.LEFT, padx=2)

        # Поиск
        search_frame = tk.Frame(self.root, pady=5)
        search_frame.pack(fill=tk.X, padx=10)

        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.search_entry.bind("<KeyRelease>", self.search_music)

        # Дерево коллекции
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("Type", "Path"), show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Панель плеера
        player_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=8)
        player_frame.pack(fill=tk.X)

        controls = [
            ("▶ Воспроизвести", self.play_music),
            ("⏏ В плейлист", self.add_to_playlist),
            ("⏹ Стоп", self.stop_foobar)
        ]

        for text, cmd in controls:
            btn = tk.Button(player_frame, text=text, command=cmd, bg="#f8f8f8")
            btn.pack(side=tk.LEFT, padx=5)

        self.current_track_label = tk.Label(
            player_frame,
            text="Готов к воспроизведению",
            bg="#e0e0e0",
            fg="#333333"
        )
        self.current_track_label.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Статус бар
        self.status_bar = tk.Label(
            self.root,
            text="",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#f0f0f0",
            fg="#555555"
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Воспроизвести", command=self.play_selected)
        self.context_menu.add_command(label="Добавить в плейлист", command=self.add_to_playlist)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Удалить", command=self.delete_item)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.play_selected)

    # ... (Все остальные методы остаются без изменений, как в предыдущей версии)
    # (scan_folder, _process_scanned_file, update_tree_view, add_artist,
    #  add_album, import_music, search_music, play_music, play_selected,
    #  _play_in_foobar, add_to_playlist, stop_foobar, delete_item и др.)


if __name__ == "__main__":
    root = tk.Tk()
    app = TvojaMuzykaApp(root)
    root.mainloop()