import subprocess
from pathlib import Path


class FoobarController:
    def __init__(self, foobar_path=None):
        """
        Инициализация контроллера foobar2000.

        :param foobar_path: Путь к foobar2000.exe (автопоиск, если None)
        """
        self.foobar_path = self._find_foobar_path() if foobar_path is None else foobar_path

    def _find_foobar_path(self):
        """Пытается автоматически найти foobar2000 в стандартных путях"""
        default_paths = [
            r"C:\Program Files\foobar2000\foobar2000.exe",
            r"C:\Program Files (x86)\foobar2000\foobar2000.exe",
            str(Path.home() / "AppData" / "Local" / "foobar2000" / "foobar2000.exe")
        ]

        for path in default_paths:
            if Path(path).exists():
                return path
        raise FileNotFoundError("Foobar2000 не найден. Укажите путь вручную.")

    def play_files(self, file_paths):
        """
        Воспроизведение файлов.

        :param file_paths: Список путей к файлам
        """
        self._send_command("/play", file_paths)

    def add_to_playlist(self, file_paths):
        """
        Добавление файлов в плейлист.

        :param file_paths: Список путей к файлам
        """
        self._send_command("/add", file_paths)

    def stop_playback(self):
        """Остановка воспроизведения"""
        self._send_command("/stop")

    def _send_command(self, command, file_paths=None):
        """
        Отправка команды в foobar2000.

        :param command: Команда (/play, /add, /stop)
        :param file_paths: Опциональные пути к файлам
        """
        if not self.foobar_path:
            raise ValueError("Путь к foobar2000 не указан")

        args = [self.foobar_path, command]
        if file_paths:
            args.extend(file_paths)

        try:
            subprocess.Popen(args)
        except Exception as e:
            raise RuntimeError(f"Ошибка при отправке команды в foobar2000: {str(e)}")