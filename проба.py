import tkinter as tk
from tkinter import  *
import os

def clicked():
    res = "Привет {}".format(txt_1.get())
    label.configure(text=res)

window = Tk()  # создаём главное окно
window.title("Моё первое окно")
window.geometry("600x600")

label = Label(window, text='Надпись 1', font=("Arial Bold", 16),  bg="black", fg="red") # Надпись 1 красная на черном
label.grid(column=0, row=0) # Размещение колонка 0

btn_1 = Button(window, text="Не нажимать!", bg="red", fg="black", command=clicked) # Кнопка 1 черная на красном
btn_1.grid(column=2, row=0) # Размещение колонка 2

txt_1 = Entry(window,width=10)  # текстовое поле txt_1 с помощью класса Tkinter Entry
txt_1.grid(column=1, row=0) # Размещение колонка 1
txt_1.focus() # Курсор сразу в поле ввода
txt_2 = Entry(window,width=10)  # текстовое поле txt_2
txt_2.grid(column=3, row=0) # Размещение колонка 3


# label.pack(side=tk.LEFT, fill=tk.X)  # размещаем элемент в окне
# tree = ttk.Treeview(window, columns=("type", "name", "path", "size", "date"), show="headings")
#
#
# scrollbar = tk.Scrollbar(window, orient="vertical", command=tree.yview)




window.mainloop()
