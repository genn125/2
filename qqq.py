
import tkinter as tk

#Функции
def select_all():
    for check in [Check1, Check2, Check3, Check4, Check5, Check6,Check7, Check8, Check9, Check10, Check11, Check12, Check13, Check14]:
        check.select()

def deselect_all():
    for check in [Check1, Check2, Check3, Check4, Check5, Check6,Check7, Check8, Check9, Check10, Check11, Check12, Check13, Check14]:
        check.deselect()

#Окно
win = tk.Tk()
win.geometry('440x750')
win.title("Списочек")
win['bg'] = '#B0E0E6'
# win.iconbitmap('C:/Users/user/Desktop/icon.ico')
win.resizable(0, 0)
win.attributes("-topmost",True)
#Переменные

#Код
Text2 = tk.Label(text = 'Список!', bg = '#B0E0E6', fg = '#800000', font = ('Arial', 32, 'bold')).grid(row = 0, column = 0, padx = 125, pady = 15)
Check1 = tk.Checkbutton(win, text = "Рашгард", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check2 = tk.Checkbutton(win, text = "Перчатки", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check3 = tk.Checkbutton(win, text = "Майки 3 - 5 шт.", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check4 = tk.Checkbutton(win, text = "Трусы, носки 3 - 5 шт.", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check5 = tk.Checkbutton(win, text = "Мыльно-рыльные принадлежности", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check6 = tk.Checkbutton(win, text = "Документы", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check7 = tk.Checkbutton(win, text = "Шорты 3 шт.", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check8 = tk.Checkbutton(win, text = "Кредитная карта", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check9 = tk.Checkbutton(win, text = "Наушники", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check10 = tk.Checkbutton(win, text = "Зарядка", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check11 = tk.Checkbutton(win, text = "Рюкзак + сумка", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check12 = tk.Checkbutton(win, text = "Покушать", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check13 = tk.Checkbutton(win, text = "Попить", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Check14 = tk.Checkbutton(win, text = "Любую книжечку", bg = '#B0E0E6', font = ('Arial', 15), padx = 20)
Fake1 = tk.Label(win, text = " ", bg = '#B0E0E6')
Select = tk.Button(win, text = "Выбрать все", font = ('Arial', 15, 'bold'), command = select_all, padx = 30, pady = 10)
Fake = tk.Label(win, text = " ", bg = '#B0E0E6')
Deselect = tk.Button(win, text = "Убрать все", font = ('Arial', 15, 'bold'), command = deselect_all, padx = 30, pady = 10)

#Вывод
Check1.grid(row = 2, column = 0, sticky = 'W')
Check2.grid(row = 3, column = 0, sticky = 'W')
Check3.grid(row = 4, column = 0, sticky = 'W')
Check4.grid(row = 6, column = 0, sticky = 'W')
Check5.grid(row = 7, column = 0, sticky = 'W')
Check6.grid(row = 8, column = 0, sticky = 'W')
Check7.grid(row = 9, column = 0, sticky = 'W')
Check8.grid(row = 11, column = 0, sticky = 'W')
Check9.grid(row = 12, column = 0, sticky = 'W')
Check10.grid(row = 13, column = 0, sticky = 'W')
Check11.grid(row = 14, column = 0, sticky = 'W')
Check12.grid(row = 15, column = 0, sticky = 'W')
Check13.grid(row = 16, column = 0, sticky = 'W')
Check14.grid(row = 17, column = 0, sticky = 'W')

Fake1.grid(row = 18, column = 0)
Select.grid(row = 19, column = 0)
Fake.grid(row = 20, column = 0)
Deselect.grid(row = 21, column = 0)

win.mainloop()