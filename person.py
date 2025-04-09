from datetime import date, datetime
from enum import Enum

class Person :
    def __init__(self, id, uuid, first_name, last_name, birthday, gender, country, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10):
        self.id = id
        self.uuid = uuid
        self.first_name = first_name
        self.last_name = last_name
        self.name = first_name + " " + last_name
        self.birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
        self.gender = Gender.MALE if gender == "Male" else Gender.FEMALE
        self.country = country
        self.a1 = a1.lower() if a1 else ""
        self.a2 = a2.lower() if a2 else ""
        self.a3 = a3.lower() if a3 else ""
        self.a4 = a4.lower() if a4 else ""
        self.a5 = a5.lower() if a5 else ""
        self.a6 = a6.lower() if a6 else ""
        self.a7 = a7.lower() if a7 else ""
        self.a8 = a8.lower() if a8 else ""
        self.a9 = a9
        self.a10 = a10
        self.team = None


    def get_age(self) -> int:
        today = date(2025, 5, 28) # Date of the current camp, change if needed
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.get_age()})"

    def __repr__(self):
        return f"Person(id={self.id}, name='{self.first_name} {self.last_name}', birthday='{self.birthday}')"
    def set_team(self, team):
        self.team = team

class Gender(Enum):
    MALE = 1
    FEMALE = 2

class SurveyResponse(Enum):
    YES = 1
    NO = 2
    MAYBE = 3

class Relation:
    def __init__(self, id, uuid_1, name_1, name_2, uuid_2, relation, weight, description):
        self.id = id
        self.uuid_1 = uuid_1
        self.name_1 = name_1
        self.name_2 = name_2
        self.uuid_2 = uuid_2
        self.relation = relation
        self.weight = weight
        self.description = description

    def __str__(self) -> str:
        return f"{self.name_1} - {self.name_2} ({self.relation})"