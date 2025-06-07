import tkinter as tk
from core.music_library import MusicLibrary
from core.ui import MusicCollectionUI
from core.player_controller import PlayerController


class MusicCollectionApp:
    def __init__(self, root):
        self.root = root
        self.library = MusicLibrary()
        self.player = PlayerController()
        self.ui = MusicCollectionUI(root, self.library, self.player)



if __name__ == "__main__":
    root = tk.Tk()
    app = MusicCollectionApp(root)
    root.mainloop()