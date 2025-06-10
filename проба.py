from tkinter import  *
from tkinter.ttk import Combobox
from tkinter import scrolledtext, messagebox

window = Tk()  # создаём главное окно
window.title("Моё первое окно")
window.geometry("1000x600")

def clicked_1():
    res_1 = "Привет1 {}".format(txt_1.get()) #  печатает то что в поле текстового ввода txt_1
    label_1.configure(text=res_1)

def clicked_2():
    res_2 = "Привет2 {}".format(combo_1.get()) #  печатает то что в выпадающем меню combo_1
    label_2.configure(text=res_2)



"""Создание простой надписи на общем фоне"""
label_1 = Label(window, text='Надпись 1', font=("Arial Bold", 16),  bg="black", fg="red") # Надпись 1 красная на черном
label_1.grid(column=0, row=0, pady=20) # Размещение колонка 0
label_2 = Label(window, text='Надпись 2', font=("Arial Bold", 20),  bg="black", fg="red") # Надпись 1 красная на черном
label_2.grid(column=1, row=1, pady=20)

"""Создание кнопки"""
btn_1 = Button(window, text="Кнопка 1", bg="red", fg="black", command=clicked_1) # Кнопка 1 черная на красном
btn_1.grid(column=2, row=0, pady=20) # Размещение колонка 2
btn_2 = Button(window, text="Кнопка 2", bg="green", fg="black", command=clicked_2) # Кнопка 1 черная на красном
btn_2.grid(column=2, row=1, pady=20) # Размещение колонка 2

"""Создание текстового поля с фокусировкой курсора на нем"""
txt_1 = Entry(window, width=50)  # текстовое поле txt_1 с помощью класса Tkinter Entry
txt_1.grid(column=1, row=0, pady=20, padx=10) # Размещение колонка 1
txt_1.focus() # Курсор сразу в поле ввода
txt_2 = Entry(window, width=10) #state='disabled')  # текстовое поле txt_2, текст вводить нельзя
txt_2.grid(column=3, row=0, pady=20, padx=10) # Размещение колонка 3

"""Выпадающее меню"""
combo_1 = Combobox(window)
combo_1['values'] = (1, 2, 3, 4, 5, "Текст в выпадающем меню")
combo_1.current(5)  # вариант показа в выпадающем меню по умолчанию
combo_1.grid(column=0, row=1, pady=20, padx=10)

""" Создание чекбокса"""
checkbox_1_state = BooleanVar()   #задайте проверку состояния чекбокса
checkbox_1_state.set(False)  # значение по умолчанию
checkbox_1 = Checkbutton(window, text='Галочка_1') # Создание чекбокса
checkbox_1.grid(column=0, row=2)


"""IntVar() - класс, который позволяет создавать объекты, хранящие целочисленные значения (тип int). 
Такие объекты используются для связи значений Python с виджетами, например, полем ввода, флажком или радиокнопкой"""
selected = IntVar()

radiobutton1 = Radiobutton(window, text='Первый', value=1, variable=selected) # radio кнопки (Radio Button)
radiobutton2 = Radiobutton(window, text='Второй', value=2, variable=selected)
radiobutton3 = Radiobutton(window, text='Третий', value=3, variable=selected)
radiobutton1.grid(column=0, row=3)
radiobutton2.grid(column=1, row=3)
radiobutton3.grid(column=2, row=3)

def clicked_radiobutton_1():
    lbl.configure(text=selected.get())

"""Получение значения Radio Button (Избранная Radio Button)"""
btn_1 = Button(window, text="Клик", command=clicked_radiobutton_1)
btn_1.grid(column=3, row=3)    # Избранная Radio Button, при нажатии на кнопку

lbl = Label(window, font=("Arial Bold", 28), bg="white", fg="red", height=1, width=2)
lbl.grid(column=0, row=4)      # В ЭТОМ ПОЛЕ ОТРАЗИТСЯ НОМЕР (value=) ЭТОЙ Radio Button

"""Добавление виджета ScrolledText (текстовая область)"""
txt_1 = scrolledtext.ScrolledText(window, width=50, height=10)
txt_1.grid(column=0, row=5)
txt_1.insert(INSERT,'Текстовое поле')

"""Создание всплывающего окна с сообщением по нажатию кнопки"""
def clicked_messagebox_info():
    messagebox.showinfo('Всплывающее окно', 'Текст в всплывшем окне')
btn_messagebox_info = Button(window, text='Клик для всплывающего окна', command=clicked_messagebox_info)
btn_messagebox_info.grid(column=3, row=6)


def clicked_messagebox_error(res):
    messagebox.showerror('error', 'Текст об ошибке')
btn_messagebox_showerror = Button(window, text='Клик для окна ошибки', command=clicked_messagebox_error)
btn_messagebox_showerror.grid(column=1, row=6)

# res = messagebox.askquestion('Заголовок', 'Текст')
# res = messagebox.askyesno('Заголовок', 'Текст')
# res = messagebox.askyesnocancel('Заголовок', 'Текст')
# res = messagebox.askokcancel('Заголовок', 'Текст')
# res = messagebox.askretrycancel('Заголовок', 'Текст')












# tree = ttk.Treeview(window, columns=("type", "name", "path", "size", "date"), show="headings")
#
#
# scrollbar = tk.Scrollbar(window, orient="vertical", command=tree.yview)




window.mainloop()
