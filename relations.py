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
            id_1 = row['id_1']
            name_1 = row['name_1']
            name_2 = row['name_2']
            id_2 = row['id_2']
            relation = row['relation']
            weight = row['weight']
            description = row['description']
            
            relations[id_1] = {
                'name_1': name_1,
                'name_2': name_2,
                'id_2': id_2,
                'relation': relation,
                'weight': weight,
                'description': description
            }
    
    return relations