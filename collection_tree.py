import tkinter.ttk as ttk


class CollectionTree(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_style()

    def _setup_style(self):
        self.tag_configure("folder", background="#f0f0f0")
        self.tag_configure("file", background="white")

    def update_tree(self, data):
        """Обновление дерева на основе данных"""
        self.delete(*self.get_children())
        self._build_tree("", data)

    def _build_tree(self, parent, node):
        """Рекурсивное построение дерева"""
        for name, content in node.items():
            if name == "_files":
                for file_name, path in content:
                    self.insert(parent, "end", text=file_name, values=("file", path))
            else:
                item = self.insert(parent, "end", text=name, values=("folder", ""))
                self._build_tree(item, content)