import os
import subprocess
from tkinter import messagebox


class PlayerController:
    def __init__(self):
        self.foobar_path = r"C:\Program Files (x86)\foobar2000\foobar2000.exe"
        self.supported_formats = ('.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.wma')
        self._verify_foobar_path()

    def _verify_foobar_path(self):
        """Проверяет наличие Foobar2000 по указанному пути."""
        if not os.path.exists(self.foobar_path):
            messagebox.showerror(
                "Ошибка",
                f"Foobar2000 не найден по пути:\n{self.foobar_path}\n"
                "Проверьте установку программы."
            )
            return False
        return True

    def _normalize_path(self, raw_path):
        """Нормализует путь и проверяет его существование."""
        try:
            path = raw_path.replace('/', '\\').strip('"').strip()
            if os.path.isabs(path):
                return path if os.path.exists(path) else None

            search_paths = [
                os.path.dirname(os.path.abspath(__file__)),
                os.path.expanduser('~'),
                'D:\\', 'C:\\',
            ]
            for base in search_paths:
                full_path = os.path.abspath(os.path.join(base, path))
                if os.path.exists(full_path):
                    return full_path
            return None
        except Exception as e:
            print(f"Ошибка обработки пути {raw_path}: {str(e)}")
            return None

    def play_selected(self, tree):
        """Воспроизводит выбранные файлы/папки."""
        if not self._verify_foobar_path():
            return False, "Foobar2000 не доступен"

        selected_items = tree.selection()
        if not selected_items:
            return False, "Не выбраны элементы"

        paths = []
        names = []
        for item in selected_items:
            item_data = tree.item(item)
            if item_data["values"][0] == "file":
                normalized_path = self._normalize_path(item_data["values"][2])
                if normalized_path:
                    paths.append(normalized_path)
                    names.append(item_data["text"])
            elif item_data["values"][0] == "folder":
                self._collect_files_from_folder(tree, item, paths, names)

        if not paths:
            return False, "Нет доступных файлов для воспроизведения"
        return self._play_in_foobar(paths, " | ".join(names[:3]))

    def _collect_files_from_folder(self, tree, folder_item, paths, names):
        """Рекурсивно собирает аудиофайлы из папки."""
        for child in tree.get_children(folder_item):
            child_data = tree.item(child)
            if child_data["values"][0] == "file":
                normalized_path = self._normalize_path(child_data["values"][2])
                if normalized_path and normalized_path.lower().endswith(self.supported_formats):
                    paths.append(normalized_path)
                    names.append(child_data["text"])
            elif child_data["values"][0] == "folder":
                self._collect_files_from_folder(tree, child, paths, names)

    def _play_in_foobar(self, file_paths, display_name):
        """Запускает воспроизведение в Foobar2000."""
        try:
            subprocess.Popen([self.foobar_path, "/play"] + file_paths, shell=False)
            return True, f"Воспроизведение: {display_name}"
        except Exception as e:
            error_msg = (
                f"Ошибка запуска foobar2000:\n{str(e)}\n\n"
                f"Проверьте пути:\n" + "\n".join(f"- {p}" for p in file_paths)
            )
            messagebox.showerror("Ошибка", error_msg)
            return False, str(e)

    def add_to_playlist(self, tree=None, paths=None):
        """
        Добавляет файлы в плейлист.
        Поддерживает:
        - Выбор из TreeView (если передан tree)
        - Готовый список путей (для drag-and-drop)
        """
        if not self._verify_foobar_path():
            return False, "Foobar2000 не доступен"

        if paths is None:  # Обработка выбора из интерфейса
            selected_items = tree.selection()
            if not selected_items:
                return False, "Не выбраны элементы"

            paths = []
            for item in selected_items:
                item_data = tree.item(item)
                if item_data["values"][0] == "file":
                    normalized_path = self._normalize_path(item_data["values"][2])
                    if normalized_path and normalized_path.lower().endswith(self.supported_formats):
                        paths.append(normalized_path)
                elif item_data["values"][0] == "folder":
                    self._collect_files_from_folder(tree, item, paths, [])

        if not paths:
            return False, "Нет доступных файлов для добавления"

        try:
            subprocess.Popen([self.foobar_path, "/add"] + paths, shell=False)
            return True, f"Добавлено {len(paths)} треков в плейлист"
        except Exception as e:
            error_msg = (
                f"Ошибка добавления в плейлист:\n{str(e)}\n\n"
                f"Проверьте пути:\n" + "\n".join(f"- {p}" for p in paths)
            )
            messagebox.showerror("Ошибка", error_msg)
            return False, str(e)

    def handle_drop(self, event):
        """Обрабатывает перетаскивание файлов/папок в интерфейс."""
        paths = []
        for item in event.widget.tk.splitlist(event.data):
            path = item.strip('{}').strip('"')
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(self.supported_formats):
                            paths.append(os.path.join(root, file))
            elif os.path.isfile(path) and path.lower().endswith(self.supported_formats):
                paths.append(path)

        if paths:
            return self.add_to_playlist(paths=paths)
        return False, "Не найдено поддерживаемых аудиофайлов"

    def stop_foobar(self):
        """Останавливает воспроизведение."""
        if not self._verify_foobar_path():
            return False, "Foobar2000 не доступен"

        try:
            subprocess.Popen([self.foobar_path, "/stop"])
            return True, "Воспроизведение остановлено"
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить foobar2000:\n{str(e)}")
            return False, str(e)