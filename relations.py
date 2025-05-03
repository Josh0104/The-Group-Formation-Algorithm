import os
from person import Person
import csv


def get_relations(people: dict[str, Person], path) -> list:
    """
    Reads the relations CSV file and returns a dictionary of relations.
    """
    if path is None or path == "" :
        path = 'relations.csv'
        
    file_path = os.path.join(os.path.dirname(__file__), 'data/', path)
    relations = {}
    
    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for i, row in enumerate(reader, start=0):  # start=0 to match line numbers
            uuid_1 = row['uuid_1']
            name_1 = row['name_1']
            name_2 = row['name_2']
            uuid_2 = row['uuid_2']
            relation = row['relation']
            weight = row['weight']
            description = row['description']
            
            id_1 = people[uuid_1].id
            id_2 = people[uuid_2].id
            
            relations.append({
                'id': i,
                'uuid_1': uuid_1,
                'name_1': name_1,
                'name_2': name_2,
                'uuid_2': uuid_2,
                'relation': relation,
                'weight': weight,
                'description': description,
                'id_1': id_1,
                'id_2': id_2
            })
    
    return relations