class Person :
    def __init__(self, id, name, age) :
        self.id = id
        self.name = name
        self.age = age

    def say_hello(self) :
        print("Hello, my name is", self.name)
