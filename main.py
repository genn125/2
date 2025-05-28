
from file_manager import FileManager
from foobar_controller import FoobarController
from collection_tree import CollectionTree
from config import Config
from logger import AppLogger


class MusicCollectionApp:
    def __init__(self, root):
        self.config = Config().load()
        self.logger = AppLogger()
        self.file_manager = FileManager(('.mp3', '.wav'))
        self.foobar = FoobarController(self.config['foobar_path'])

        # Инициализация интерфейса
        self.tree = CollectionTree(root)
        self._setup_ui()

    def scan_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.music_library = self.file_manager.scan_folder(folder)
            self.tree.update_tree(self.music_library)
            self.logger.log(f"Отсканирована папка: {folder}")