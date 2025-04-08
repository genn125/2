class Goat:
    age = 0  # классовый атрибут


    def pet (self):
        print('Коза говорит: Meeeeee')
    pet()
b = Goat()
a = Goat()
a.age = 5 # Экземплярный атрибут

print('Возраст козы:', b.age, "лет")

