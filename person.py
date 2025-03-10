from datetime import date
from enum import Enum

class Person :
    def __init__(self, id, name, birthday, gender, country, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10):
        self.id = id
        self.name = name
        self.birthday = birthday
        self.gender = gender
        self.country = country
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.a5 = a5
        self.a6 = a6
        self.a7 = a7
        self.a8 = a8
        self.a9 = a9
        self.a10 = a10

    def say_hello(self) :
        print("Hello, my name is", self.name)

    def calculate_age(self):
        today = date(2025, 5, 28)
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

class Gender(Enum):
    MALE = 1
    FEMALE = 2

class SurveyResponse(Enum):
    YES = 1
    NO = 2
    MAYBE = 3
