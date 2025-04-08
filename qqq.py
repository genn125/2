class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} says woof!"

    def dog_years(self):
        return self.age * 7

my_dog = Dog("Buddy", 3)
print("моё имя:",my_dog.name,"мне", my_dog.dog_years())
print(my_dog.bark())