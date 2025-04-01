import os
import csv

def get_relations() -> dict:
    """
    Reads the relations CSV file and returns a dictionary of relations.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'relations.csv')
    relations = {}
    
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            uuid_1 = row['uuid_1']
            name_1 = row['name_1']
            name_2 = row['name_2']
            uuid_2 = row['uuid_2']
            relation = row['relation']
            weight = row['weight']
            description = row['description']
            
            relations[uuid_1] = {
                'name_1': name_1,
                'name_2': name_2,
                'uuid_2': uuid_2,
                'relation': relation,
                'weight': weight,
                'description': description
            }
    
    return relations