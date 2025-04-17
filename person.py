
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
        self.a2 = AnswerOption.from_str(a2) if a2 else None
        self.a3 = AnswerOption.from_str(a3) if a3 else None
        self.a4 = AnswerOption.from_str(a4) if a4 else None
        self.a5 = AnswerOption.from_str(a5) if a5 else None
        self.a6 = AnswerOption.from_str(a6) if a6 else None
        self.a7 = AnswerOption.from_str(a7) if a7 else None
        self.a8 = AnswerOption.from_str(a8) if a8 else None
        self.a9 = a9
        self.a10 = a10
        self.team = None
        self.age = self.get_age()

    def get_age(self) -> int:
        today = date(2025, 5, 28) # Date of the current camp, change if needed
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.get_age()})"

    def __repr__(self):
        return f"Person(id={self.id}, name='{self.first_name} {self.last_name}', birthday='{self.birthday}')"
    def set_team(self, team):
        self.team = team
    
    def to_dict(self) -> dict: # convert Person → dict
        return {
            'id': self.id,
            'uuid': self.uuid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birthday': self.birthday.isoformat(),  # datetime to string
            'gender': self.gender.name,             # Enum to string
            'country': self.country,
            'a1': self.a1,
            'a2': self.a2.name if self.a2 else None,
            'a3': self.a3.name if self.a3 else None,
            'a4': self.a4.name if self.a4 else None,
            'a5': self.a5.name if self.a5 else None,
            'a6': self.a6.name if self.a6 else None,
            'a7': self.a7.name if self.a7 else None,
            'a8': self.a8.name if self.a8 else None,
            'a9': self.a9,
            'a10': self.a10,
            'team': self.team
        }
    
    @staticmethod
    def from_dict(data) -> 'Person': # convert dict → Person
        return Person(
            id=data['id'],
            uuid=data['uuid'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            birthday=data['birthday'],
            gender=data['gender'],
            country=data['country'],
            a1=data['a1'],
            a2=data['a2'],
            a3=data['a3'],
            a4=data['a4'],
            a5=data['a5'],
            a6=data['a6'],
            a7=data['a7'],
            a8=data['a8'],
            a9=data['a9'],
            a10=data['a10'],
        )

class Gender(Enum):
    MALE = 1
    FEMALE = 2

#Enum valuebased on points
class AnswerOption(Enum):
    NO = 0
    MAYBE = 1
    YES = 3
    
    @staticmethod
    def from_str(value: str) -> 'AnswerOption':
        if value.lower() == "yes":
            return AnswerOption.YES
        elif value.lower() == "maybe":
            return AnswerOption.MAYBE
        else:
            return AnswerOption.NO
        
    def __str__(self) -> str: 
        if self == AnswerOption.YES:
            return "Yes"
        elif self == AnswerOption.MAYBE:
            return "Maybe"
        else:
            return "No"
    

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