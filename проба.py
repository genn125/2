import tkinter as tk
from tkinter import ttk, Menu, messagebox, filedialog
import os


window = tk.Tk()  # создаём главное окно
window.title("Моё первое окно")
window.geometry("300x200")
label = tk.Label(window, text="Привет, экран!")
label.pack()  # размещаем элемент в окне





window.mainloop()
