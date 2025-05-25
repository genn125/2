import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog


class MusicCollectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Музыкальная коллекция с foobar2000")
        self.root.geometry("800x600")

        # Путь к foobar2000 (измените на ваш)
        self.foobar_path = r"D:\Музыка\!foobar2000\foobar2000.exe"

        # Переменные для хранения данных
        self.music_library = {}
        self.current_playing = None

        # Создание интерфейса
        self.create_widgets()

        # Загрузка коллекции
        self.load_collection()

    def create_widgets(self):
        # Панель управления
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.btn_add = tk.Button(control_frame, text="Добавить группу", command=self.add_artist)
        self.btn_add.pack(side=tk.LEFT, padx=5)

        self.btn_add_album = tk.Button(control_frame, text="Добавить альбом", command=self.add_album)
        self.btn_add_album.pack(side=tk.LEFT, padx=5)

        self.btn_import = tk.Button(control_frame, text="Импортировать музыку", command=self.import_music)
        self.btn_import.pack(side=tk.LEFT, padx=5)

        # Поиск
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_music)

        # Дерево коллекции
        self.tree = ttk.Treeview(self.root, columns=("Type", "Path"), show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Плеер
        player_frame = tk.Frame(self.root)
        player_frame.pack(pady=10)

        self.btn_play = tk.Button(player_frame, text="▶ Воспроизвести в foobar2000", command=self.play_music)
        self.btn_play.pack(side=tk.LEFT, padx=5)

        self.btn_add_to_playlist = tk.Button(player_frame, text="＋ Добавить в плейлист", command=self.add_to_playlist)
        self.btn_add_to_playlist.pack(side=tk.LEFT, padx=5)

        self.current_track_label = tk.Label(player_frame, text="Трек не выбран")
        self.current_track_label.pack(side=tk.LEFT, padx=10)

        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Воспроизвести в foobar2000", command=self.play_selected)
        self.context_menu.add_command(label="Добавить в плейлист", command=self.add_to_playlist)
        self.context_menu.add_command(label="Удалить", command=self.delete_item)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.play_selected)

    def load_collection(self):
        # Здесь можно добавить загрузку из файла
        # В демо-версии просто очищаем дерево
        for i in self.tree.get_children():
            self.tree.delete(i)

    def add_artist(self):
        artist_name = simpledialog.askstring("Добавить группу", "Введите название группы:")
        if artist_name and artist_name not in self.music_library:
            self.music_library[artist_name] = {}
            self.tree.insert("", "end", text=artist_name, values=("artist", ""))

    def add_album(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите группу для добавления альбома")
            return

        item = self.tree.item(selected)
        if item["values"][0] != "artist":
            messagebox.showerror("Ошибка", "Выберите группу для добавления альбома")
            return

        artist_name = item["text"]
        album_name = simpledialog.askstring("Добавить альбом", "Введите название альбома:")
        year = simpledialog.askinteger("Добавить альбом", "Введите год выпуска:")

        if album_name and year:
            if year not in self.music_library[artist_name]:
                self.music_library[artist_name][year] = {}

            if album_name not in self.music_library[artist_name][year]:
                self.music_library[artist_name][year][album_name] = []
                album_id = self.tree.insert(selected, "end", text=f"{year} - {album_name}", values=("album", ""))

    def import_music(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите альбом для импорта музыки")
            return

        item = self.tree.item(selected)
        if item["values"][0] != "album":
            messagebox.showerror("Ошибка", "Выберите альбом для импорта музыки")
            return

        files = filedialog.askopenfilenames(title="Выберите музыкальные файлы",
                                            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")])

        if files:
            parent = self.tree.parent(selected)
            artist_item = self.tree.item(parent)
            artist_name = artist_item["text"]

            album_text = item["text"]
            year, album_name = album_text.split(" - ", 1)
            year = int(year)

            for file_path in files:
                song_name = os.path.basename(file_path)
                self.music_library[artist_name][year][album_name].append((song_name, file_path))
                self.tree.insert(selected, "end", text=song_name, values=("song", file_path))

    def search_music(self, event=None):
        query = self.search_entry.get().lower()

        for item in self.tree.get_children():
            self._search_item(item, query)

    def _search_item(self, item, query):
        item_text = self.tree.item(item, "text").lower()
        if query in item_text:
            self.tree.selection_add(item)
            # Раскрываем родительские элементы
            parent = self.tree.parent(item)
            while parent:
                self.tree.item(parent, open=True)
                parent = self.tree.parent(parent)
        else:
            self.tree.selection_remove(item)

        # Рекурсивно проверяем дочерние элементы
        for child in self.tree.get_children(item):
            self._search_item(child, query)

    def play_music(self):
        selected = self.tree.focus()
        if not selected:
            return


        self.play_selected_item(selected)

    def play_selected(self, event=None):
        selected = self.tree.focus()
        if not selected:
            return

        self.play_selected_item(selected)

    def play_selected_item(self, item_id):
        item = self.tree.item(item_id)

        if item["values"][0] == "song":
            self._play_in_foobar([item["values"][1]], item["text"])
        elif item["values"][0] == "album":
            self._play_album(item_id)

    def _play_album(self, album_id):
        paths = []
        for child in self.tree.get_children(album_id):
            item = self.tree.item(child)
            if item["values"][0] == "song":
                paths.append(item["values"][1])

        if paths:
            album_name = self.tree.item(album_id)["text"]
            self._play_in_foobar(paths, f"Альбом: {album_name}")

    def _play_in_foobar(self, file_paths, display_name):
        try:
            # Формируем команду для foobar2000
            # /play немедленно начинает воспроизведение
            # /add добавляет в текущий плейлист
            command = [self.foobar_path, "/play"] + list(file_paths)

            subprocess.Popen(command)
            self.current_playing = file_paths[0] if len(file_paths) == 1 else file_paths
            self.current_track_label.config(text=f"Воспроизводится в foobar2000: {display_name}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить foobar2000: {e}")

    def add_to_playlist(self):
        selected = self.tree.focus()
        if not selected:
            return

        item = self.tree.item(selected)

        if item["values"][0] == "song":
            self._add_files_to_foobar([item["values"][1]], item["text"])
        elif item["values"][0] == "album":
            paths = []
            for child in self.tree.get_children(selected):
                child_item = self.tree.item(child)
                if child_item["values"][0] == "song":
                    paths.append(child_item["values"][1])

            if paths:
                album_name = item["text"]
                self._add_files_to_foobar(paths, f"Альбом: {album_name}")

    def _add_files_to_foobar(self, file_paths, display_name):
        try:
            # /add добавляет файлы в текущий плейлист без немедленного воспроизведения
            command = [self.foobar_path, "/add"] + list(file_paths)

            subprocess.Popen(command)
            self.current_track_label.config(text=f"Добавлено в плейлист foobar2000: {display_name}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить в foobar2000: {e}")

    def delete_item(self):
        selected = self.tree.focus()
        if not selected:
            return

        item = self.tree.item(selected)
        confirm = messagebox.askyesno("Подтверждение", f"Удалить '{item['text']}'?")

        if confirm:
            # Удаляем из структуры данных
            if item["values"][0] == "artist":
                del self.music_library[item["text"]]
            elif item["values"][0] == "album":
                parent = self.tree.parent(selected)
                artist_item = self.tree.item(parent)
                artist_name = artist_item["text"]
                album_text = item["text"]
                year, album_name = album_text.split(" - ", 1)
                year = int(year)
                del self.music_library[artist_name][year][album_name]

            # Удаляем из дерева
            self.tree.delete(selected)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicCollectionApp(root)
    root.mainloop()