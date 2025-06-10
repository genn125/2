from tkinter import  *
from tkinter.ttk import Combobox


def clicked_1():
    res_1 = "Привет1 {}".format(txt_1.get()) #  печатает то что в поле текстового ввода txt_1
    label_1.configure(text=res_1)


def clicked_2():
    res_2 = "Привет2 {}".format(combo_1.get()) #  печатает то что в выпадающем меню combo_1
    label_2.configure(text=res_2)

window = Tk()  # создаём главное окно
window.title("Моё первое окно")
window.geometry("800x600")

label_1 = Label(window, text='Надпись 1', font=("Arial Bold", 16),  bg="black", fg="red") # Надпись 1 красная на черном
label_1.grid(column=0, row=0, pady=20) # Размещение колонка 0
label_2 = Label(window, text='Надпись 2', font=("Arial Bold", 16),  bg="black", fg="red") # Надпись 1 красная на черном
label_2.grid(column=1, row=1, pady=20)


btn_1 = Button(window, text="Кнопка 1", bg="red", fg="black", command=clicked_1) # Кнопка 1 черная на красном
btn_1.grid(column=2, row=0, pady=20) # Размещение колонка 2
btn_2 = Button(window, text="Кнопка 2", bg="green", fg="black", command=clicked_2) # Кнопка 1 черная на красном
btn_2.grid(column=2, row=1, pady=20) # Размещение колонка 2

txt_1 = Entry(window, width=50)  # текстовое поле txt_1 с помощью класса Tkinter Entry
txt_1.grid(column=1, row=0, pady=20, padx=10) # Размещение колонка 1
txt_1.focus() # Курсор сразу в поле ввода
txt_2 = Entry(window, width=10) #state='disabled')  # текстовое поле txt_2, текст вводить нельзя
txt_2.grid(column=3, row=0, pady=20, padx=10) # Размещение колонка 3

combo_1 = Combobox(window)
combo_1['values'] = (1, 2, 3, 4, 5, "Текст в выпадающем меню")
combo_1.current(5)  # вариант показа в выпадающем меню по умолчанию
combo_1.grid(column=0, row=1, pady=20, padx=10)
# tree = ttk.Treeview(window, columns=("type", "name", "path", "size", "date"), show="headings")
#
#
# scrollbar = tk.Scrollbar(window, orient="vertical", command=tree.yview)




window.mainloop()
