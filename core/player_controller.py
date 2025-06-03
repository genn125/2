import os
import subprocess
from tkinter import messagebox

class PlayerController:
    def __init__(self):
        self.foobar_path = r"C:\Program Files (x86)\foobar2000\foobar2000.exe"

    def play_selected(self, tree):
        selected_items = tree.selection()
        if not selected_items:
            return
        paths = []
        names = []
        for item in selected_items:
            item_data = tree.item(item)
            if item_data["values"][0] == "file":
                paths.append(item_data["values"][1])
                names.append(item_data["text"])
            elif item_data["values"][0] == "folder":
                self._collect_files_from_folder(tree, item, paths, names)
        if paths:
            self._play_in_foobar(paths, " | ".join(names))

    def _collect_files_from_folder(self, tree, folder_item, paths, names):
        for child in tree.get_children(folder_item):
            child_data = tree.item(child)
            if child_data["values"][0] == "file":
                paths.append(child_data["values"][1])
                names.append(child_data["text"])
            elif child_data["values"][0] == "folder":
                self._collect_files_from_folder(tree, child, paths, names)

    def _play_in_foobar(self, file_paths, display_name):
        try:
            subprocess.Popen([self.foobar_path, "/play"] + file_paths)
            return True, f"Воспроизведение: {display_name[:50]}..."
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить foobar2000:\n{str(e)}")
            return False, str(e)

    def add_to_playlist(self, tree):
        selected_items = tree.selection()
        if not selected_items:
            return
        paths = []
        for item in selected_items:
            item_data = tree.item(item)
            if item_data["values"][0] == "file":
                paths.append(item_data["values"][1])
            elif item_data["values"][0] == "folder":
                self._collect_files_from_folder(tree, item, paths, [])
        if paths:
            try:
                subprocess.Popen([self.foobar_path, "/add"] + paths)
                return True, f"Добавлено {len(paths)} треков в плейлист"
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить в плейлист:\n{str(e)}")
                return False, str(e)

    def stop_foobar(self):
        try:
            subprocess.Popen([self.foobar_path, "/stop"])
            return True, "Воспроизведение остановлено"
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить foobar2000:\n{str(e)}")
            return False, str(e)